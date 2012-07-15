from django.contrib.gis import admin

from census_places.models import PlaceBoundary

class PlaceBoundaryAdmin(admin.options.OSMGeoAdmin):
    search_fields = (
                'name', 
            )

admin.site.register(PlaceBoundary, PlaceBoundaryAdmin)
