#!/usr/bin/env python
# -*- coding: ascii -*-

"""
Active911 Python
Elixir and Tonic
Extends Sleek XMPP's Client XMPP to support Active911.

Changelog:
	- 2018-05-15 - Initial Commit

"""

__author__ = "Joseph Porcelli (porcej@gmail.com)"
__version__ = "0.0.1"
__copyright__ = "Copyright (c) 2018 Joseph Porcelli"
__license__ = "MIT"

__all__ = ['Active911']


import os
import sys
import logging
import sleekxmpp
import requests


class Active911(sleekxmpp.ClientXMPP):
    """
    A really simple wrapper for Active911
    """

    # Here are out application constants
    api_url = "https://access.active911.com/interface/web_api.php"
    domain = "push.active911.com"

    session = requests.Session()


    def __init__(self, device_code, output_dir):
        """
        Initilize the XMPP Client
        """
        opsResource = "?operation=register&device_code=" 

        # Get the device id and registration infromation for 
        #   device code and set cookie
        response = self.session.get(self.api_url + opsResource + device_code);


        # Added on 2018-04-26 - Check to make sure the cookies
        if ((not 'a91_device_id' in self.session.cookies) and 
                (not 'a91_registration_code' in self.session.cookies)):
           logging.error("Invalid Active911 Device ID or bad network connection.")
           sys.exit("Invalid Active911 Device ID or bad network connection.")

        # Initialize for position reporting
        # response = self.session.get(self.api_url + "?&operation=init")

        # Ensure the output directory exists
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)

        self.output_path = output_dir       

        
        # JID = "deivce[a91_device_id]@[domain]"
        jid = "device" + self.session.cookies['a91_device_id'] + "@" + self.domain
        password = self.session.cookies['a91_registration_code']

        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self['feature_mechanisms'].unencrypted_plain = True

        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0199') # XMPP Ping

        # Add handler for starting XMPP sessions and parsing incoming messages
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("position", self.position)   # Need to run api->init first

    def start(self, event):
        """
        All we want to do  is start... but to be sure everything
        is working correctly, we will send an empty presnce stanza
        """
        self.send_presence()
        # We don't care about a contact list so we skip fetching a roster
        # self.get_roster()
        logging.info("XMPP Session started...")


    def message(self, msg):
        """
        This is where we process incoming message stanzas
        """
        if msg['type'] in ('chat', 'normal'):
            alert_ids = msg['body'].split(':')

            # Reguest alert from Web API
            alert_msg = self.session.get(
                "%s?operation=fetch_alert&message_id=%s&_=%s" %
                    (self.api_url, alert_ids[1], alert_ids[2]))
            alert_data = alert_msg.json()
            
            logging.info("Message {} received.".format(alert_ids[1]))
            alert(alert_id, alert_data)


    def alert(self, alert_id, alert_msg):
        """
        This is where we do somehting with the alert.
        This method should be implamented using the 
        """
        logging.info("Alert {}:\n\n{}\n".format(alert_id, alert_msg))



    def position(self, loc):
        """
        This is where we process position information... big hint...
            we don't actually do anything here
        """
        logging.info(loc['from'] + " new position is " + loc['body'] + ".")


if __name__ == '__main__':
	"""
	By Default we do nothing.
	"""
	None
