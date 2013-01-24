from __future__ import with_statement

import logging
import os.path
import shutil
import tempfile
import urllib2
import zipfile

from django.contrib.gis.gdal import DataSource, OGRGeometry, OGRGeomType
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.utils import IntegrityError

from optparse import make_option

from census_places.enums import STATES
from census_places.models import PlaceBoundary, ZIPBoundary

STATE = 'state'
ZCTA = 'zcta'
FILE_TYPES = (STATE, ZCTA)

logger = logging.getLogger('census_places.management.commands.import_places')
logging.basicConfig(level=logging.INFO)

class Command(BaseCommand):
    args = '<\'State/Province Name\'|FIPS Code|\'all\'>' 
    help = 'Downloads and imports place boundaries supplied by the United States Census.'
    
    option_list = BaseCommand.option_list + (
        make_option('--dryrun', action='store_true', default=False),
        make_option('--verbose', action='store_true', default=False),
        make_option('--zips', action='store_true', default=False, help='If given, imports Zip Code Tabulation Areas for the given state.'),
    )

    URL_PATTERN =      "http://www2.census.gov/geo/tiger/GENZ2010/gz_2010_%(fips_code)s_160_00_500k.zip"
    URL_PATTERN_ZCTA = "http://www2.census.gov/geo/tiger/TIGER2010/ZCTA5/2010/tl_2010_%(fips_code)s_zcta510.zip"

    @transaction.commit_on_success
    def handle(self, *args, **options):
        self.dryrun = options['dryrun']
        self.verbose = options['verbose']
        self.zips = options['zips']
        try:
            arg = args[0]
        except IndexError:
            raise CommandError(
                "You must supply an argument of either a quoted state name, "
                "a one or two digit FIPS Code, or the word 'all'."
                )
        if arg == 'all':
            return self.import_all_states()
        else:
            return self.import_single_state(arg)

    def import_all_states(self):
        for fips_code, state_name in STATES:
            self.import_single_state(fips_code)

    def import_single_state(self, arg):
        url = self._get_url_from_arg(arg)
        logger.info("Downloading state data for \"%s\" from %s" % (arg, url))
        shapefile_dir = self._get_temporary_shapefile_dir_from_url(url)
        self._insert_from_shapefile(shapefile_dir, file_type=STATE)
        shutil.rmtree(shapefile_dir)
        
        if self.zips:
            url = self._get_url_from_arg(arg, file_type=ZCTA)
            logger.info("Downloading zip data for \"%s\" from %s" % (arg, url))
            shapefile_dir = self._get_temporary_shapefile_dir_from_url(url)
            self._insert_from_shapefile(shapefile_dir, file_type=ZCTA)
            shutil.rmtree(shapefile_dir)

    def _cleanup_temporary_directory(self, directory):
        shutil.rmtree(directory)

    def _get_multipolygon_geometry_from_row(self, row):
        if row.geom_type.django == 'PolygonField':
            geom = OGRGeometry(OGRGeomType('MultiPolygon'))
            geom.add(row.geom)
            return geom
        elif row.geom_type.django == 'MultiPolygonField':
            return geom

    def _insert_from_shapefile(self, shapefile_dir, file_type=STATE):
        assert file_type in FILE_TYPES
        shapefile_path = self._get_shapefile_path_from_directory(shapefile_dir)
        source = DataSource(shapefile_path)

        total = len(source[0])
        i = 0
        for row in source[0]:
            i += 1
            logger.info('%i of %i: %.0f%%' % (i, total, i/float(total)*100))
            geom = self._get_multipolygon_geometry_from_row(row)
            if not geom:
                logger.warning(
                        "Unable to convert row %s %s into MultiPolygon" % (
                            row.fid,
                            repr(row)
                            )
                        )
                continue
            
            if self.verbose:
                for field in row.fields:
                    logger.info('%s %s' % (field, row.get(field)))
                
            if file_type == STATE:
                key = dict(
                    geo_id = row.get('GEO_ID'),
                    state = row.get('STATE'),
                    place = row.get('PLACE'),
                    defaults = dict(
                        name = row.get('NAME').decode('latin1'),
                        lsad = row.get('LSAD'),
                        censusarea = row.get('CENSUSAREA'),
                        geog = geom.wkt,
                    )
                )
                obj, _ = PlaceBoundary.objects.get_or_create(**key)
                for k, d in key.iteritems():
                    if k == 'defaults':
                        continue
                    setattr(obj, k, d)
            else:
                key = dict(
                    state = row.get('STATEFP10'),
                    geo_id = row.get('GEOID10'),
                    zip_code = row.get('ZCTA5CE10'),
                    defaults = dict(
                        classfp10 = row.get('CLASSFP10'),
                        mtfcc10 = row.get('MTFCC10'),
                        funcstat10 = row.get('FUNCSTAT10'),
                        aland10 = row.get('ALAND10'),
                        awater10 = row.get('AWATER10'),
                        lat = row.get('INTPTLAT10'),
                        lng = row.get('INTPTLON10'),
                        partflg10 = row.get('PARTFLG10'),
                        geog = geom.wkt,
                    )
                )
                try:
                    obj, _ = ZIPBoundary.objects.get_or_create(**key)
                    for k, d in key.iteritems():
                        if k == 'defaults':
                            continue
                        setattr(obj, k, d)
                except IntegrityError, e:
                    pass

            if not self.dryrun:
                sid = transaction.savepoint()
                try:
                    obj.save()
                    transaction.savepoint_commit(sid)
                    logger.info(
                        "(%s) %s Imported Successfully" % (
                            row.fid,
                            obj,
                            )
                        )
                except IntegrityError:
                    transaction.savepoint_rollback(sid)
                    logger.warning(
                        "(%s) %s Already Exists" % (
                            row.fid,
                            obj,
                            )
                        )

    def _get_shapefile_path_from_directory(self, directory):
        shapefile_path = None
        for path in os.listdir(directory):
            basename, extension = os.path.splitext(path)
            if extension == '.shp':
                shapefile_path = os.path.join(
                        directory,
                        path
                        )

        if not shapefile_path:
            raise CommandError("No shapefile was found in the data extracted!")

        return shapefile_path

    def _get_temporary_shapefile_dir_from_url(self, url):
        temporary_directory = tempfile.mkdtemp()
        with tempfile.TemporaryFile() as temporary_file:
            zip_file_stream = urllib2.urlopen(url)
            temporary_file.write(
                    zip_file_stream.read()
                    )
            zip_file_stream.close()
            archive = zipfile.ZipFile(temporary_file, 'r')
            archive.extractall(temporary_directory)
        return temporary_directory

    def _get_fips_code_by_state_abbreviation(self, state_arg):
        for fips_code, state in STATES:
            if state.lower() == state_arg.lower():
                return fips_code
        return None

    def _get_url_from_arg(self, arg, file_type=STATE):
        assert file_type in FILE_TYPES
        try:
            fips_code = "%02d" % int(arg)
        except ValueError:
            fips_code = self._get_fips_code_by_state_abbreviation(arg)
            if not fips_code:
                raise CommandError(
                        "The state name you specified \"%s\" was not found." % arg
                        )
        if file_type == STATE:
            return self.URL_PATTERN % {'fips_code': fips_code}
        else:
            return self.URL_PATTERN_ZCTA % {'fips_code': fips_code}
