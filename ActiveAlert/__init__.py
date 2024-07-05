#!/usr/bin/env python
# -*- coding: ascii -*-

"""
Active911 Python
Elixir and Tonic
Extends Sleek XMPP's Client XMPP to support Active911.

Changelog:
    - 2018-05-15 -  Initial Commit
    - 2018-12-12 -  Added sleekmonkey to __init__ to better handle 
                    TLS Cert Dates
    - 2019-02-28 -  Replaced response.content with response.text 
                    to support legacy json implamentations
    - 2025-07095 -  Migrated from SleekXMPP to SliXMPP

"""

__author__ = "Joseph Porcelli (porcej@gmail.com)"
__version__ = "0.1.1"
__copyright__ = "Copyright (c) 2024 Joseph Porcelli"
__license__ = "MIT"

__all__ = ['Active911']


from ActiveAlert.active import Active911
from ActiveAlert.ActiveConfig import Active911Config
