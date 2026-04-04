import secrets

def generate_random_code(length: int = 6) -> str:
    """Generates a random code with a specified length (6 by default)."""
    code = "".join(secrets.choice("0123456789") for _ in range(length)) 
    return code