# Parks Domain

This domain handles all functionality related to skate parks, including park information, features, photos, and ratings.

## Models

### Park

Represents a skate park location with detailed information.

**Fields:**
- `id`: Unique identifier
- `name`: Name of the skate park
- `description`: Detailed description
- `park_type`: Type of park (street, vert, bowl, plaza, diy, indoor, hybrid)
- `status`: Current status (active, closed_temporarily, closed_permanently, under_construction, planned)
- `address`: Street address
- `city`: City where the park is located
- `state`: State/province
- `country`: Country
- `postal_code`: Postal/ZIP code
- `latitude`: Geographic latitude
- `longitude`: Geographic longitude
- `is_free`: Whether the park is free to use
- `opening_hours`: JSON object with opening hours
- `website_url`: URL to the park's official website
- `phone_number`: Contact phone number
- `email`: Contact email address
- `created_at`: When the park entry was created
- `updated_at`: When the park entry was last updated
- `tags`: Array of tags for searchability
- `features`: List of features available at the park (many-to-many relationship)
- `photos`: List of photos of the park (one-to-many relationship)
- `ratings`: List of user ratings for the park (one-to-many relationship)

### Feature

Represents features that can be present in skate parks (e.g., rails, stairs, ledges, bowls, half-pipes).

**Fields:**
- `id`: Unique identifier
- `name`: Name of the feature
- `description`: Description of the feature
- `icon_url`: URL to an icon representing the feature
- `parks`: List of parks that have this feature (many-to-many relationship)

### ParkPhoto

Represents photos of skate parks.

**Fields:**
- `id`: Unique identifier
- `park_id`: ID of the park
- `url`: URL to the photo
- `caption`: Optional caption for the photo
- `is_primary`: Whether this is the primary photo for the park
- `uploaded_by`: ID of the user who uploaded the photo
- `uploaded_at`: When the photo was uploaded

### ParkRating

Represents user ratings for skate parks.

**Fields:**
- `id`: Unique identifier
- `park_id`: ID of the park
- `user_id`: ID of the user who submitted the rating
- `rating`: Rating value (1-5 stars)
- `review`: Optional review text
- `created_at`: When the rating was created
- `updated_at`: When the rating was last updated

## API Endpoints

### Parks

- `GET /api/v1/parks`: List all parks with optional filtering
- `GET /api/v1/parks/{park_id}`: Get detailed information about a specific park
- `POST /api/v1/parks`: Create a new park (requires moderator or admin role)
- `PUT /api/v1/parks/{park_id}`: Update an existing park (requires moderator or admin role)
- `DELETE /api/v1/parks/{park_id}`: Delete a park (requires admin role)
- `POST /api/v1/parks/{park_id}/ratings`: Rate a park (requires authentication)

### Features

- `GET /api/v1/features`: List all available features
- `GET /api/v1/features/{feature_id}`: Get information about a specific feature
- `POST /api/v1/features`: Create a new feature (requires moderator or admin role)
- `PUT /api/v1/features/{feature_id}`: Update an existing feature (requires moderator or admin role)
- `DELETE /api/v1/features/{feature_id}`: Delete a feature (requires admin role)

## Services

The `ParkService` provides the following functionality:
- Get parks by ID or with filtering and pagination
- Create, update, and delete parks
- Manage park features
- Add ratings to parks

## Repositories

The `ParkRepository` handles database operations for parks, features, photos, and ratings.
