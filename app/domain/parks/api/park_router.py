"""
API routes for parks.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db_session
from app.infrastructure.security.auth import get_current_active_user
from app.domain.users.models.user import User, Role
from app.domain.parks.models.park import ParkType, ParkStatus
from app.domain.parks.schemas.park import (
    Park,
    ParkDetail,
    ParkCreate,
    ParkUpdate,
    ParkList,
    ParkRating,
    ParkRatingCreate,
)
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


@router.get("", response_model=ParkList)
async def get_parks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=100, description="Maximum number of records to return"
    ),
    park_type: Optional[ParkType] = Query(None, description="Filter by park type"),
    city: Optional[str] = Query(None, description="Filter by city"),
    country: Optional[str] = Query(None, description="Filter by country"),
    is_free: Optional[bool] = Query(None, description="Filter by free admission"),
    status: Optional[ParkStatus] = Query(None, description="Filter by park status"),
    query: Optional[str] = Query(
        None, description="Search term for name, description, etc."
    ),
    park_service: ParkService = Depends(get_park_service),
):
    """
    Get a list of skate parks with optional filtering.
    """
    # Build filters
    filters = {}
    if park_type:
        filters["park_type"] = park_type
    if city:
        filters["city"] = city
    if country:
        filters["country"] = country
    if is_free is not None:
        filters["is_free"] = is_free
    if status:
        filters["status"] = status
    if query:
        filters["query"] = query

    # Get parks
    parks, total = await park_service.search_parks(
        filters=filters if filters else None, skip=skip, limit=limit
    )

    # Calculate pagination info
    page = skip // limit + 1
    pages = (total + limit - 1) // limit if total > 0 else 1

    return {
        "items": parks,
        "total": total,
        "page": page,
        "page_size": limit,
        "pages": pages,
    }


@router.get("/{park_id}", response_model=ParkDetail)
async def get_park(
    park_id: int = Path(..., ge=1, description="ID of the park to retrieve"),
    park_service: ParkService = Depends(get_park_service),
):
    """
    Get detailed information about a specific skate park.
    """
    park = await park_service.get_park_by_id(park_id)
    if not park:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Park with ID {park_id} not found",
        )
    return park


@router.post("", response_model=Park, status_code=status.HTTP_201_CREATED)
async def create_park(
    park_data: ParkCreate,
    current_user: User = Depends(get_current_active_user),
    park_service: ParkService = Depends(get_park_service),
):
    """
    Create a new skate park.

    Requires authentication.
    """
    # Check if user has permission to create parks
    if current_user.role not in [Role.ADMIN, Role.MODERATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create parks",
        )

    return await park_service.create_park(park_data)


@router.put("/{park_id}", response_model=Park)
async def update_park(
    park_data: ParkUpdate,
    park_id: int = Path(..., ge=1, description="ID of the park to update"),
    current_user: User = Depends(get_current_active_user),
    park_service: ParkService = Depends(get_park_service),
):
    """
    Update an existing skate park.

    Requires authentication and appropriate permissions.
    """
    # Check if user has permission to update parks
    if current_user.role not in [Role.ADMIN, Role.MODERATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update parks",
        )

    updated_park = await park_service.update_park(park_id, park_data)
    if not updated_park:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Park with ID {park_id} not found",
        )

    return updated_park


@router.delete("/{park_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_park(
    park_id: int = Path(..., ge=1, description="ID of the park to delete"),
    current_user: User = Depends(get_current_active_user),
    park_service: ParkService = Depends(get_park_service),
):
    """
    Delete a skate park.

    Requires authentication and admin permissions.
    """
    # Check if user has permission to delete parks
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete parks",
        )

    success = await park_service.delete_park(park_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Park with ID {park_id} not found",
        )


@router.post("/{park_id}/ratings", response_model=ParkRating)
async def rate_park(
    rating_data: ParkRatingCreate,
    park_id: int = Path(..., ge=1, description="ID of the park to rate"),
    current_user: User = Depends(get_current_active_user),
    park_service: ParkService = Depends(get_park_service),
):
    """
    Rate a skate park.

    Requires authentication.
    """
    rating = await park_service.add_park_rating(
        park_id=park_id,
        user_id=current_user.id,
        rating=rating_data.rating,
        review=rating_data.review,
    )

    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Park with ID {park_id} not found",
        )

    return rating
