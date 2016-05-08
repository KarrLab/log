#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
from setuptools import setup


name = 'log'
package = 'log'
description = 'because you deserve something better than log4j'
url = 'https://github.com/vforgione/log'
author = 'Vince Forgione'
author_email = 'vince.4gione@icloud.com'
license = 'MIT'

install_requires = []
version = sys.version_info
if version.major == 3 and version.minor < 4:
    install_requires.append('enum')

dev_requires = [
    'pytest',
]

arrow_requires = [
    'arrow',
]


def get_version(pkg):
    init_py = open(os.path.join(pkg, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


def get_packages(pkg):
    return [dirpath for dirpath, dirnames, filenames in os.walk(pkg) if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(pkg):
    walk = [(dirpath.replace(pkg + os.sep, '', 1), filenames) for dirpath, dirnames, filenames in os.walk(pkg) if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

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
    packages=get_packages(package),
    install_requires=install_requires,
    extras_require={
        'dev': dev_requires,
        'arrow': arrow_requires,
    },
)
