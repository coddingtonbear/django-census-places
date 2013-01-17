# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PlaceBoundary'
        db.create_table('census_places_placeboundary', (
            ('geo_id', self.gf('django.db.models.fields.CharField')(max_length=60, primary_key=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, db_index=True)),
            ('place', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=90)),
            ('lsad', self.gf('django.db.models.fields.CharField')(max_length=7, null=True, blank=True)),
            ('censusarea', self.gf('django.db.models.fields.FloatField')()),
            ('geog', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(spatial_index=False, geography=True)),
        ))
        db.send_create_signal('census_places', ['PlaceBoundary'])


    def backwards(self, orm):
        # Deleting model 'PlaceBoundary'
        db.delete_table('census_places_placeboundary')


    models = {
        'census_places.placeboundary': {
            'Meta': {'ordering': "['name']", 'object_name': 'PlaceBoundary'},
            'censusarea': ('django.db.models.fields.FloatField', [], {}),
            'geo_id': ('django.db.models.fields.CharField', [], {'max_length': '60', 'primary_key': 'True'}),
            'geog': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'spatial_index': 'False', 'geography': 'True'}),
            'lsad': ('django.db.models.fields.CharField', [], {'max_length': '7', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            'place': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_index': 'True'})
        }
    }

    complete_apps = ['census_places']