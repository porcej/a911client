#!/usr/bin/env python
# -*- coding: ascii -*-

"""Active911 Python Client Library.

This library extends SliXMPP's ClientXMPP to support Active911's real-time
incident notification system. It provides a robust interface for connecting
to Active911's services and handling alerts.

Changelog:
    - 2018-05-15 - Initial Commit
    - 2018-12-12 - Added sleekmonkey to __init__ to better handle TLS Cert Dates
    - 2019-02-28 - Replaced response.content with response.text to support legacy json
    - 2025-03-24 - Migrated from SleekXMPP to Slixmpp and updated run method for asyncio
    - 2024-03-24 - Added improved error handling, type hints, and connection management
    - 2024-03-24 - Added connection state tracking and heartbeat monitoring
    - 2025-06-14 - Renamed module to a911client and updated imports
    - 2025-06-16 - Added Active911Alert class and updated imports
"""

from a911client.Active911Config import Active911Config
from a911client.Active911Exceptions import (
    Active911Error,
    Active911ConnectionError,
    Active911AuthenticationError,
)
from a911client.Active911Xmpp import Active911Xmpp
from a911client.Active911Client import Active911Client
from a911client.Active911Alert import Active911Alert

__author__ = "Joseph Porcelli (porcej@gmail.com)"
__version__ = "0.2.0"
__copyright__ = "Copyright (c) 2025 Joseph Porcelli"
__license__ = "MIT"

__all__ = [
    'Active911Config',
    'Active911Error',
    'Active911ConnectionError',
    'Active911AuthenticationError',
    'Active911Xmpp',
    'Active911Client',
    'Active911Alert',
]
