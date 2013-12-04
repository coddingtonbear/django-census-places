Django-census-places
====================

Do you have GPS data that you would like to populate with City & State information?  This Django application allows you to import census-designated place shapefiles provided by the United States Census, and then utilize that data to find the city and state for any given point within the United States.

Installation
------------

You can either install from pip:

    pip install django-census-places

*or* checkout and install the source from the [bitbucket repository](https://bitbucket.org/latestrevision/django-census-places):

    hg clone https://bitbucket.org/latestrevision/django-census-places
    cd django-census-places
    python setup.py install

*or* checkout and install the source from the [github repository](https://github.com/latestrevision/django-census-places):

    git clone https://github.com/latestrevision/django-census-places.git
    cd django-census-places
    python setup.py install

If you, perhaps, live in Portland, Oregon, and are using this application to identify the city name for any points gathered from Google Latitude or another service, you may desire to import data for only Washington and Oregon.  To do that you would run:

    python manage.py import_places Oregon
    python manage.py import_places Washington

But if you happen using this location information for data that could be from any state, you would instead run::

    python manage.py import_places all

See the 'Commands' section below for more information.

Use
---

For a point named `point`, you can find which (if any) city or [census designated place](http://en.wikipedia.org/wiki/Census-designated_place) the point is within by finding which PlaceBoundary object overlaps this point, like:

    from census_places.models import PlaceBoundary

    try:
        city = PlaceBoundary.get_containing(point)
    except PlaceBoundary.DoesNotExist:
        # You are currently outside of any known city's boundaries
        city = None

Sometimes, though, you might be in the uncivilized parts, and your `point` may not be within a census designated place; if you happen to be gathering data from places that might not be within a census designated place, you might have a desire to gather the nearest city to any given point:

    from census_places.models import PlaceBoundary

    try:
        city = PlaceBoundary.get_nearest_to(point)
        # The returned object is annotated with its distance from the point you
        # specified, and can be gathered from its 'distance' property:
        print "This place is %s miles from me" % city.distance.mi
    except PlaceBoundary.DoesNotExist:
        # You must be in an exceptionally rustic place at the moment
        city = None

Commands
--------

`import_places <State/Protectorate Name|FIPS code|'all'>`: Download the specified state or protectorate's shapefile (or 'all' available shapefiles), and import the data into your application.


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/latestrevision/django-census-places/trend.png)](https://bitdeli.com/f
