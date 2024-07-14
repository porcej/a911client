#!/usr/bin/env python
# -*- coding: ascii -*-

"""
Sample App to demonstrage Active911

Changelog:
	- 2018-05-15 - Initial Commit

"""

__author__ = "Joseph Porcelli (porcej@gmail.com)"
__version__ = "0.0.1"
__copyright__ = "Copyright (c) 2018 Joseph Porcelli"
__license__ = "MIT"


import os
import sys
import logging
import getpass
import configparser
import json
from optparse import OptionParser
from pathlib import Path
from a911client import Active911



# Here we handle some command line input funkyness
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input



class Active911Client(Active911):
    """
    Here we override Active911 to implament a simple
    demonstration client
    - We are just going to pretty print the json to the screen
    """
    def alert(self, alert_id, alert_msg):
        """
        This is where we do somehting with the alert.
        This method should be implamented using the 
        """
        logging.info("Alert {}:\n\n{}\n".format(alert_id, json.dumps(alert_msg)))



if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # Registraion id.
    optp.add_option("-a", "--aid", dest="areg",
                    help="Active911 Registration ID")
    
    # Parse command line arguments, opts holds values, args holds options
    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%H:%M:%S')

    if opts.areg is None:
         opts.areg = raw_input("A911 Device ID: ")

    # xmpp = Active911Client(opts.areg, opts.opath)
    xmpp = Active911Client(opts.areg)
    xmpp.initialize()
    xmpp.run()


    # We wrap the XMPP stuff in a try..finally clause
    # to fource the disconnect method to run if there is any error
    # try:
    #     # Connect to the XMPP server and start processing XMPP stanzas.
    #     if not xmpp.connect():
    #         print('Unable to connect.')
    #         sys.exit(1)

    #     xmpp.process(block=True)
        
    #     print('Done')
    # finally:
    #     xmpp.disconnect()
