from __future__ import with_statement

import codecs
import logging
import os.path
import subprocess
import tempfile
import urllib2
import zipfile

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from census_places.enums import STATES

SHP2PGSQL = getattr(settings, 'SHP2PGSQL_PATH', 'shp2pgsql')

logger = logging.getLogger('census_places.management.commands.import_paces')
logging.basicConfig(level=logging.DEBUG)

class Command(BaseCommand):
    args = '<\'State/Province Name\'|FIPS Code|\'all\'>' 
    help = 'Imports start and end e-mail messages sent by Runmeter (http://www.abvio.com/runmeter/) '\
            + 'delivered to a mailbox watched by django_mailbox, creating location points for the '\
            + 'username specified.'

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
        for fips_code in STATES:
            self.import_single_state(fips_code)

    def import_single_state(self, arg):
        url = self._get_url_from_args(arg)
        logger.info("Importing \"%s\" from %s" % (arg, url))
        shapefile_path = self._get_temporary_shapefile_path_from_url(url)
        sql = self._get_sql_from_shapefile(shapefile_path)
        self._import_from_sql(sql)
        os.remove(shapefile_path)

    def _import_from_sql(self, sql):
        cursor = connection.cursor()
        cursor.execute(sql)

    def _get_sql_from_shapefile(self, shapefile):
        shapefile_extraction_args = (
            SHP2PGSQL,
            '-a', # Append to existing tables (tables are created by syncdb)
            '-G', # Use geography types rather than geometry
            '-W', 'UTF-8', # Specify that incoming data is UTF-8
            shapefile,
            'census_places_placeboundary'
            )

        logger.debug(shapefile_extraction_args)
        process = subprocess.Popen(
                shapefile_extraction_args,
                stdout=subprocess.PIPE
                )
        sql, stderr = process.communicate()
        return sql

    def _get_temporary_shapefile_path_from_url(self, url):
        temporary_directory = tempfile.mkdtemp()
        with tempfile.TemporaryFile() as temporary_file:
            zip_file_stream = urllib2.urlopen(url)
            temporary_file.write(
                    zip_file_stream.read()
                    )
            zip_file_stream.close()
            archive = zipfile.ZipFile(temporary_file, 'r')
            archive.extractall(temporary_directory)

        shapefile_path = None
        for path in os.listdir(temporary_directory):
            basename, extension = os.path.splitext(path)
            if extension == '.shp':
                shapefile_path = os.path.join(
                        temporary_directory,
                        path
                        )

        if not shapefile_path:
            raise CommandError("No shapefile was found in the data extracted!")

        return shapefile_path

    def _get_fips_code_by_state_abbreviation(self, state_arg):
        for fips_code, state in STATES:
            if state.lower() == state_arg.lower():
                return fips_code
        return None

    def _get_url_from_args(self, arg):
        try:
            fips_code = int(arg)
        except ValueError:
            fips_code = self._get_fips_code_by_state_abbreviation(arg)
            if not fips_code:
                raise CommandError(
                        "The state name you specified \"%s\" was not found." % arg
                        )
        return self.URL_PATTERN % {'fips_code': fips_code}
