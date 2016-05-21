#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from setuptools import setup


name = 'log'
package = 'log'
description = 'because you deserve better than log4j'
url = 'https://github.com/vforgione/log'
author = 'Vince Forgione'
author_email = 'vince.4gione@icloud.com'
license = 'MIT'

install_requires = []

timezone_requires = install_requires + [
    'arrow',
]

dev_requires = timezone_requires + [
    'pytest',
    'pytest-cov',
    'capturer',
    'coveralls',
    'flake8',
]

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: MacOS',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
]


def get_version(pkg):
    init_py = open(os.path.join(pkg, '__version__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


def get_packages(pkg):
    return [
        dirpath for dirpath, dirnames, filenames in os.walk(pkg)
        if os.path.exists(os.path.join(dirpath, '__init__.py'))
    ]


def get_package_data(pkg):
    walk = [
        (dirpath.replace(pkg + os.sep, '', 1), filenames) for dirpath, dirnames, filenames in os.walk(pkg)
        if not os.path.exists(os.path.join(dirpath, '__init__.py'))
    ]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename) for filename in filenames])
    return {pkg: filepaths}


setup(
    name=name,
    version=get_version(package),
    url=url,
    license=license,
    description=description,
    author=author,
    author_email=author_email,
    classifiers=classifiers,
    packages=get_packages(package),
    install_requires=install_requires,
    extras_require={
        'timezone': timezone_requires,
        'dev': dev_requires,
    },
)
