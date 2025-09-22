#!/usr/bin/env python
# -*- coding: ascii -*-

"""
A modern Python client library for interacting with Active911's API and XMPP interface.

This library provides a robust, type-safe, and async-first approach to handling 
Active911 alerts and communications.

This software is licensed as described in the README.md and LICENSE
file, which you should have received as part of this distribution.

Changelog:
    - 2018-12-12 - Initial Commit
    - 2019-02-27 - Fixed several typos
    - 2019-02-27 - Changes requires to install_requires
    - 2025-03-24 - Migrated from SleekXMPP to Slixmpp and updated for asyncio
    - 2024-03-24 - Added improved error handling, type hints, and connection management
    - 2025-06-14 - Renamed module to a911client and updated imports
    - 2025-06-16 - Added Active911Alert class and updated imports
"""

from setuptools import setup, find_packages

from a911client import __version__

VERSION          = __version__
DESCRIPTION      = 'A modern Python client library for Active911 API and XMPP interface.'
# with codecs.open('README.md', 'r', encoding='UTF-8') as readme:
#     LONG_DESCRIPTION = ''.join(readme)

CLASSIFIERS      = [ 'Intended Audience :: Developers',
                     'License :: OSI Approved :: MIT License',
                     'Programming Language :: Python',
                     'Programming Language :: Python :: 3',
                     'Programming Language :: Python :: 3.6',
                     'Programming Language :: Python :: 3.7',
                     'Programming Language :: Python :: 3.8',
                     'Programming Language :: Python :: 3.9',
                     'Programming Language :: Python :: 3.10',
                     'Programming Language :: Python :: 3.11',
                     'Programming Language :: Python :: 3.12',
                     'Operating System :: OS Independent',
                     'Topic :: Software Development :: Libraries :: Python Modules',
                     'Topic :: Communications :: Chat',
                     'Topic :: System :: Networking',
                     'Development Status :: 4 - Beta'
                   ]

REQUIREMENTS     = [
                     'aiohttp>=3.12.13',
                     'slixmpp>=1.10.0',
                     'typing-extensions>=4.9.0',
                    ]
SETUP_REQUIREMENTS = ['aiohttp>=3.12.13']

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
    keywords='active911 emergency alerts xmpp api client',
    project_urls={
        'Bug Reports': 'https://github.com/porcej/a911client/issues',
        'Source': 'https://github.com/porcej/a911client',
        'Documentation': 'https://github.com/porcej/a911client#readme',
    },
)
