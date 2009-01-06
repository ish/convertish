from setuptools import setup, find_packages
import sys, os

version = '0.5.1'

setup(name='convertish',
      version=version,
      description="Convertish is a type coercion library",
      long_description="""\
Convertish uses adaption to coerce variable types. It currently has converters registered for schemaish types but is easily extended.
""",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Environment :: Web Environment",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2",
      ], 
      keywords='convert,converstion,coercion,adapt,adaption,schema',
      author='Tim Parkin, Matt Goodall',
      author_email='developers@ish.io',
      url='http://ish.io/projects/show/convertish',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
