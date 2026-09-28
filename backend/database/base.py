from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase): pass
from .models import *  # noqa: F401,F403,E402
