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


import asyncio
import json
import logging
import requests
import sys
from slixmpp import ClientXMPP
from a911client.ActiveConfig import Active911Config

class Active911(ClientXMPP):
    """
    A really simple wrapper for Active911
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
            Active911 Device Dode.
        app : Object
            Application class to run under or None
        """

        # Add logging
        if app:
            self.app = app;
            self.logger = app.logger
        else:
            self.logger = logging


        # Get the device id and registration infromation for 
        #   device code and set cookie
        # response = self.session.get(f'{Active911Config.register_url}{device_code}');
        response = self.session.get(Active911Config.register_url(device_code))
        rjson = json.loads(response.text)

        if rjson['result'] == 'success':
            self.logger.info("Client registration to Active911 sucessful.")

        elif rjson['result'] == 'Unauthorized':
            self.logger.error('Client registration to Active911 failed: Unauthorized')
            raise Exception('Client registration to Active911 failed: Unauthorized')

        else:
            self.logger.error('Client registration to Active911 failed: ' \
                + rjson['message'] )
            raise Exception('Client registration to Active911 failed: ' \
                + rjson['message'] )

        # Added on 2018-04-26 - Check to make sure the cookies
        if ((not 'a91_device_id' in self.session.cookies) and 
                (not 'a91_registration_code' in self.session.cookies)):

            # We raise an exception rather than quiting to let the app handle the issue
            self.logger.error("Invalid Active911 Device ID or bad network connection.")
            raise Exception('Invalid Active911 Device ID or bad network connection')
            # sys.exit("Invalid Active911 Device ID or bad network connection.")

        # JID = "deivce[a91_device_id]@[domain]"
        jid = "device" + self.session.cookies['a91_device_id'] + "@" + Active911Config.xmpp_domain
        password = self.session.cookies['a91_registration_code']


        # Check the thread for an eventloop, if there is not one, create one
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

        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0199') # XMPP Ping

        # Starting XMPP sessions
        self.add_event_handler("session_start", self.start)
        # Parse incoming messages
        self.add_event_handler("message", self.message)
        # Discard Position Information
        self.add_event_handler("position", self.position)   # Need to run api->init first
        # Discard SSL Errors
        self.add_event_handler("ssl_invalid_cert", self.discard)

    async def start(self, event):
        """
        Handles session start event, sets presence, gets roster, and joins a conference room.

        Parameters:
        -----------
        event : dict
            The event data.
        """

        self.send_presence()
        # Active911 does not provide a roster
        # await self.get_roster(). 
        self.logger.info("XMPP Session started...")


    async def message(self, msg):
        """
        Handles incoming messages and replies with a thank-you message.

        Parameters:
        -----------
        msg : Message
            The incoming message object.
        """
        if msg['type'] in ('chat', 'normal'):
            alert_ids = msg['body'].split(':')

            # Reguest alert from Web API
            alert_msg = self.session.get(
                "%s?operation=fetch_alert&message_id=%s&_=%s" %
                    (Active911Config.access_uri, alert_ids[1], alert_ids[2]))
            alert_data = alert_msg.json()
            
            self.logger.info("Message {} received.".format(alert_ids[1]))
            self.alert(alert_ids[1], alert_data)

    def initialize(self):
        """
        Here we download last 10 A911 alerts
        we may do other stuff here later
        """
        # Initialize for position reporting
        response = self.session.get(Active911Config.access_uri + "?&operation=init")
        data = json.loads(response.text)

        if data['result'] == 'success':
            self.logger.info("Active911 sucessfully initilized.")
            alerts = data['message']['alerts']
            for idx, alert in enumerate(alerts):
                alert_response = {'result': 'success', \
                                    'message': alert, \
                                    'init': True}
                
                self.alert(idx, alert_response)


        elif data['result'] == 'Unauthorized':
            self.logger.error('Client initilization to Active911 failed: Unauthorized')
            raise Exception('Client initilization to Active911 failed: Unauthorized')

        else:
            self.logger.error('Client initilization to Active911 failed: ' \
                + data['message'] )
            raise Exception('Client initilization to Active911 failed: ' \
                + data['message'] )


    def alert(self, alert_id, alert_msg):
        """
        This is where we do somehting with the alert.
        This method should be implamented by the client
        to do something with the generated alert
        """
        self.logger.info("Alert {}:\n\n{}\n".format(alert_id, alert_msg))



    def position(self, loc):
        """
        This is where we process position information... big hint...
            we don't actually do anything here
        """
        self.logger.info(loc['from'] + " new position is " + loc['body'] + ".")

    def discard(self, event):
        """
        This does nothing.  This can be called for events that we don't care about.
        """
        return

    def run(self, block=True):
        """
        Performs connection handling 
         - If block is true (default), blocks keeps the thread alive
                until a disconnect stanza is received or a termination
                commaned is issued (<Ctrl> + C)
         - If block is false  - thread does not block only use this 
                if your're handling threading in the client

        """
        # We wrap the XMPP stuff in a try..finally clause
        # to force the disconnect method to run if there is any error
        try:
            # Connect to the XMPP server and start processing XMPP stanzas.
            self.connect(address=(Active911Config.xmpp_server, Active911Config.xmpp_port))
            # if not self.connect(address=(Active911Config.xmpp_server, Active911Config.xmpp_port)):
            #     self.logger.error("Unable to connect to Active911")
            #     sys.exit(1) # If we can't connect, then why are we here

            self.logger.info("Connected to Active911 via XMPP.")
            self.process(forever=True)
            self.logger.info("Closing XMPP connection to Active911.")
            
        finally:
            self.disconnect()
            self.logger.info("Disconnected from Active911.")


if __name__ == '__main__':
    """
    By Default we do nothing.
    """
    None
