"""
Pydantic schemas for park domain.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, conint

from app.domain.parks.models.park import ParkType, ParkStatus


class FeatureBase(BaseModel):
    """Base schema for Feature."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    icon_url: Optional[str] = None


class FeatureCreate(FeatureBase):
    """Schema for creating a new Feature."""

    pass


class FeatureUpdate(FeatureBase):
    """Schema for updating a Feature."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)


class Feature(FeatureBase):
    """Schema for Feature response."""

    id: int

    class Config:
        from_attributes = True


class ParkPhotoBase(BaseModel):
    """Base schema for ParkPhoto."""

    url: str
    caption: Optional[str] = None
    is_primary: bool = False


class ParkPhotoCreate(ParkPhotoBase):
    """Schema for creating a new ParkPhoto."""

    park_id: int


class ParkPhotoUpdate(ParkPhotoBase):
    """Schema for updating a ParkPhoto."""

    url: Optional[str] = None
    is_primary: Optional[bool] = None


class ParkPhoto(ParkPhotoBase):
    """Schema for ParkPhoto response."""

    id: int
    park_id: int
    uploaded_by: Optional[int] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


class ParkRatingBase(BaseModel):
    """Base schema for ParkRating."""

    rating: conint(ge=1, le=5) = Field(..., description="Rating from 1 to 5 stars")
    review: Optional[str] = None


class ParkRatingCreate(ParkRatingBase):
    """Schema for creating a new ParkRating."""

    park_id: int


class ParkRatingUpdate(ParkRatingBase):
    """Schema for updating a ParkRating."""

    rating: Optional[conint(ge=1, le=5)] = None


class ParkRating(ParkRatingBase):
    """Schema for ParkRating response."""

    id: int
    park_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ParkBase(BaseModel):
    """Base schema for Park."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    park_type: ParkType
    status: ParkStatus = ParkStatus.ACTIVE

    # Location
    address: Optional[str] = None
    city: str
    state: Optional[str] = None
    country: str
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Additional Information
    is_free: bool = True
    opening_hours: Optional[Dict[str, Any]] = None
    website_url: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None

    # Tags
    tags: Optional[List[str]] = None


class ParkCreate(ParkBase):
    """Schema for creating a new Park."""

    feature_ids: Optional[List[int]] = None


class ParkUpdate(BaseModel):
    """Schema for updating a Park."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    park_type: Optional[ParkType] = None
    status: Optional[ParkStatus] = None

    # Location
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Additional Information
    is_free: Optional[bool] = None
    opening_hours: Optional[Dict[str, Any]] = None
    website_url: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None

    # Tags
    tags: Optional[List[str]] = None

    # Features
    feature_ids: Optional[List[int]] = None


class Park(ParkBase):
    """Schema for Park response."""

    id: int
    created_at: datetime
    updated_at: datetime
    features: List[Feature] = []
    average_rating: Optional[float] = None

    class Config:
        from_attributes = True


class ParkDetail(Park):
    """Schema for detailed Park response."""

    photos: List[ParkPhoto] = []
    ratings: List[ParkRating] = []


class ParkList(BaseModel):
    """Schema for paginated list of parks."""

    items: List[Park]
    total: int
    page: int
    page_size: int
    pages: int


class ParkSearch(BaseModel):
    """Schema for park search parameters."""

    query: Optional[str] = None
    park_type: Optional[ParkType] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    is_free: Optional[bool] = None
    features: Optional[List[int]] = None
    min_rating: Optional[conint(ge=1, le=5)] = None
    status: Optional[ParkStatus] = None
    tags: Optional[List[str]] = None
