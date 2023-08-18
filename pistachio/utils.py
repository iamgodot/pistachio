from random import choice
from string import ascii_letters, digits

from passlib.hash import bcrypt


# FIXME: seems slow
def hash_password(password: str) -> str:
    return bcrypt.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.verify(password, hashed)


def generate_alnum(k: int):
    """Generate an alpha-numeric string of length k."""
    return "".join(choice(ascii_letters + digits) for _ in range(k))


if __name__ == "__main__":
    p1 = hash_password("foo")
    p2 = hash_password("bar")
    print(len(p1), len(p2))
    r1 = verify_password("foo", p1)
    r2 = verify_password("bar", p1)
    print(r1, r2)
