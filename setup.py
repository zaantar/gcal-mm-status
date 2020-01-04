# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readmeText = f.read()

with open('LICENSE') as f:
    licenseText = f.read()

setup(
    name='gcal-mm-status',
    version='0.1.0',
    description='I\'m learning Python here!',
    long_description=readmeText,
    author='Jan Štětina',
    author_email='zaantar@gmail.com',
    url='https://github.com/zaantar/gcal-mm-status',
    license=licenseText,
    packages=find_packages(exclude=('tests', 'docs'))
)