# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='sgio',
    version='0.1.0',
    description='I/O for VABS and SwiftComp',
    long_description=readme,
    author='Su Tian',
    author_email='sutian@analyswiftcomp',
    url='https://github.com/wenbinyugroup/sgio',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
