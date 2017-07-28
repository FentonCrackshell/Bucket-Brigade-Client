#!/usr/bin/env python

from setuptools import setup

setup(
	name='bucket-brigade',
    version='1.0',
    description='Distributed AWS bucket scanner',
    author='Fenton Crackshell',
    author_email='fentoncrackshell@outlook.com',
    url='http://disney.wikia.com/wiki/Fenton_Crackshell',
    packages=['bucket_sweep'],
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Programming Language :: Python :: 2.7'
	],
	install_requires=[
		"stem>=1.5.4",
		"requests>=2.18.1"
	],
    entry_points={
        'console_scripts': [
            'bucket_brigade=bucket_sweep.cli:start',
        ],
    }
)