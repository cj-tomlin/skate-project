"""
Park model representing skate parks.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    ForeignKey,
    DateTime,
    Table,
    Enum as SqlAlchemyEnum,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime, timezone
from typing import List, Optional

from app.infrastructure.database.base import Base


class ParkType(str, Enum):
    """Types of skate parks."""

    STREET = "street"
    VERT = "vert"
    BOWL = "bowl"
    PLAZA = "plaza"
    DIY = "diy"
    INDOOR = "indoor"
    HYBRID = "hybrid"


class ParkStatus(str, Enum):
    """Status of a skate park."""

    ACTIVE = "active"
    CLOSED_TEMPORARILY = "closed_temporarily"
    CLOSED_PERMANENTLY = "closed_permanently"
    UNDER_CONSTRUCTION = "under_construction"
    PLANNED = "planned"


# Association table for park features (many-to-many)
park_features = Table(
    "park_features",
    Base.metadata,
    Column("park_id", Integer, ForeignKey("parks.id"), primary_key=True),
    Column("feature_id", Integer, ForeignKey("features.id"), primary_key=True),
)


class Feature(Base):
    """
    Features that can be present in skate parks.

    Examples: Rails, Stairs, Ledges, Bowls, Half-pipes, etc.
    """

    __tablename__ = "features"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon_url = Column(String(255), nullable=True)

    # Relationships
    parks = relationship("Park", secondary=park_features, back_populates="features")

    def __repr__(self):
        return f"<Feature(id={self.id}, name='{self.name}')>"


class Park(Base):
    """
    Skate park model representing skateboarding locations.

    Attributes:
        id: Unique identifier for the park
        name: Name of the skate park
        description: Detailed description of the park
        park_type: Type of skate park (street, vert, bowl, etc.)
        status: Current status of the park
        address: Street address
        city: City where the park is located
        state: State/province where the park is located
        country: Country where the park is located
        postal_code: Postal/ZIP code
        latitude: Geographic latitude
        longitude: Geographic longitude
        is_free: Whether the park is free to use
        opening_hours: JSON object with opening hours
        website_url: URL to the park's official website
        phone_number: Contact phone number
        email: Contact email address
        created_at: When the park entry was created
        updated_at: When the park entry was last updated
        features: List of features available at the park
        photos: List of photos of the park
        ratings: List of user ratings for the park
    """

    __tablename__ = "parks"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Basic Information
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    park_type = Column(SqlAlchemyEnum(ParkType), nullable=False)
    status = Column(SqlAlchemyEnum(ParkStatus), default=ParkStatus.ACTIVE)

    # Location
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Additional Information
    is_free = Column(Boolean, default=True)
    opening_hours = Column(JSON, nullable=True)
    website_url = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)

    # Metadata
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Tags for searchability
    tags = Column(ARRAY(String), nullable=True)

    # Relationships
    features = relationship("Feature", secondary=park_features, back_populates="parks")
    photos = relationship(
        "ParkPhoto", back_populates="park", cascade="all, delete-orphan"
    )
    ratings = relationship(
        "ParkRating", back_populates="park", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Park(id={self.id}, name='{self.name}', city='{self.city}', country='{self.country}')>"

    @property
    def average_rating(self) -> Optional[float]:
        """Calculate the average rating for this park."""
        if not self.ratings:
            return None
        return sum(rating.rating for rating in self.ratings) / len(self.ratings)

    @property
    def feature_names(self) -> List[str]:
        """Get a list of feature names for this park."""
        return [feature.name for feature in self.features]


class ParkPhoto(Base):
    """
    Photos of skate parks.
    """

    __tablename__ = "park_photos"

    id = Column(Integer, primary_key=True, index=True)
    park_id = Column(Integer, ForeignKey("parks.id"), nullable=False)
    url = Column(String(255), nullable=False)
    caption = Column(String(255), nullable=True)
    is_primary = Column(Boolean, default=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    park = relationship("Park", back_populates="photos")

    def __repr__(self):
        return f"<ParkPhoto(id={self.id}, park_id={self.park_id})>"


class ParkRating(Base):
    """
    User ratings for skate parks.
    """

    __tablename__ = "park_ratings"

    id = Column(Integer, primary_key=True, index=True)
    park_id = Column(Integer, ForeignKey("parks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    park = relationship("Park", back_populates="ratings")

    def __repr__(self):
        return f"<ParkRating(id={self.id}, park_id={self.park_id}, user_id={self.user_id}, rating={self.rating})>"
