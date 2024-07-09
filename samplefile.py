#!/usr/bin/env python
# -*- coding: ascii -*-

"""
Sample Implamentation of a911's Active911 class 
to write Alert Messages to files in a predefined
directory

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



"""
    TODO:
        - Persist device id across runs (sqllite, flatfile, 
            whathave you) This is a request form the fine folks
            at Active911.
        - Do better error checking (invalid device code, etc)
    Change Log:
        - 2018-04-26
            - Added cookie checking to make sure Active911 Device 
                ID is valid prior to continuing to initilize connection
"""

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input


class Active911Client(Active911):
    """
    Override Active911 - to dump json file of alert message
    """

    # Here we add output directory path to our client
    output_path = ''

    def __init__(self, device_code, output_dir):
        """
        Initilize the XMPP Client
        """

        # Ensure the output directory exists
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        self.output_path = output_dir

        # Call the Active911's constructor
        super().__init__(device_code=device_code)


    def alert(self, alert_id, alert_msg):
        """
        Here we handle the alert by saving it to a file in 
        self.output_path
        """
        with open(os.path.join(self.output_path, alert_id \
            + '.json'), 'w') as jfh:
                json.dump(alert_msg, jfh)


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
    
    # Output Path
    optp.add_option('-p', '--path', help="Output directory",
                    dest="opath")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%H:%M:%S')

    if opts.areg is None:
         opts.areg = raw_input("A911 Device ID: ")

    if opts.opath is None:
        opts.opath = raw_input("Output directory: ")

    xmpp = Active911Client(opts.areg, opts.opath)
    xmpp.run()

