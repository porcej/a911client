import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass()
class PageGroup:
    """Represents a page group in an Active911 alert."""
    id: str = ""

    def to_dict(self) -> Dict[str, str]:
        """Convert the page group to a dictionary."""
        return {"id": self.id}

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'PageGroup':
        """Create a PageGroup instance from a dictionary."""
        return cls(id=data.get("id", ""))


@dataclass()
class Active911Alert:
    """Represents an Active911 alert with all its associated data.
    
    This class handles the conversion between JSON and Python objects,
    and provides sorting capabilities based on timestamp.
    
    All fields are optional and will default to empty values if not provided.
    
    Attributes:
        address: The address of the incident
        age: Age of the alert in minutes
        agency_id: ID of the responding agency
        agency_name: Name of the responding agency
        cad_code: CAD system code
        city: City where the incident occurred
        cross_street: Nearest cross street
        description: Description of the incident
        details: Additional details about the incident
        id: Unique identifier for the alert
        lat: Latitude of the incident
        lon: Longitude of the incident
        map_code: Map code for the incident
        pagegroups: List of page groups associated with the alert
        place: Place name (if applicable)
        priority: Priority level of the incident
        response_vocabulary: Response vocabulary options
        source: Source of the alert
        state: State where the incident occurred
        timestamp: Unix timestamp of when the alert was created
        unit: Primary responding unit
        units: List of responding units
    """
    
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

    def __post_init__(self):
        """Convert response_vocabulary from string to list if needed and handle empty values."""
        # Handle response_vocabulary
        if isinstance(self.response_vocabulary, str):
            try:
                self.response_vocabulary = json.loads(self.response_vocabulary)
            except json.JSONDecodeError:
                self.response_vocabulary = []
        elif self.response_vocabulary is None:
            self.response_vocabulary = []

        # Handle pagegroups
        if self.pagegroups is None:
            self.pagegroups = []
        elif isinstance(self.pagegroups, list):
            self.pagegroups = [
                PageGroup.from_dict(pg) if isinstance(pg, dict) else pg
                for pg in self.pagegroups
            ]

        # Handle units
        if isinstance(self.units, str):
            self.units = [unit.strip() for unit in self.units.split() if unit.strip()]
        elif self.units is None:
            self.units = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert the alert to a dictionary.
        
        Returns:
            Dictionary representation of the alert
        """
        data = asdict(self)
        data['pagegroups'] = [pg.to_dict() for pg in self.pagegroups]
        data['response_vocabulary'] = json.dumps(self.response_vocabulary)
        return data

    def to_json(self) -> str:
        """Convert the alert to a JSON string.
        
        Returns:
            JSON string representation of the alert
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Active911Alert':
        """Create an Active911Alert instance from a dictionary.
        
        Args:
            data: Dictionary containing alert data
            
        Returns:
            Active911Alert instance
        """
        # Filter out None values to use defaults
        filtered_data = {k: v for k, v in data.items() if v is not None}
        return cls(**filtered_data)

    @classmethod
    def from_json(cls, json_str: str) -> 'Active911Alert':
        """Create an Active911Alert instance from a JSON string.
        
        Args:
            json_str: JSON string containing alert data
            
        Returns:
            Active911Alert instance
        """
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError:
            return cls()  # Return empty alert if JSON is invalid

    def get_datetime(self) -> datetime:
        """Get the alert timestamp as a datetime object.
        
        Returns:
            datetime object representing the alert timestamp
        """
        return datetime.fromtimestamp(self.timestamp)

    def __lt__(self, other: 'Active911Alert') -> bool:
        """Compare alerts based on timestamp for sorting.
        
        Args:
            other: Another Active911Alert instance
            
        Returns:
            True if this alert's timestamp is less than the other's
        """
        return self.timestamp < other.timestamp

    def __eq__(self, other: 'Active911Alert') -> bool:
        """Compare alerts for equality based on ID.
        
        Args:
            other: Another Active911Alert instance
            
        Returns:
            True if the alerts have the same ID
        """
        if not isinstance(other, Active911Alert):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Generate a hash based on the alert ID.
        
        Returns:
            Hash value for the alert
        """
        return hash(self.id)
