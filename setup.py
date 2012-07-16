from setuptools import setup

setup(
    name='census_places',
    version='1.0.3',
    url='http://bitbucket.org/latestrevision/django-census-places/',
    description='Import and utilize place boundaries provided by the United States Census',
    author='Adam Coddington',
    author_email='me@adamcoddington.net',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    packages=['census_places', 'census_places.management.commands'],
)
