import asyncio
import json
import logging
from typing import Optional, Any, Callable, Dict

import aiohttp

from a911client import (
    Active911Config,
    Active911Error,
    Active911ConnectionError,
    Active911AuthenticationError,
    Active911Xmpp,
)


class Active911Client:
    """Client for interacting with the Active911 API and XMPP service.

    This client handles authentication, device registration, and alert processing
    for the Active911 service. It supports both API and XMPP-based communication.

    To receive alerts, set the alert_handler attribute to an async function that
    takes a single argument (alert_data). For example:

    ```python
    async def my_alert_handler(alert_data):
        print(f"Received alert: {alert_data}")

    client = Active911Client(device_code="your-device-code")
    client.alert_handler = my_alert_handler
    ```

    The alert_handler will be called for:
    - Individual alerts received via XMPP
    - Alerts fetched via fetch_alert()
    - Alerts received during bulk fetch via fetch_all_alerts()
    """

    def __init__(self, device_code: str, logger: Optional[logging.Logger] = None) -> None:
        """Initialize the Active911 client.

        Args:
            device_code: The device code for authentication
            logger: Optional logger instance
        """
        # Set up logger
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

        self.device_code = device_code
        self.session: Optional[aiohttp.ClientSession] = None
        self.user_id: Optional[str] = None
        self.device_id: Optional[str] = None
        self.registration_code: Optional[str] = None
        self.is_registered: bool = False
        self.is_authenticated: bool = False
        self.agencies: list = []
        self.session = aiohttp.ClientSession()

    async def __aenter__(self) -> 'Active911Client':
        """Initialize client session when entering async context."""
        self.logger.info("Initializing Active911 client session")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Clean up resources when exiting async context."""
        try:
            if self.session:
                self.logger.info("Closing Active911 client session")
                await self.session.close()
                self.session = None
            self.is_authenticated = False
            self.is_registered = False
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
            # Ensure session is None even if close fails
            self.session = None

    async def post_request(self, data: Optional[dict] = None) -> dict:
        """Make a POST request to the Active911 API.

        Args:
            data: The data to send in the POST request

        Returns:
            The JSON response from the API

        Raises:
            Active911AuthenticationError: If authentication fails
            Active911Error: If the API request fails
            Active911ConnectionError: If there's a connection error
        """
        try:
            self.logger.info(
                f"Making POST request to {Active911Config.access_uri} "
                f"for {data['operation']}"
            )
            async with self.session.post(
                Active911Config.access_uri, data=data
            ) as response:
                result = await response.json()
                if result["result"] == "success":
                    self.logger.info(
                        f"POST request to {Active911Config.access_uri} "
                        f"for {data['operation']} successful"
                    )
                    return result
                else:
                    if result["message"] == "Unauthorized":
                        self.logger.error(
                            f"Authentication failed: {result['message']}"
                        )
                        raise Active911AuthenticationError(
                            f"API Error: {result['message']}"
                        )
                    else:
                        self.logger.error(
                            f"Registration failed: {result['message']}"
                        )
                        raise Active911Error(
                            f"API Error: {result['message']}"
                        )
        except Exception as e:
            self.logger.error(f"Connection error during registration: {str(e)}")
            await self.session.close()
            raise Active911ConnectionError(f"Connection error: {str(e)}")

    async def register_device(self) -> None:
        """Register the device with the Active911 API.

        Raises:
            Active911ConnectionError: If there's a connection error
        """
        try:
            self.logger.info(f"Registering device with code: {self.device_code}")
            request_data = {
                "operation": "register",
                "device_code": self.device_code
            }
            data = await self.post_request(request_data)
            self.logger.info("Device registration successful")
            self.is_registered = True
        except Exception as e:
            self.logger.error(f"Connection error during registration: {str(e)}")
            raise Active911ConnectionError(f"Connection error: {str(e)}")

    async def authenticate(self) -> None:
        """Authenticate with the Active911 API.

        Raises:
            Active911ConnectionError: If there's a connection error
        """
        try:
            self.logger.info("Authenticating with Active911 API")
            request_data = {
                "operation": "init",
                "client_version": f"WebView v{Active911Config.client_version}",
                "limit_to_five_responses": 0
            }
            data = await self.post_request(request_data)
            if data.get("message", {}).get("device", {}).get("info"):
                self.user_id = data["message"]["device"]["info"]["user_id"]
                self.device_id = data["message"]["device"]["info"]["device_id"]
                self.registration_code = data["message"]["device"]["info"]["registration_code"]
                self.is_authenticated = True
                self.logger.info(
                    f"Authentication successful for device ID: {self.device_id}"
                )
        except Exception as e:
            self.logger.error(f"Connection error during authentication: {str(e)}")
            raise Active911ConnectionError(f"Connection error: {str(e)}")

    async def fetch_alert(self, message_id: str) -> None:
        """Fetch an alert from the Active911 API.

        Args:
            message_id: The ID of the message to fetch

        Raises:
            Active911ConnectionError: If there's a connection error
        """
        try:
            self.logger.debug(f"Fetching alert for message ID: {message_id}")
            request_data = {
                "operation": "fetch_alert",
                "message_id": message_id
            }
            data = await self.post_request(request_data)
            self.logger.debug(
                f"Successfully fetched alert for message ID: {message_id}"
            )
            if hasattr(self, 'alert_handler'):
                await self.alert_handler(data["message"])
        except Exception as e:
            self.logger.error(f"Connection error while fetching alert: {str(e)}")
            raise Active911ConnectionError(f"Connection error: {str(e)}")

    async def fetch_all_alerts(self) -> None:
        """Fetch all alerts from the Active911 API.

        Raises:
            Active911ConnectionError: If there's a connection error
        """
        try:
            self.logger.debug("Fetching all alerts")
            request_data = {
                "operation": "bulk_fetch_alerts"
            }
            data = await self.post_request(request_data)
            self.logger.debug("Successfully fetched all alerts")
            for alert in data["message"]:
                self.logger.info(f"Bulk alert: {alert}")
                if hasattr(self, 'alert_handler'):
                    alert_obj = json.loads(alert) if isinstance(alert, str) else alert
                    await self.alert_handler(alert_obj)
        except Exception as e:
            self.logger.error(f"Connection error while fetching alert: {str(e)}")
            raise Active911ConnectionError(f"Connection error: {str(e)}")

    async def message_handler(self, message_data: dict) -> None:
        """Handle incoming XMPP messages.

        Args:
            message_data: The message data received from XMPP
        """
        self.logger.info(f"Processing message: {message_data}")
        await self.fetch_alert(message_data['message_id'])

    async def active911_xmpp(self) -> None:
        """Connect to the XMPP server and start the message handler.

        Raises:
            Active911ConnectionError: If there's a connection error
        """
        try:
            self.logger.info("Initializing XMPP connection")
            xmpp = Active911Xmpp({
                "device_id": self.device_id,
                "registration_code": self.registration_code
            }, logger=self.logger)

            xmpp.message_handler = self.message_handler
            xmpp.connected_handler = self.fetch_all_alerts
            
            # Set up error handler
            async def error_handler(error: Any) -> None:
                self.logger.error(f"XMPP error occurred: {error}")
                # Don't re-raise the error, just log it
                
            xmpp.error_handler = error_handler
            
            # Set up disconnected handler
            async def disconnected_handler() -> None:
                self.logger.warning(
                    "XMPP connection lost, attempting to reconnect..."
                )
                # Don't re-raise the error, let the reconnection logic handle it
                
            xmpp.disconnected_handler = disconnected_handler

            while True:  # Keep trying to maintain connection
                try:
                    await xmpp.run()
                    # Wait for XMPP connection to be established
                    while not xmpp.connected:
                        await asyncio.sleep(0.1)
                    self.logger.info("XMPP connection established")
                    # Keep connection alive until disconnected
                    while xmpp.connected:
                        await asyncio.sleep(1)
                except Active911ConnectionError as e:
                    self.logger.error(f"XMPP connection error: {str(e)}")
                    # Wait before retrying
                    await asyncio.sleep(5)
                    continue
                except Exception as e:
                    self.logger.error(
                        f"Unexpected error in XMPP connection: {str(e)}"
                    )
                    # Wait before retrying
                    await asyncio.sleep(5)
                    continue
        except Exception as e:
            self.logger.error(f"Fatal XMPP error: {str(e)}")
            raise Active911ConnectionError(f"Fatal connection error: {str(e)}")


def main() -> None:
    pass

if __name__ == "__main__":
    main()