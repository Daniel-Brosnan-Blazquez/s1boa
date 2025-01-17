"""
Setup configuration for the s1boa application

Written by DEIMOS Space S.L. (dibb)

module s1boa
"""
from setuptools import setup, find_packages

setup(name="s1boa",
      version="1.0.0",
      description="S1 engine and visualization tool for Business Operation Analysis",
      author="Daniel Brosnan",
      author_email="daniel.brosnan@deimos-space.com",
      packages=find_packages(),
      include_package_data=True,
      python_requires='>=3',
      install_requires=[
          "eboa",
          "vboa",
          "astropy",
          "massedit"
      ],
      test_suite='nose.collector')
