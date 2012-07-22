from distutils.core import setup

setup(
    name='django-census-places',
    version='1.2.1',
    url='http://bitbucket.org/latestrevision/django-census-places/',
    description='Use city (and census designated place) boundaries provided by the United States Census',
    author='Adam Coddington',
    author_email='me@adamcoddington.net',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    packages=[
        'census_places',
        'census_places.management',
        'census_places.management.commands',
        ]
)
