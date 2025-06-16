#!/usr/bin/env python
# -*- coding: ascii -*-

"""
Active911 Python
Elixir and Tonic
Extends SliXMPP's ClientXMPP to support Active911.

Changelog:
    - 2018-05-15 -  Initial Commit
    - 2018-12-12 -  Added sleekmonkey to __init__ to better handle 
                    TLS Cert Dates
    - 2019-02-28 -  Replaced response.content with response.text 
                    to support legacy json implamentations
    - 2025-03-24 - Migrated from SleekXMPP to Slixmpp
    - 2024-03-24 - Added type hints and improved structure

"""

from __future__ import annotations

__author__ = "Joseph Porcelli (porcej@gmail.com)"
__version__ = "0.1.2"
__copyright__ = "Copyright (c) 2024 Joseph Porcelli"
__license__ = "MIT"

__all__ = ['Active911Config']


from dataclasses import dataclass
from typing import ClassVar


@dataclass
class Active911Config:
    """
    Configuration settings for Active911 client.
    
    This class contains all the necessary configuration parameters for connecting
    to and interacting with the Active911 service.
    """
    # API endpoints
    access_uri: ClassVar[str] = "https://access.active911.com/web_api.php"
    register_resource: ClassVar[str] = "?operation=register&device_code="
    markerfactory_uri: ClassVar[str] = "https://markerfactory.active911.com"
    
    # XMPP settings
    xmpp_server: ClassVar[str] = "push.active911.com"
    xmpp_protocol: ClassVar[str] = "https"
    xmpp_port: ClassVar[str] = "5280"
    xmpp_domain: ClassVar[str] = "push.active911.com"
    xmpp_resource: ClassVar[str] = "http-bind"
    xmpp_conference_name: ClassVar[str] = "conference.push.active911.com"
    
    # Other settings
    google_maps_uri: ClassVar[str] = "https://maps.googleapis.com/maps/api/js?client=gme-active911inc&v=3.53&sensor=false$channel=TESTING",
    reload_after_days: ClassVar[int] = 1
    reload_at_hour: ClassVar[int] = 2
    region_code: ClassVar[str] = ""
    init_resource: ClassVar[str] = "?&operation=init"
    client_version: ClassVar[str] = "1747693468"

    @classmethod
    def register_url(cls, device_code: str) -> str:
        """
        Generate an ActiveAlert Registration URL.

        Args:
            device_code: Active 911 Device code to register

        Returns:
            Active 911 Registration URL for the given device code
        """
        return f'{cls.access_uri}{cls.register_resource}{device_code}'

    @classmethod
    def xmpp_uri(cls) -> str:
        """
        Get the XMPP Connect URI.

        Returns:
            XMPP Connect URI
        """
        return f'{cls.xmpp_protocol}://{cls.xmpp_server}:{cls.xmpp_port}/{cls.xmpp_resource}'

    @classmethod
    def initialization_uri(cls) -> str:
        """
        Get the ActiveAlert Initialization URL.

        Returns:
            Active Alert Initialization URI
        """
        return f'{cls.access_uri}{cls.init_resource}'