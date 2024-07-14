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
    - 2025-07095 -  Migrated from SleekXMPP to SliXMPP

"""

__author__ = "Joseph Porcelli (porcej@gmail.com)"
__version__ = "0.1.1"
__copyright__ = "Copyright (c) 2024 Joseph Porcelli"
__license__ = "MIT"

__all__ = ['Active911']


class Active911Config:
    """
    Represents different constants used by Active911

    """
    access_uri = "https://access.active911.com/web_api.php"
    register_resource = "?operation=register&device_code=" 
    markerfactory_uri = "https://markerfactory.active911.com"
    xmpp_server = "push.active911.com"
    xmpp_protocol = "https"
    xmpp_port = "5280"
    xmpp_domain = "push.active911.com"
    xmpp_resource = "http-bind"
    xmpp_conference_name = "conference.push.active911.com"
    google_maps_uri = "https://maps.googleapis.com/maps/api/js?client=gme-active911inc&v=3.53&sensor=false$channel=TESTING"
    reload_after_days = 1
    reload_at_hour = 2
    region_code = ""
    mixpanel_token = "2e3710ffc695cdb34dac95bcc07148d1"
    init_resource = "?&operation=init"
    # register_url = f'{access_uri}{register_resource}'

    @staticmethod
    def register_url(device_code: str) -> str:
        """
        Generates an ActiveAlert Registration URL

        Arguments:
            device_code (Str): Active 911 Device code to register

        Returns:
            str: Active 911 Registration URL for the given device code
        """
        return f'{Active911Config.access_uri}{Active911Config.register_resource}{device_code}'

    @staticmethod
    def xmpp_uri() -> str:
        """
        Returns a string representing the XMPP Connect URI

        Returns:
            str: XMPP Connect URI
        """
        return f'{Active911Config.xmpp_protocol}://{Active911Config.xmpp_server}:{Active911Config.xmpp_port}/{Active911Config.xmpp_resource}'

    @staticmethod
    def initialization_uri() -> str:
        """
        Returns a string representing the ActiveAlert Initilization URL

        Returns:
            (str): Active Alert Intilization URI
        """
        return f'{Active911Config.access_uri}{Active911Config.init_resource}'