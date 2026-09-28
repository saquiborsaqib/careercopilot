from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.security import hash_password, verify_password
from backend.database.models.enums import UserRole
from backend.database.models.user import User
from backend.schemas.user import UserCreate


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def create_user(db: Session, data: UserCreate) -> User:
    # Public self-registration always creates a STUDENT account; admin
    # accounts are provisioned separately (see backend.scripts.create_admin).
    user = User(
        name=data.name.strip(),
        email=str(data.email).lower(),
        password_hash=hash_password(data.password),
        role=UserRole.STUDENT,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("An account with this email already exists")
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user
