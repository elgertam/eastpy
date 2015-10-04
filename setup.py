#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'attrs>=15.0.0',
    'typing>=3.5.0',
]

test_requirements = [
]

setup(
    name='eastpy',
    version='0.1.1',
    description="East-oriented Python examples, based on James Ladd's \"East-oriented\" technique.",
    long_description=readme + '\n\n' + history,
    author="Andrew M Elgert",
    author_email='andrew.elgert@gmail.com',
    url='https://github.com/elgertam/eastpy',
    packages=[
        'eastpy',
    ],
    package_dir={'eastpy':
                 'eastpy'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='eastpy',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
