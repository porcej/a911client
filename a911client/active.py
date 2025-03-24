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
    - 2025-03-24 - Migrated from SleekXMPP to Slixmpp and updated run method for asyncio
"""

__author__ = "Joseph Porcelli (porcej@gmail.com)"
__version__ = "0.1.1"
__copyright__ = "Copyright (c) 2024 Joseph Porcelli"
__license__ = "MIT"

__all__ = ['Active911']


import asyncio
import json
import logging
import requests
import sys
from slixmpp import ClientXMPP
from a911client.ActiveConfig import Active911Config

class Active911(ClientXMPP):
    """
    A really simple wrapper for Active911.
    """
    session = requests.Session()
    app = None
    logger = logging

    def __init__(self, device_code, app=None):
        """
        Initializes the XMPP client.

        Parameters:
        -----------
        device_code : str
            Active911 Device Code.
        app : Object
            Application class to run under or None.
        """
        if app:
            self.app = app
            self.logger = app.logger
        else:
            self.logger = logging

        # Get the device id and registration information and set cookie.
        response = self.session.get(Active911Config.register_url(device_code))
        rjson = json.loads(response.text)

        if rjson['result'] == 'success':
            self.logger.info("Client registration to Active911 successful.")
        elif rjson['result'] == 'Unauthorized':
            self.logger.error('Client registration to Active911 failed: Unauthorized')
            raise Exception('Client registration to Active911 failed: Unauthorized')
        else:
            self.logger.error('Client registration to Active911 failed: ' + rjson['message'])
            raise Exception('Client registration to Active911 failed: ' + rjson['message'])

        # Check that the required cookies were set.
        if (('a91_device_id' not in self.session.cookies) or 
            ('a91_registration_code' not in self.session.cookies)):
            self.logger.error("Invalid Active911 Device ID or bad network connection.")
            raise Exception('Invalid Active911 Device ID or bad network connection')

        # Construct the JID.
        jid = "device" + self.session.cookies['a91_device_id'] + "@" + Active911Config.xmpp_domain
        password = self.session.cookies['a91_registration_code']

        # Ensure an event loop is available.
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError as e:
            if str(e).startswith('There is no current event loop in thread'):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            else:
                raise

        super().__init__(jid, password)

        self['feature_mechanisms'].unencrypted_plain = True

        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0004')  # Data Forms
        self.register_plugin('xep_0060')  # PubSub
        self.register_plugin('xep_0199')  # XMPP Ping

        # Starting XMPP sessions.
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("position", self.position)   # Discard position information
        self.add_event_handler("ssl_invalid_cert", self.discard)

    async def start(self, event):
        """
        Handles session start event, sets presence, and logs the session start.
        """
        self.send_presence()
        self.logger.info("XMPP Session started...")

    async def message(self, msg):
        """
        Handles incoming messages and replies with a thank-you message.
        """
        if msg['type'] in ('chat', 'normal'):
            alert_ids = msg['body'].split(':')

            # Request alert from Web API.
            alert_msg = self.session.get(
                "%s?operation=fetch_alert&message_id=%s&_=%s" %
                (Active911Config.access_uri, alert_ids[1], alert_ids[2]))
            alert_data = alert_msg.json()

            self.logger.info("Message {} received.".format(alert_ids[1]))
            self.alert(alert_ids[1], alert_data)

    def initialize(self):
        """
        Downloads the last 10 A911 alerts and processes them.
        """
        response = self.session.get(Active911Config.initialization_uri())
        data = json.loads(response.text)

        if data['result'] == 'success':
            self.logger.info("Active911 initialized.")
            alerts = data['message']['alerts']
            for idx, alert in enumerate(alerts):
                alert_response = {'result': 'success', 'message': alert, 'init': True}
                self.alert(idx, alert_response)
        else:
            err_msg = f'Client initialization to Active911 failed: {data["result"]} - {data["message"]}'
            self.logger.error(err_msg)
            raise Exception(err_msg)

    def alert(self, alert_id, alert_msg):
        """
        Handles alert information. This method should be implemented by the client.
        """
        self.logger.info("Alert {}:\n\n{}\n".format(alert_id, alert_msg))

    def position(self, loc):
        """
        Processes position information (currently just logs it).
        """
        self.logger.info(loc['from'] + " new position is " + loc['body'] + ".")

    def discard(self, event):
        """
        Discards events we don't care about.
        """
        return

    def run(self, block=True):
        """
        Performs connection handling using the asyncio event loop.
         - Connects to the server, then runs the loop until interrupted.
         - On interruption, disconnects cleanly.
        """
        loop = asyncio.get_event_loop()
        try:
            self.connect(address=(Active911Config.xmpp_server, Active911Config.xmpp_port))
            self.logger.info("Connected to Active911 via XMPP.")
            # Run the event loop indefinitely.
            loop.run_forever()
            self.logger.info("Closing XMPP connection to Active911.")
        except KeyboardInterrupt:
            self.logger.info("KeyboardInterrupt received, disconnecting...")
        finally:
            loop.run_until_complete(self.disconnect())
            self.logger.info("Disconnected from Active911.")


if __name__ == '__main__':
    """
    By default, the module does nothing.
    """
    pass