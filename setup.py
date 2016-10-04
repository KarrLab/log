#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
from setuptools import setup, find_packages


name = 'log'
package = 'log'
description = 'because you deserve better than log4j'
url = 'https://github.com/vforgione/log'
author = 'Vince Forgione'
author_email = 'vince.4gione@icloud.com'
license = 'MIT'

install_requires = [
    'PyYAML',
    'six'
]
if sys.version_info < (3, 4, 0):
    install_requires.append('enum34')

timezone_requires = install_requires + [
    'arrow',
]

dev_requires = timezone_requires + [
    'pytest',
    'pytest-cov',
    'capturer',
    'coveralls',
    'flake8',
    'sphinx',
    'sphinx-autobuild',
    'sphinx-rtd-theme',
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


setup(
    name=name,
    version=get_version(package),
    url=url,
    license=license,
    description=description,
    author=author,
    author_email=author_email,
    classifiers=classifiers,
    packages=find_packages(exclude=['*tests*']),
    install_requires=install_requires,
    extras_require={
        'timezone': timezone_requires,
        'dev': dev_requires,
    },
)
