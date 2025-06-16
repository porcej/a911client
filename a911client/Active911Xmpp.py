import asyncio
import logging
import random
import time
from typing import Optional, List, Dict, Any, Callable

import slixmpp
from slixmpp.xmlstream import ElementBase, register_stanza_plugin
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0199 import XEP_0199

from a911client import (
    Active911Config,
    Active911Error,
    Active911ConnectionError,
    Active911AuthenticationError,
)


class Active911Xmpp(slixmpp.ClientXMPP):
    """Wrapper for XMPP functionality specific to Active911 integration.
    
    This class extends slixmpp.ClientXMPP to provide Active911-specific
    functionality including message handling, connection management,
    and room management.

    Args:
        param: Dictionary containing configuration parameters
        logger: Optional logger instance to use for logging

    Attributes:
        logger: Logger instance for logging
        settings: Dictionary containing configuration parameters
        connected: Boolean indicating if the client is connected
        reconnect_attempts: Integer tracking the number of reconnect attempts
        pings: List of pings sent to the server
        plugin: Dictionary containing the plugin instance

    Callbacks:
        error_handler: Optional callback for error messages
        assignment_handler: Optional callback for assignment messages
        message_handler: Optional callback for message messages
        response_handler: Optional callback for response messages
        popup_handler: Optional callback for popup messages
        unknown_command_handler: Optional callback for unknown commands
        connected_handler: Optional callback for connected events
        disconnected_handler: Optional callback for disconnected events
    """
    
    logger: logging.Logger
    
    def __init__(
        self,
        param: Dict[str, Any],
        logger: Optional[logging.Logger] = None
    ) -> None:
        """Initialize the Active911Xmpp client.
        
        Args:
            param: Dictionary containing configuration parameters
            logger: Optional logger instance to use
        """
        # Default settings
        self.settings = {
            "device_id": 0,
            "registration_code": "",
            "server": Active911Config.xmpp_server,
            "port": Active911Config.xmpp_port,
            "domain": Active911Config.xmpp_domain,
            "conference_name": Active911Config.xmpp_conference_name,
            "incoming_callback": lambda msg: None,
            "rooms": [],
            "max_reconnect_attempts": 10,
            "reconnect_delay": 30,
            "keepalive_interval": 10,
            "keepalive_timeout": 5
        }
        self.settings.update(param)

        # Use parent logger if provided, otherwise create a new one
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                handler.setLevel(logging.INFO)
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
        
        # Calculate JID and nick
        jid = f"device{self.settings['device_id']}@{self.settings['domain']}"
        nick = f"{self.settings['device_id']}-{random.randint(0, 9999)}"

        self.connected = False
        self.reconnect_attempts = 0
        
        super().__init__(jid, self.settings['registration_code'])
        
        self.pings = []
        
        # Register plugins
        self.register_plugin('xep_0045')  # Multi-User Chat
        self.register_plugin('xep_0199')  # XMPP Ping
        
        # Register handlers
        self.add_event_handler("connected", self._on_connected)
        self.add_event_handler('session_start', self._on_session_start)
        self.add_event_handler("message", self._on_message)
        self.add_event_handler("disconnected", self._on_disconnected)
        # self.add_event_handler('groupchat_message', self._on_groupchat_message)
        # self.add_event_handler('message', self._on_direct_message)
        # self.add_event_handler('ping_response', self._on_ping_response)

    async def run(self, callback: Optional[Callable] = None) -> None:
        """Run the XMPP client.
        
        Args:
            callback: Optional callback to run after connection
            
        Raises:
            Active911ConnectionError: If connection fails
        """
        try:
            self.connect((
                self.settings['server'],
                int(self.settings['port'])
            ))
            self.logger.info("Successfully connected to Active911 XMPP server")
        except Exception as e:
            self.logger.error(f"Connection error: {str(e)}")
            if hasattr(self, 'error_handler'):
                await self.error_handler(str(e))
            raise Active911ConnectionError(f"Connection error: {str(e)}")

    async def _on_connected(self, event: Any) -> None:
        """Handle connection event.
        
        Args:
            event: Connection event data
        """
        self.logger.info("XMPP connected")
        self.connected = True
        if hasattr(self, 'connected_handler'):
            await self.connected_handler()

    async def _on_disconnected(self, event: Any) -> None:
        """Handle disconnection event.
        
        Args:
            event: Disconnection event data
        """
        self.logger.info("XMPP disconnected")
        self.connected = False
        if hasattr(self, 'disconnected_handler'):
            try:
                await self.disconnected_handler()
            except Exception as e:
                self.logger.error(f"Error in disconnected handler: {str(e)}")
        await self.try_reconnect()
        
    async def _on_session_start(self, event: Any) -> None:
        """Handle session start event.
        
        Args:
            event: Session start event data
        """
        self.send_presence()
        # self.get_roster()
        self.plugin['xep_0199'].enable_keepalive(
            interval=self.settings['keepalive_interval'],
            timeout=self.settings['keepalive_timeout']
        )
        self.logger.info("Session started")
        self.reconnect_attempts = 0

    async def _on_message(self, msg: Any) -> None:
        """Handle incoming messages.
        
        Args:
            msg: Incoming message data
        """
        if msg['type'] in ('chat', 'normal'):
            try:
                message_components = msg['body'].split(':')
                command = message_components[0]
                message_data = {'command': command}

                if command == 'assignment':
                    message_data.update({
                        'device_id': message_components[1],
                        'agency_id': message_components[2],
                        'assignment_id': message_components[3]
                    })
                    if hasattr(self, 'assignment_handler'):
                        await self.assignment_handler(message_data)
                elif command == 'message':
                    message_data.update({
                        'message_id': message_components[1],
                        'alert_id': message_components[2],
                        'sound': message_components[3],
                        'message': message_components[4]
                    })
                    if hasattr(self, 'message_handler'):
                        await self.message_handler(message_data)
                elif command == 'response':
                    message_data.update({
                        'device_id': message_components[1],
                        'action': message_components[2],
                        'alert_id': message_components[3]
                    })
                    if hasattr(self, 'response_handler'):
                        await self.response_handler(message_data)
                elif command == 'popup':
                    message_data.update({
                        'device_id': message_components[1],
                        'message': message_components[2]
                    })
                    if hasattr(self, 'popup_handler'):
                        await self.popup_handler(message_data)
                else:
                    if hasattr(self, 'unknown_command_handler'):
                        await self.unknown_command_handler(message_data)
                    else:
                        self.logger.debug(f"Unknown command: {command}")

            except Exception as e:
                self.logger.error(f"Error processing message: {str(e)}")
        else:
            self.logger.debug(
                f"Message of type {msg['type']} received: {msg['body']}"
            )

    async def try_reconnect(self) -> None:
        """Attempt to reconnect to the XMPP server with exponential backoff."""
        self.reconnect_attempts += 1
        if self.reconnect_attempts > self.settings['max_reconnect_attempts']:
            self.logger.error("Max reconnect attempts reached, stopping reconnect")
            if hasattr(self, 'error_handler'):
                await self.error_handler("Max reconnect attempts reached")
            return

        delay = self.settings['reconnect_delay'] * self.reconnect_attempts
        self.logger.info(f"Attempting reconnect in {delay} seconds...")
        await asyncio.sleep(delay)

        try:
            self.connect((
                self.settings['server'],
                int(self.settings['port'])
            ))
            self.logger.info(
                f"Reconnected to Active911 XMPP server after "
                f"{self.reconnect_attempts} attempts"
            )
        except Exception as e:
            self.logger.error(f"Reconnect attempt failed: {str(e)}")
            if hasattr(self, 'error_handler'):
                await self.error_handler(str(e))
            await self.try_reconnect()
