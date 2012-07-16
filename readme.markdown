Introduction
============

Do you have GPS data that you would like to populate with City & State information?  This Django application allows you to import census-designated place shapefiles provided by the United States Census, and then utilize that data to find the city and state for any given point.

Use
---

For a point named `point`, you can find which (if any) city or [census designated place](http://en.wikipedia.org/wiki/Census-designated_place) the point is within by finding which PlaceBoundary object overlaps this point, like:

    from census_places.models import PlaceBoundary

    try:
        city = PlaceBoundary.objects.get(
                geog__covers=point
                )
    except PlaceBoundary.DoesNotExist:
        city = None

Sometimes, though, you might be in the uncivilized parts, and your `point` may not be within a census designated place; if you happen to be gathering data from places that might not be within a census designated place, you might have a desire to gather the nearest city to any given point:

    from census_places.models import PlaceBoundary

    def get_nearest_city(point, buffer=0.1, buffer_interval=0.1, buffer_maximum=10):
        while buffer <= buffer_maximum:
            buffered_point = point.buffer(buffer)
            cities = PlaceBoundary.objects.filter(geog__bboverlaps=buffered_point)\
                    .distance(point)\
                    .order_by('distance')
            if cities.count() > 0:
                return cities[0]
            else:
                buffer = buffer + buffer_interval
                return get_nearest_city(point, buffer, buffer_interval, buffer_maximum)
        raise Exception("You must be in an exceptionally rustic place at the moment.")

Commands
--------

`import_places <State/Protectorate Name|FIPS code|'all'>`: Download the specified state or protectorate's shapefile (or 'all' available shapefiles), and import the data into your application.

Examples
--------

If you, perhaps, live in Portland, Oregon, and are using this application to identify the city name for any points gathered from Google Latitude or another service, you may desire to import data for only Washington and Oregon.  To do that you would run:

    python manage.py import_places Oregon
    python manage.py import_places Washington

But if you happen using this location information for data that could be from any state, you would instead run::

    python manage.py import_places all
