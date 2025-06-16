#!/usr/bin/env python
# -*- coding: ascii -*-

"""Sample application demonstrating Active911Client usage.

This script demonstrates how to use the Active911Client to connect to Active911
via XMPP and display nicely formatted alerts.

Changelog:
    - 2025-06-14 - Renamed module to a911client and updated imports
    - 2025-06-14 - Updated to use Asyncio and Slixmpp
    - 2025-06-14 - Updated to use Active911Client
    - 2025-06-14 - Updated to use Active911Alert
    - 2025-06-14 - Updated to use Active911Config
    - 2025-06-14 - Updated to use Active911Error
    - 2025-06-14 - Updated to use Active911Xmpp
    - 2025-06-14 - Updated to use Active911Client
"""

__author__ = "Joseph Porcelli (porcej@gmail.com)"
__version__ = "0.2.0"
__copyright__ = "Copyright (c) 2025 Joseph Porcelli"
__license__ = "MIT"

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any

from a911client import Active911Client, Active911Alert


def setup_logging(level: str) -> logging.Logger:
    """Set up logging with the specified level.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')

    logger = logging.getLogger('active911')
    logger.setLevel(numeric_level)

    # Create console handler with formatting
    handler = logging.StreamHandler()
    handler.setLevel(numeric_level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def format_alert(alert_data: Dict[str, Any]) -> str:
    """Format alert data into a readable string.

    Args:
        alert_data: Alert data dictionary

    Returns:
        Formatted alert string
    """
    # Extract common fields
    print(f"\t\t *** Alert date is of type {type(alert_data)}")
    from pprint import pprint
    print(pprint(alert_data))
    print(f"\t\t *** Alert date is of type {type(alert_data)}")
    alert_id = alert_data.get('id', 'Unknown')
    timestamp = alert_data.get('timestamp', '')
    if timestamp:
        try:
            dt = datetime.fromtimestamp(int(timestamp))
            timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            pass

    # Format the alert
    output = [
        f"\n{'='*80}",
        f"Alert ID: {alert_id}",
        f"Time: {timestamp}",
        f"{'-'*80}"
    ]

    # Add address information
    if 'address' in alert_data:
        output.extend([
            "Location:",
            f"  {alert_data.get('address', 'Unknown Street')}",
            f"  {alert_data.get('city', 'Unknown City')}, "
            f"{alert_data.get('state', 'Unknown State')} "
        ])

    # Add call information
    if 'call' in alert_data:
        output.extend([
            "\nCall Information:",
            f"  Type: {alert_data['call'].get('type', 'Unknown')}",
            f"  Priority: {alert_data['call'].get('priority', 'Unknown')}",
            f"  Notes: {alert_data['call'].get('notes', 'No notes')}"
        ])

    # Add units information
    if 'units' in alert_data:
        output.extend([
            "\nUnits:",
            *[f"  - {unit}" for unit in alert_data['units'].split(' ')]
        ])

    # Add any additional information
    if 'additional_info' in alert_data:
        output.extend([
            "\nAdditional Information:",
            *[f"  {k}: {v}" for k, v in alert_data['additional_info'].items()]
        ])

    output.append(f"{'='*80}\n")
    return '\n'.join(output)


async def alert_handler(alert_data: Dict[str, Any]) -> None:
    """Handle incoming alerts by formatting and displaying them.

    Args:
        alert_data: Alert data dictionary
    """
    # for key, value in alert_data.items():
    #     print(f"\t - {key}: {value}")
    # alert = Active911Alert(**alert_data)
    try:
        alert = Active911Alert(**alert_data)
        print("="*80)
        print(f"Alert units: {alert_data['units']}")
        alert_json = alert.to_json()
        print(json.dumps(json.loads(alert_json), indent=2))
    except Exception as e:
        self.logger(f'Error: {e}')


async def main() -> None:
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description='Active911 Alert Monitor',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'device_code',
        help='Active911 device code'
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level'
    )
    args = parser.parse_args()

    # Set up logging
    logger = setup_logging(args.log_level)

    try:
        # Create and configure client
        client = Active911Client(
            device_code=args.device_code,
            logger=logger
        )
        client.alert_handler = alert_handler

        # Connect and start monitoring
        logger.info(f"Connecting to Active911 with device code: {args.device_code}")
        await client.register_device()
        await client.authenticate()
        await client.active911_xmpp()

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())

