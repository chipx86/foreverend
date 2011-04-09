#!/usr/bin/env python

import os
import shutil
import sys

from ez_setup import use_setuptools
use_setuptools()

from setuptools import find_packages

try:
    import py2exe
except:
    pass


PACKAGE_NAME = 'forever_end'
APP_NAME = 'foreverend'
VERSION = '0.3'

METADATA = dict(
    name=PACKAGE_NAME,
    version=VERSION,
    description='Time has been fractured by a mysterious artifact, and '
                'only *you* are probe enough to fix it.',
    author='Christian Hammond',
    author_email='chipx86@chipx86.com',
    entry_points={
        'console_scripts': [
            'forever_end = foreverend.game:main',
        ],
    },
    install_requires=[
        'pygame',
    ],
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Games/Entertainment :: Platforming',
    ])

cmd = sys.argv[1]

if cmd in ('build_exe', 'install_exe'):
    from cx_Freeze import setup, Executable

    METADATA['executables'] = [Executable('main.py')]

    #setup(**METADATA)

    exclude_modules = ['tcl', 'tk']

    dist_dir = os.path.join('dist', '%s_%s' % (PACKAGE_NAME, VERSION))
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.system("cxfreeze --install-dir='%s' --target-name='%s' "
              "--exclude-modules=%s main.py" %
              (dist_dir, APP_NAME, ','.join(exclude_modules)))

    for dirname in exclude_modules:
        path = os.path.join(dist_dir, dirname)

        if os.path.exists(path):
            shutil.rmtree(path)

    dest_data_dir = os.path.join(dist_dir, 'data')

    if os.path.exists(dest_data_dir):
        shutil.rmtree(dest_data_dir)

    shutil.copytree(data_dir, dest_data_dir)
else:
    from setuptools import setup
    setup(**METADATA)
