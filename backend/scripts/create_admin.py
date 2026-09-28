"""Create or promote an admin account. Run from the command line only --
there is no HTTP endpoint for this, by design, so admin access can never be
granted through the public API.

Usage:
    python -m backend.scripts.create_admin admin@example.com "Admin Name" "StrongPassword123"
    python -m backend.scripts.create_admin existing.user@example.com --promote
"""

from __future__ import annotations

import sys

from backend.core.security import hash_password
from backend.database.connection import SessionLocal
from backend.database.models.enums import UserRole
from backend.database.models.user import User


def create_or_promote_admin(email: str, name: str | None = None, password: str | None = None) -> User:
    db = SessionLocal()
    try:
        email = email.strip().lower()
        user = db.query(User).filter(User.email == email).first()
        if user is not None:
            user.role = UserRole.ADMIN
            db.commit()
            db.refresh(user)
            print(f"Promoted existing user {email} to admin.")
            return user

        if not name or not password:
            raise SystemExit("User does not exist yet: provide both a name and password to create one.")

        user = User(
            name=name.strip(),
            email=email,
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created new admin user {email}.")
        return user
    finally:
        db.close()


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)

    email_arg = args[0]
    if "--promote" in args:
        create_or_promote_admin(email_arg)
    elif len(args) >= 3:
        create_or_promote_admin(email_arg, name=args[1], password=args[2])
    else:
        raise SystemExit(__doc__)
