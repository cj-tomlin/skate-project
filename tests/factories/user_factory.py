import uuid
import factory
from datetime import datetime, timezone
from factory.fuzzy import FuzzyChoice

from app.domain.users.models.user import User, Role
from app.infrastructure.security.password import hash_password


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Factory for creating User instances for testing.

    Usage:
        # Create a user with default values
        user = UserFactory()

        # Create a user with custom values
        admin_user = UserFactory(
            username="admin",
            email="admin@example.com",
            role=Role.ADMIN
        )

        # Create a batch of users
        users = UserFactory.create_batch(5)
    """

    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    # Generate a unique username
    username = factory.LazyFunction(lambda: f"user_{uuid.uuid4().hex[:8]}")

    # Generate a unique email
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")

    # Hash a default password
    hashed_password = factory.LazyFunction(lambda: hash_password("password123"))

    # Default account status
    is_active = True
    is_verified = False
    two_factor_enabled = False

    # Random role (with higher probability for regular user)
    role = FuzzyChoice(
        [
            Role.USER,
            Role.USER,
            Role.USER,  # Higher probability for USER
            Role.MODERATOR,
            Role.ADMIN,
        ]
    )

    # Timestamps
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    last_login_at = None
    deleted_at = None

    # Profile information
    profile_picture_url = None
    bio = factory.Faker("paragraph", nb_sentences=3)
    settings = {"theme": "light", "notifications": True}

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the _create method to handle the session."""
        session = cls._meta.sqlalchemy_session
        if session is None:
            raise ValueError(
                "No SQLAlchemy session provided for UserFactory. "
                "Set UserFactory._meta.sqlalchemy_session before using the factory."
            )
        return super()._create(model_class, *args, **kwargs)

    @factory.post_generation
    def with_verified_email(self, create, extracted, **kwargs):
        """
        Post-generation hook to create a verified user.

        Usage:
            verified_user = UserFactory(with_verified_email=True)
        """
        if extracted:
            self.is_verified = True

    @factory.post_generation
    def with_admin_role(self, create, extracted, **kwargs):
        """
        Post-generation hook to create an admin user.

        Usage:
            admin_user = UserFactory(with_admin_role=True)
        """
        if extracted:
            self.role = Role.ADMIN
