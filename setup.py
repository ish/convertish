from setuptools import setup, find_packages
import sys, os

version = '0.6dev'

setup(name='convertish',
      version=version,
      description="Convertish is a type conversion library with converters for basic types",
      long_description="""\
Convertish uses adaption to coerce variable types. It currently has converters registered for schemaish types but is easily extended. It currently has a converter which can serialise most objects to strings. The library should be very easy to extend to convert to / from most types. 

      Changlog at `http://github.com/ish/convertish/raw/master/CHANGELOG <http://github.com/ish/convertish/raw/master/CHANGELOG>`_
""",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Environment :: Web Environment",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2",
      ], 
      keywords='convert conversion coercion adapt adaption schema',
      author='Tim Parkin, Matt Goodall',
      author_email='developers@ish.io',
      url='http://ish.io/projects/show/convertish',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "simplegeneric",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
