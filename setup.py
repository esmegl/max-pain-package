#!/usr/bin/python3

from setuptools import setup


setup(
	name='mp-calc',
	version='0.0.1',
	author='Esmeralda Gallardo',
	author_email='gallardo.esmeralda05@gmail.com',
	packages=['mp_calc'],
	install_requires=[
        'docker',
		'pytest',
        'asks',
        'elasticsearch',
        'cryptofeed',
        'trio'
	]
)