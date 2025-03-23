#!/usr/bin/env python
# -*- coding: ascii -*-

"""
A really simple client for Active 911 Alerts


This software is licensed as described in the README.md and LICENSE
file, which you should have received as part of this distribution.

Changelog:
    - 2018-12-12 - Initial Commit
    - 2019-02-27 - Fixed several typos
    - 2019-02-27 - Changes requires to install_requires
"""

from setuptools import setup, find_packages

from a911client import __version__

VERSION          = __version__
DESCRIPTION      = 'A tiny Python client for Active911 alert messages.'
# with codecs.open('README.md', 'r', encoding='UTF-8') as readme:
#     LONG_DESCRIPTION = ''.join(readme)

CLASSIFIERS      = [ 'Intended Audience :: Developers',
                     'License :: OSI Approved :: MIT License',
                     'Programming Language :: Python',
                     'Programming Language :: Python :: 3',
                     'Operating System :: OS Independent',
                     'Topic :: Software Development :: Libraries :: Python Modules'
                   ]

REQUIREMENTS     = [
                     'requests',
                     'slixmpp',
                     'urllib3',
                    ]
SETUP_REQUIREMENTS = ['requests']

# packages     = [ 'A911Client' ]

setup(
    name             = "a911client",
    version          = VERSION,
    description      = DESCRIPTION,
    long_description = open('README.md').read(),
    long_description_content_type = 'text/markdown',
    author       = 'Joe Porcelli',
    author_email = 'joe@kt3i.com',
    url          = 'http://github.com/porcej/a911client',
    license      = 'MIT',
    platforms    = [ 'any' ],
    packages     = find_packages(),
    install_requires     = REQUIREMENTS,
    setup_requires = SETUP_REQUIREMENTS,
    classifiers  = CLASSIFIERS,
    python_requires='>=3.6',
)
