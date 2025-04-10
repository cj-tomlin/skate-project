"""
Service for park domain.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone

from app.domain.parks.models.park import Park, Feature, ParkRating
from app.domain.parks.repositories.park_repository import ParkRepository
from app.domain.parks.schemas.park import (
    ParkCreate,
    ParkUpdate,
    FeatureCreate,
    FeatureUpdate,
)


class ParkService:
    """
    Service for park-related operations.
    """

    def __init__(self, repository: ParkRepository):
        """
        Initialize the service with a repository.

        Args:
            repository: Park repository
        """
        self.repository = repository

    async def get_park_by_id(self, park_id: int) -> Optional[Park]:
        """
        Get a park by ID.

        Args:
            park_id: ID of the park to retrieve

        Returns:
            Park object or None if not found
        """
        return await self.repository.get_by_id(park_id)

    async def get_parks(
        self, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Park], int]:
        """
        Get all parks with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of Park objects, total count)
        """
        parks = await self.repository.get_all(skip=skip, limit=limit)
        total = await self.repository.count()
        return parks, total

    async def search_parks(
        self, filters: Optional[Dict[str, Any]] = None, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Park], int]:
        """
        Search parks with filters and pagination.

        Args:
            filters: Dictionary of filter conditions
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of Park objects, total count)
        """
        return await self.repository.search(filters=filters, skip=skip, limit=limit)

    async def create_park(self, park_data: ParkCreate) -> Park:
        """
        Create a new park.

        Args:
            park_data: Park creation data

        Returns:
            Created Park object
        """
        # Extract feature IDs
        feature_ids = park_data.feature_ids or []

        # Create park object
        park = Park(
            name=park_data.name,
            description=park_data.description,
            park_type=park_data.park_type,
            status=park_data.status,
            address=park_data.address,
            city=park_data.city,
            state=park_data.state,
            country=park_data.country,
            postal_code=park_data.postal_code,
            latitude=park_data.latitude,
            longitude=park_data.longitude,
            is_free=park_data.is_free,
            opening_hours=park_data.opening_hours,
            website_url=park_data.website_url,
            phone_number=park_data.phone_number,
            email=park_data.email,
            tags=park_data.tags,
        )

        # Create the park
        created_park = await self.repository.create(park)

        # Add features if provided
        if feature_ids:
            await self.repository.add_features(created_park, feature_ids)

        return created_park

    async def update_park(self, park_id: int, park_data: ParkUpdate) -> Optional[Park]:
        """
        Update an existing park.

        Args:
            park_id: ID of the park to update
            park_data: Park update data

        Returns:
            Updated Park object or None if not found
        """
        # Get the park
        park = await self.repository.get_by_id(park_id)
        if not park:
            return None

        # Update park fields
        if park_data.name is not None:
            park.name = park_data.name
        if park_data.description is not None:
            park.description = park_data.description
        if park_data.park_type is not None:
            park.park_type = park_data.park_type
        if park_data.status is not None:
            park.status = park_data.status
        if park_data.address is not None:
            park.address = park_data.address
        if park_data.city is not None:
            park.city = park_data.city
        if park_data.state is not None:
            park.state = park_data.state
        if park_data.country is not None:
            park.country = park_data.country
        if park_data.postal_code is not None:
            park.postal_code = park_data.postal_code
        if park_data.latitude is not None:
            park.latitude = park_data.latitude
        if park_data.longitude is not None:
            park.longitude = park_data.longitude
        if park_data.is_free is not None:
            park.is_free = park_data.is_free
        if park_data.opening_hours is not None:
            park.opening_hours = park_data.opening_hours
        if park_data.website_url is not None:
            park.website_url = park_data.website_url
        if park_data.phone_number is not None:
            park.phone_number = park_data.phone_number
        if park_data.email is not None:
            park.email = park_data.email
        if park_data.tags is not None:
            park.tags = park_data.tags

        # Update the park
        updated_park = await self.repository.update(park)

        # Update features if provided
        if park_data.feature_ids is not None:
            # Remove all existing features
            existing_feature_ids = [feature.id for feature in park.features]
            if existing_feature_ids:
                await self.repository.remove_features(
                    updated_park, existing_feature_ids
                )

            # Add new features
            if park_data.feature_ids:
                await self.repository.add_features(updated_park, park_data.feature_ids)

        return updated_park

    async def delete_park(self, park_id: int) -> bool:
        """
        Delete a park.

        Args:
            park_id: ID of the park to delete

        Returns:
            True if successful, False if not found
        """
        park = await self.repository.get_by_id(park_id)
        if not park:
            return False

        return await self.repository.delete(park)

    async def get_feature_by_id(self, feature_id: int) -> Optional[Feature]:
        """
        Get a feature by ID.

        Args:
            feature_id: ID of the feature to retrieve

        Returns:
            Feature object or None if not found
        """
        return await self.repository.get_feature_by_id(feature_id)

    async def get_all_features(self) -> List[Feature]:
        """
        Get all features.

        Returns:
            List of Feature objects
        """
        return await self.repository.get_all_features()

    async def create_feature(self, feature_data: FeatureCreate) -> Feature:
        """
        Create a new feature.

        Args:
            feature_data: Feature creation data

        Returns:
            Created Feature object
        """
        feature = Feature(
            name=feature_data.name,
            description=feature_data.description,
            icon_url=feature_data.icon_url,
        )

        return await self.repository.create_feature(feature)

    async def update_feature(
        self, feature_id: int, feature_data: FeatureUpdate
    ) -> Optional[Feature]:
        """
        Update an existing feature.

        Args:
            feature_id: ID of the feature to update
            feature_data: Feature update data

        Returns:
            Updated Feature object or None if not found
        """
        feature = await self.repository.get_feature_by_id(feature_id)
        if not feature:
            return None

        if feature_data.name is not None:
            feature.name = feature_data.name
        if feature_data.description is not None:
            feature.description = feature_data.description
        if feature_data.icon_url is not None:
            feature.icon_url = feature_data.icon_url

        return await self.repository.update_feature(feature)

    async def delete_feature(self, feature_id: int) -> bool:
        """
        Delete a feature.

        Args:
            feature_id: ID of the feature to delete

        Returns:
            True if successful, False if not found
        """
        feature = await self.repository.get_feature_by_id(feature_id)
        if not feature:
            return False

        return await self.repository.delete_feature(feature)

    async def add_park_rating(
        self, park_id: int, user_id: int, rating: int, review: Optional[str] = None
    ) -> Optional[ParkRating]:
        """
        Add a rating to a park.

        Args:
            park_id: ID of the park
            user_id: ID of the user adding the rating
            rating: Rating value (1-5)
            review: Optional review text

        Returns:
            Created ParkRating object or None if park not found
        """
        park = await self.repository.get_by_id(park_id)
        if not park:
            return None

        # Check if user has already rated this park
        existing_rating = next((r for r in park.ratings if r.user_id == user_id), None)

        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating
            existing_rating.review = review
            existing_rating.updated_at = datetime.now(timezone.utc)
            await self.repository.update(park)
            return existing_rating
        else:
            # Create new rating
            new_rating = ParkRating(
                park_id=park_id, user_id=user_id, rating=rating, review=review
            )
            park.ratings.append(new_rating)
            await self.repository.update(park)
            return new_rating
