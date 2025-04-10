"""
Repository for park domain.
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.parks.models.park import Park, Feature


class ParkRepository:
    """
    Repository for park-related database operations.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def get_by_id(
        self, park_id: int, include_features: bool = True
    ) -> Optional[Park]:
        """
        Get a park by ID.

        Args:
            park_id: ID of the park to retrieve
            include_features: Whether to include related features

        Returns:
            Park object or None if not found
        """
        query = select(Park).where(Park.id == park_id)

        if include_features:
            query = query.options(
                selectinload(Park.features),
                selectinload(Park.photos),
                selectinload(Park.ratings),
            )

        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_all(
        self, skip: int = 0, limit: int = 100, include_features: bool = True
    ) -> List[Park]:
        """
        Get all parks with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_features: Whether to include related features

        Returns:
            List of Park objects
        """
        query = select(Park).offset(skip).limit(limit)

        if include_features:
            query = query.options(selectinload(Park.features))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count parks, optionally with filters.

        Args:
            filters: Optional dictionary of filter conditions

        Returns:
            Count of parks
        """
        query = select(func.count(Park.id))

        if filters:
            query = self._apply_filters(query, filters)

        result = await self.session.execute(query)
        return result.scalar()

    async def search(
        self,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
        include_features: bool = True,
    ) -> Tuple[List[Park], int]:
        """
        Search parks with filters and pagination.

        Args:
            filters: Dictionary of filter conditions
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_features: Whether to include related features

        Returns:
            Tuple of (list of Park objects, total count)
        """
        # Build the query
        query = select(Park)

        if filters:
            query = self._apply_filters(query, filters)

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Include related entities if requested
        if include_features:
            query = query.options(selectinload(Park.features))

        # Execute the query
        result = await self.session.execute(query)
        parks = list(result.scalars().all())

        # Get total count
        count_query = select(func.count(Park.id))
        if filters:
            count_query = self._apply_filters(count_query, filters)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        return parks, total

    def _apply_filters(self, query, filters: Dict[str, Any]):
        """
        Apply filters to a query.

        Args:
            query: SQLAlchemy query
            filters: Dictionary of filter conditions

        Returns:
            Updated query with filters applied
        """
        filter_conditions = []

        # Text search
        if "query" in filters and filters["query"]:
            search_term = f"%{filters['query']}%"
            filter_conditions.append(
                or_(
                    Park.name.ilike(search_term),
                    Park.description.ilike(search_term),
                    Park.city.ilike(search_term),
                    Park.address.ilike(search_term),
                )
            )

        # Park type
        if "park_type" in filters and filters["park_type"]:
            filter_conditions.append(Park.park_type == filters["park_type"])

        # Location filters
        if "city" in filters and filters["city"]:
            filter_conditions.append(Park.city.ilike(f"%{filters['city']}%"))

        if "state" in filters and filters["state"]:
            filter_conditions.append(Park.state.ilike(f"%{filters['state']}%"))

        if "country" in filters and filters["country"]:
            filter_conditions.append(Park.country.ilike(f"%{filters['country']}%"))

        # Is free
        if "is_free" in filters and filters["is_free"] is not None:
            filter_conditions.append(Park.is_free == filters["is_free"])

        # Status
        if "status" in filters and filters["status"]:
            filter_conditions.append(Park.status == filters["status"])

        # Tags
        if "tags" in filters and filters["tags"]:
            for tag in filters["tags"]:
                filter_conditions.append(Park.tags.contains([tag]))

        # Features
        if "features" in filters and filters["features"]:
            # This requires a join with the features table
            feature_ids = filters["features"]
            query = query.join(Park.features).filter(Feature.id.in_(feature_ids))

        # Apply all filter conditions
        if filter_conditions:
            query = query.filter(and_(*filter_conditions))

        return query

    async def create(self, park: Park) -> Park:
        """
        Create a new park.

        Args:
            park: Park object to create

        Returns:
            Created Park object
        """
        self.session.add(park)
        await self.session.flush()
        await self.session.refresh(park)
        return park

    async def update(self, park: Park) -> Park:
        """
        Update an existing park.

        Args:
            park: Park object to update

        Returns:
            Updated Park object
        """
        self.session.add(park)
        await self.session.flush()
        await self.session.refresh(park)
        return park

    async def delete(self, park: Park) -> bool:
        """
        Delete a park.

        Args:
            park: Park object to delete

        Returns:
            True if successful
        """
        await self.session.delete(park)
        await self.session.flush()
        return True

    async def add_features(self, park: Park, feature_ids: List[int]) -> Park:
        """
        Add features to a park.

        Args:
            park: Park object
            feature_ids: List of feature IDs to add

        Returns:
            Updated Park object
        """
        # Get the features
        query = select(Feature).where(Feature.id.in_(feature_ids))
        result = await self.session.execute(query)
        features = result.scalars().all()

        # Add features to the park
        for feature in features:
            park.features.append(feature)

        await self.session.flush()
        await self.session.refresh(park)
        return park

    async def remove_features(self, park: Park, feature_ids: List[int]) -> Park:
        """
        Remove features from a park.

        Args:
            park: Park object
            feature_ids: List of feature IDs to remove

        Returns:
            Updated Park object
        """
        # Get the features
        query = select(Feature).where(Feature.id.in_(feature_ids))
        result = await self.session.execute(query)
        features = result.scalars().all()

        # Remove features from the park
        for feature in features:
            if feature in park.features:
                park.features.remove(feature)

        await self.session.flush()
        await self.session.refresh(park)
        return park

    async def get_feature_by_id(self, feature_id: int) -> Optional[Feature]:
        """
        Get a feature by ID.

        Args:
            feature_id: ID of the feature to retrieve

        Returns:
            Feature object or None if not found
        """
        query = select(Feature).where(Feature.id == feature_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_all_features(self) -> List[Feature]:
        """
        Get all features.

        Returns:
            List of Feature objects
        """
        query = select(Feature)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_feature(self, feature: Feature) -> Feature:
        """
        Create a new feature.

        Args:
            feature: Feature object to create

        Returns:
            Created Feature object
        """
        self.session.add(feature)
        await self.session.flush()
        await self.session.refresh(feature)
        return feature

    async def update_feature(self, feature: Feature) -> Feature:
        """
        Update an existing feature.

        Args:
            feature: Feature object to update

        Returns:
            Updated Feature object
        """
        self.session.add(feature)
        await self.session.flush()
        await self.session.refresh(feature)
        return feature

    async def delete_feature(self, feature: Feature) -> bool:
        """
        Delete a feature.

        Args:
            feature: Feature object to delete

        Returns:
            True if successful
        """
        await self.session.delete(feature)
        await self.session.flush()
        return True
