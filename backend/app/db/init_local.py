from app.db.base import Base
from app.db.session import engine
from app.models import *  # noqa: F401,F403
from app.db.seed import seed


def init_local() -> None:
    Base.metadata.create_all(bind=engine)
    seed()


if __name__ == "__main__":
    init_local()
