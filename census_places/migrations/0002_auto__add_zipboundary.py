# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ZIPBoundary'
        db.create_table('census_places_zipboundary', (
            ('geo_id', self.gf('django.db.models.fields.CharField')(max_length=60, primary_key=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, db_index=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10, db_index=True)),
            ('classfp10', self.gf('django.db.models.fields.CharField')(max_length=10, db_index=True)),
            ('mtfcc10', self.gf('django.db.models.fields.CharField')(max_length=10, db_index=True)),
            ('funcstat10', self.gf('django.db.models.fields.CharField')(max_length=10, db_index=True)),
            ('aland10', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('awater10', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('lat', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=10)),
            ('lng', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=10)),
            ('partflg10', self.gf('django.db.models.fields.CharField')(max_length=10, db_index=True)),
            ('geog', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(spatial_index=False, geography=True)),
        ))
        db.send_create_signal('census_places', ['ZIPBoundary'])


    def backwards(self, orm):
        # Deleting model 'ZIPBoundary'
        db.delete_table('census_places_zipboundary')


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
        },
        'census_places.zipboundary': {
            'Meta': {'ordering': "['zip_code']", 'object_name': 'ZIPBoundary'},
            'aland10': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'awater10': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'classfp10': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            'funcstat10': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            'geo_id': ('django.db.models.fields.CharField', [], {'max_length': '60', 'primary_key': 'True'}),
            'geog': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'spatial_index': 'False', 'geography': 'True'}),
            'lat': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '10'}),
            'lng': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '10'}),
            'mtfcc10': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            'partflg10': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_index': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10', 'db_index': 'True'})
        }
    }

    complete_apps = ['census_places']