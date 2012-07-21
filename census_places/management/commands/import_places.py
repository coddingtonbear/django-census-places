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

from census_places.enums import STATES
from census_places.models import PlaceBoundary

logger = logging.getLogger('census_places.management.commands.import_places')
logging.basicConfig(level=logging.INFO)

class Command(BaseCommand):
    args = '<\'State/Province Name\'|FIPS Code|\'all\'>' 
    help = 'Downloads and imports place boundaries supplied by the United States Census.'

    URL_PATTERN = "http://www2.census.gov/geo/tiger/GENZ2010/gz_2010_%(fips_code)s_160_00_500k.zip"

    @transaction.commit_on_success
    def handle(self, *args, **options):
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
        logger.info("Downloading data for \"%s\" from %s" % (arg, url))
        shapefile_dir = self._get_temporary_shapefile_dir_from_url(url)
        self._insert_from_shapefile(shapefile_dir)
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

    def _insert_from_shapefile(self, shapefile_dir):
        shapefile_path = self._get_shapefile_path_from_directory(shapefile_dir)
        source = DataSource(shapefile_path)

        for row in source[0]:
            geom = self._get_multipolygon_geometry_from_row(row)
            if not geom:
                logger.warning(
                        "Unable to convert row %s %s into MultiPolygon" % (
                            row.fid,
                            repr(row)
                            )
                        )
                continue
            place = PlaceBoundary()
            place.geo_id = row.get('GEO_ID')
            place.state = row.get('STATE')
            place.place = row.get('PLACE')
            place.name = row.get('NAME').decode('latin1')
            place.lsad = row.get('LSAD')
            place.censusarea = row.get('CENSUSAREA')
            place.geog = geom.wkt
            place.save()
            logger.info(
                    "Imported (%s) %s" % (
                        row.fid,
                        place.name,
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

    def _get_url_from_arg(self, arg):
        try:
            fips_code = "%02d" % int(arg)
        except ValueError:
            fips_code = self._get_fips_code_by_state_abbreviation(arg)
            if not fips_code:
                raise CommandError(
                        "The state name you specified \"%s\" was not found." % arg
                        )
        return self.URL_PATTERN % {'fips_code': fips_code}
