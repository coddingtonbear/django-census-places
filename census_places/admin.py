from django.contrib.gis import admin

from census_places.models import PlaceBoundary, ZIPBoundary

class PlaceBoundaryAdmin(admin.options.OSMGeoAdmin):
    list_display = (
        'name',
        'get_state_display',
        'place',
        'lsad',
        'censusarea',
    )
    list_filter = (
        'lsad',
    )
    search_fields = (
        'name',
    )

    def get_state_display(self, obj):
        return obj.get_state_display()
    get_state_display.short_description = 'State'

admin.site.register(PlaceBoundary, PlaceBoundaryAdmin)

class ZIPBoundaryAdmin(admin.options.OSMGeoAdmin):
    list_display = (
        'zip_code',
        'state',
        'lat',
        'lng'
    )
    list_filter = (
        'state',
    )
    search_fields = (
        'zip_code',
    )

admin.site.register(ZIPBoundary, ZIPBoundaryAdmin)
