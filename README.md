# a911client

A modern Python client library for interacting with Active911's API and XMPP interface. This library provides a robust, type-safe, and async-first approach to handling Active911 alerts and communications.

## Features

- Full support for Active911's API and XMPP interface
- Async/await based architecture for better performance
- Type hints and comprehensive error handling
- Automatic reconnection and connection state management
- JSON serialization/deserialization of alerts
- Configurable logging
- Support for multiple agencies and alert types
- Rich alert data model with sorting and comparison capabilities
- Context manager support for proper resource cleanup
- Comprehensive exception handling

## Requirements

- Python 3.6+
- aiohttp>=3.12.13
- slixmpp>=1.10.0
- requests>=2.31.0
- urllib3>=2.1.0
- typing-extensions>=4.9.0
- python-dateutil>=2.8.2

## Installation

```bash
# Install from PyPI
pip install a911client

# Or install from GitHub
pip install git+https://github.com/porcej/a911client
```

## Quick Start

```python
import asyncio
import logging
from a911client import Active911Client, Active911Alert

async def alert_handler(alert_data):
    """Handle incoming alerts."""
    # Convert raw alert data to Active911Alert object
    alert = Active911Alert.from_dict(alert_data)
    print(f"Received alert: {alert.description}")
    print(f"Location: {alert.address}, {alert.city}, {alert.state}")
    print(f"Responding units: {', '.join(alert.units)}")

async def main():
    # Initialize the client
    client = Active911Client(device_code="your-device-code")
    
    # Set up alert handler
    client.alert_handler = alert_handler
    
    # Connect and start processing alerts
    async with client:
        await client.register_device()
        await client.authenticate()
        await client.active911_xmpp()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
```

## Advanced Usage

### Alert Handling

The `Active911Alert` class provides a rich interface for working with alerts:

```python
# Create an alert from JSON
alert = Active911Alert.from_json(json_string)

# Create an alert from dictionary
alert = Active911Alert.from_dict(alert_dict)

# Access alert properties
print(f"Alert ID: {alert.id}")
print(f"Address: {alert.address}")
print(f"Responding Units: {', '.join(alert.units)}")
print(f"Timestamp: {alert.get_datetime()}")

# Convert alert to JSON
json_data = alert.to_json()

# Convert alert to dictionary
alert_dict = alert.to_dict()

# Sort alerts by timestamp
alerts = [alert1, alert2, alert3]
sorted_alerts = sorted(alerts)

# Compare alerts
if alert1 == alert2:
    print("Same alert")
```

### Error Handling

The library provides specific exception types for different error scenarios:

```python
from a911client import (
    Active911Error,
    Active911ConnectionError,
    Active911AuthenticationError
)

try:
    await client.authenticate()
except Active911AuthenticationError as e:
    print(f"Authentication failed: {e}")
except Active911ConnectionError as e:
    print(f"Connection error: {e}")
```

### Configuration

The client can be configured with various options:

```python
import logging

# Create a custom logger
logger = logging.getLogger("my_app")
logger.setLevel(logging.INFO)

client = Active911Client(
    device_code="your-device-code",
    logger=logger
)
```

### Context Manager Usage

The client supports context manager usage for proper resource cleanup:

```python
async with Active911Client(device_code="your-device-code") as client:
    client.alert_handler = my_alert_handler
    await client.register_device()
    await client.authenticate()
    await client.active911_xmpp()
# Session is automatically closed when exiting the context
```

## API Reference

### Active911Client

The main client class for interacting with Active911.

```python
class Active911Client:
    def __init__(self, device_code: str, logger: Optional[logging.Logger] = None)
    async def __aenter__() -> 'Active911Client'
    async def __aexit__(exc_type, exc_val, exc_tb) -> None
    async def register_device() -> None
    async def authenticate() -> None
    async def fetch_alert(message_id: str) -> None
    async def fetch_all_alerts() -> None
    async def active911_xmpp() -> None
    async def post_request(data: Optional[dict] = None) -> dict
    async def message_handler(message_data: dict) -> None
```

**Properties:**
- `device_code`: The device code for authentication
- `session`: aiohttp ClientSession instance
- `user_id`: Authenticated user ID
- `device_id`: Registered device ID
- `registration_code`: Device registration code
- `is_registered`: Boolean indicating if device is registered
- `is_authenticated`: Boolean indicating if client is authenticated
- `agencies`: List of associated agencies
- `alert_handler`: Callable for handling incoming alerts

### Active911Alert

A dataclass representing an Active911 alert with comprehensive data handling.

```python
@dataclass
class Active911Alert:
    address: str = ""
    age: int = 0
    agency_id: int = 0
    agency_name: str = ""
    cad_code: str = ""
    city: str = ""
    cross_street: str = ""
    description: str = ""
    details: str = ""
    id: int = 0
    lat: float = 0.0
    lon: float = 0.0
    map_code: str = ""
    pagegroups: List[PageGroup] = field(default_factory=list)
    place: str = ""
    priority: str = ""
    response_vocabulary: List[str] = field(default_factory=list)
    source: str = ""
    state: str = ""
    timestamp: int = 0
    unit: str = ""
    units: List[str] = field(default_factory=list)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Active911Alert'
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Active911Alert'
    def to_json(self) -> str
    def to_dict(self) -> Dict[str, Any]
    def get_datetime(self) -> datetime
    def __lt__(self, other: 'Active911Alert') -> bool
    def __eq__(self, other: 'Active911Alert') -> bool
    def __hash__(self) -> int
```

### Active911Xmpp

XMPP client for real-time alert processing.

```python
class Active911Xmpp(slixmpp.ClientXMPP):
    def __init__(self, param: Dict[str, Any], logger: Optional[logging.Logger] = None)
    async def run(self, callback: Optional[Callable] = None) -> None
    async def try_reconnect(self) -> None
```

### Active911Config

Configuration settings for the Active911 client.

```python
@dataclass
class Active911Config:
    access_uri: ClassVar[str] = "https://access.active911.com/web_api.php"
    xmpp_server: ClassVar[str] = "push.active911.com"
    # ... other configuration settings
    
    @classmethod
    def register_url(cls, device_code: str) -> str
    @classmethod
    def xmpp_uri(cls) -> str
    @classmethod
    def initialization_uri(cls) -> str
```

### Exceptions

The library provides specific exception types:

```python
class Active911Error(Exception):  # Base exception
class Active911ConnectionError(Active911Error):  # Connection issues
class Active911AuthenticationError(Active911Error):  # Authentication failures
```

## Sample Application

The project includes a sample application (`sample.py`) that demonstrates how to use the library:

```bash
# Run the sample application
python sample.py YOUR_DEVICE_CODE --log-level INFO
```

The sample application:
- Connects to Active911 using your device code
- Displays incoming alerts in a formatted manner
- Handles errors gracefully
- Supports configurable logging levels

## Version Information

Current version: **0.2.0**

**Recent Updates:**
- Migrated from SleekXMPP to Slixmpp for better async support
- Added comprehensive type hints throughout the codebase
- Implemented context manager support for proper resource cleanup
- Enhanced error handling with specific exception types
- Added rich alert data model with sorting and comparison capabilities
- Improved connection management and automatic reconnection
- Added support for bulk alert fetching

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

* **Joseph Porcelli** - *Initial work* - [porcej](https://github.com/porcej)

See also the list of [contributors](https://github.com/porcej/a911client/contributors) who participated in this project.

