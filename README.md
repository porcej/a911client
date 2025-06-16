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

## Requirements

- Python 3.8+
- aiohttp
- slixmpp
- typing-extensions

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

async def alert_handler(alert: Active911Alert):
    """Handle incoming alerts."""
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

# Access alert properties
print(f"Alert ID: {alert.id}")
print(f"Address: {alert.address}")
print(f"Responding Units: {alert.units}")

# Convert alert to JSON
json_data = alert.to_json()

# Sort alerts by timestamp
alerts = [alert1, alert2, alert3]
sorted_alerts = sorted(alerts)
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
client = Active911Client(
    device_code="your-device-code",
    logger=logging.getLogger("my_app")
)
```

## API Reference

### Active911Client

The main client class for interacting with Active911.

```python
class Active911Client:
    def __init__(self, device_code: str, logger: Optional[logging.Logger] = None)
    async def authenticate() -> None
    async def fetch_alert(message_id: str) -> None
    async def fetch_all_alerts() -> None
    async def active911_xmpp() -> None
```

### Active911Alert

A dataclass representing an Active911 alert.

```python
@dataclass
class Active911Alert:
    address: str
    age: int
    agency_id: int
    agency_name: str
    # ... other fields ...
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Active911Alert'
    def to_json(self) -> str
    def get_datetime(self) -> datetime
```

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

