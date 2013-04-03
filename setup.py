from distutils.core import setup

from census_places import __version__

setup(
    name='django-census-places',
    version=__version__,
    url='http://bitbucket.org/latestrevision/django-census-places/',
    description='Use city (and census designated place) boundaries provided by the United States Census',
    author='Adam Coddington',
    author_email='me@adamcoddington.net',
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    packages=[
        'census_places',
        'census_places.management',
        'census_places.management.commands',
        'census_places.migrations',
    ]
)
