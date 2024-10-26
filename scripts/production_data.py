import secrets


def generate_secret_key(length=32):
    """Generates a cryptographically secure secret key."""
    return secrets.token_hex(length)


if __name__ == "__main__":
    # Generate a 32-byte (256-bit) secret key
    secret_key = generate_secret_key()
    print(f"Your generated secret key: {secret_key}")
