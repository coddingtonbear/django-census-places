from django.contrib.gis import admin

from census_places.models import PlaceBoundary

class PlaceBoundaryAdmin(admin.options.OSMGeoAdmin):
    list_display = (
            'name',
            'get_state_display',
            'place',
            'lsad',
            'censusarea',
            )
    search_fields = (
                'name',
            )

    def get_state_display(self, obj):
        return obj.get_state_display()
    get_state_display.short_description = 'State'

admin.site.register(PlaceBoundary, PlaceBoundaryAdmin)
