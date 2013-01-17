import logging

from django.contrib.gis.db import models

from census_places.enums import STATES

logger = logging.getLogger('census_places.models')

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
    lsad = models.CharField(
        null=True,
        blank=True,
        max_length=7
    )
    
    censusarea = models.FloatField(
        verbose_name='census area')
    
    geog = models.MultiPolygonField(
        geography=True,
        spatial_index=False#True # Breaks MySQL with InnoDB.
    )

    objects = models.GeoManager()

    @classmethod
    def get_containing(cls, point):
        boundary = cls.objects.get(
            geog__covers=point
        )
        logger.debug("Found geometry %s covering %s" % (
                boundary,
                point,
            )
        )
        return boundary

    @classmethod
    def get_nearest_to(cls, point, stack_depth_maximum=5, stack_depth=1, buffer_size=0.2):
        buffered_point = point.buffer(buffer_size)
        cities = cls.objects.filter(geog__bboverlaps=buffered_point)\
                .distance(point)\
                .order_by('distance')
        if cities.count() > 0:
            city = cities[0]
            logger.debug("Found geometry %s covering %s" % (
                    city,
                    point,
                    )
                )
            return city
        else:
            buffer_size = buffer_size * 2
            stack_depth = stack_depth + 1
            if stack_depth <= stack_depth_maximum:
                logger.debug("Recursively calling with buffer: %s (stack depth: %s)" % (
                        buffer_size,
                        stack_depth
                        )
                    )
                return cls.get_nearest_to(point, stack_depth_maximum, stack_depth, buffer_size)
            else:
                logger.debug(
                        "No geometry found; stack depth maximum encountered "
                        "at buffer of size %s" % buffer
                        )
                raise cls.DoesNotExist(
                        "No cities were found within the range you specified; "
                        "try increasing your initial buffer_size from %s or "
                        "your stack_depth_maximum from %s." % (
                            buffer_size,
                            stack_depth_maximum
                            )
                        )

    def __unicode__(self):
        return "%s, %s" % (self.name, self.get_state_display())

    class Meta:
        ordering = ['name', ]
        verbose_name_plural = "Place Boundaries"
        verbose_name = "Place Boundary"
#        app_label = 'census places'
#        db_table = 'census_places_placeboundary'

class ZIPBoundary(models.Model):
    
    geo_id = models.CharField(
        primary_key=True,
        max_length=60)
    
    state = models.CharField(
        max_length=2,
        db_index=True,
        choices=STATES)
    
    zip_code = models.CharField(
        max_length=10,
        unique=True,
        db_index=True)
    
    classfp10 = models.CharField(
        max_length=10,
        db_index=True)
    
    mtfcc10 = models.CharField(
        max_length=10,
        db_index=True)
    
    funcstat10 = models.CharField(
        max_length=10,
        db_index=True)
    
    aland10 = models.PositiveIntegerField(
        verbose_name='land area')
    
    awater10 = models.PositiveIntegerField(
        verbose_name='water area')
    
    lat = models.DecimalField(
        max_digits=15,
        decimal_places=10,
        verbose_name='latitude')
    
    lng = models.DecimalField(
        max_digits=15,
        decimal_places=10,
        verbose_name='longitude')
    
    partflg10 = models.CharField(
        max_length=10,
        db_index=True)
    
    geog = models.MultiPolygonField(
        geography=True,
        spatial_index=False#True # Breaks MySQL with InnoDB.
        )

    objects = models.GeoManager()

    def __unicode__(self):
        return "%s" % (self.zip_code,)

    class Meta:
        ordering = ['zip_code', ]
        verbose_name_plural = "ZIP Boundaries"
        verbose_name = "ZIP Boundary"
#        app_label = 'census places'
#        db_table = 'census_places_zipboundary'
        