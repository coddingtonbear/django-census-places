from django.contrib.gis.db import models

from census_places.enums import STATES

class PlaceBoundary(models.Model):
    geo_id = models.CharField(
            primary_key=True,
            max_length=60
            )
    state = models.CharField(
            max_length=2,
            db_index=True,
            choices=STATES
            )
    place = models.CharField(max_length=5)
    name = models.CharField(max_length=90)
    lsad = models.CharField(max_length=7)
    censusarea = models.FloatField()
    geog = models.MultiPolygonField(
            geography=True,
            spatial_index=True
            )

    objects = models.GeoManager()

    def __unicode__(self):
        return "%s, %s" % (self.name, self.get_state_display())

    class Meta:
        ordering = ['name', ]
        verbose_name_plural = "Place Boundaries"
        verbose_name = "Place Boundary"
