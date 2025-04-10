"""
API routes for park features.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db_session
from app.infrastructure.security.auth import get_current_active_user
from app.domain.users.models.user import User, Role
from app.domain.parks.schemas.park import Feature, FeatureCreate, FeatureUpdate
from app.domain.parks.services.park_service import ParkService
from app.domain.parks.repositories.park_repository import ParkRepository


router = APIRouter()


async def get_park_service(db: AsyncSession = Depends(get_db_session)) -> ParkService:
    """
    Dependency for getting the park service.

    Args:
        db: Database session

    Returns:
        ParkService instance
    """
    repository = ParkRepository(db)
    return ParkService(repository)


@router.get("", response_model=List[Feature])
async def get_features(park_service: ParkService = Depends(get_park_service)):
    """
    Get a list of all available skate park features.
    """
    return await park_service.get_all_features()


@router.get("/{feature_id}", response_model=Feature)
async def get_feature(
    feature_id: int = Path(..., ge=1, description="ID of the feature to retrieve"),
    park_service: ParkService = Depends(get_park_service),
):
    """
    Get information about a specific skate park feature.
    """
    feature = await park_service.get_feature_by_id(feature_id)
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature with ID {feature_id} not found",
        )
    return feature


@router.post("", response_model=Feature, status_code=status.HTTP_201_CREATED)
async def create_feature(
    feature_data: FeatureCreate,
    current_user: User = Depends(get_current_active_user),
    park_service: ParkService = Depends(get_park_service),
):
    """
    Create a new skate park feature.

    Requires authentication and appropriate permissions.
    """
    # Check if user has permission to create features
    if current_user.role not in [Role.ADMIN, Role.MODERATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create features",
        )

    return await park_service.create_feature(feature_data)


@router.put("/{feature_id}", response_model=Feature)
async def update_feature(
    feature_data: FeatureUpdate,
    feature_id: int = Path(..., ge=1, description="ID of the feature to update"),
    current_user: User = Depends(get_current_active_user),
    park_service: ParkService = Depends(get_park_service),
):
    """
    Update an existing skate park feature.

    Requires authentication and appropriate permissions.
    """
    # Check if user has permission to update features
    if current_user.role not in [Role.ADMIN, Role.MODERATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update features",
        )

    updated_feature = await park_service.update_feature(feature_id, feature_data)
    if not updated_feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature with ID {feature_id} not found",
        )

    return updated_feature


@router.delete("/{feature_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feature(
    feature_id: int = Path(..., ge=1, description="ID of the feature to delete"),
    current_user: User = Depends(get_current_active_user),
    park_service: ParkService = Depends(get_park_service),
):
    """
    Delete a skate park feature.

    Requires authentication and admin permissions.
    """
    # Check if user has permission to delete features
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete features",
        )

    success = await park_service.delete_feature(feature_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature with ID {feature_id} not found",
        )
