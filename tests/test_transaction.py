import pytest
from sqlalchemy import Column, Integer, String, UniqueConstraint, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from buska_core.exceptions import ConflictError
from buska_core.transaction import transactional


class Base(DeclarativeBase):
    pass


class Widget(Base):
    __tablename__ = "widgets"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    __table_args__ = (UniqueConstraint("name"),)


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    return factory()


def test_commits_on_success(session):
    with transactional(session):
        session.add(Widget(name="a"))

    assert session.query(Widget).count() == 1


def test_rolls_back_and_raises_conflict_on_integrity_error(session):
    session.add(Widget(name="a"))
    session.commit()

    with pytest.raises(ConflictError):
        with transactional(session):
            session.add(Widget(name="a"))
            session.flush()

    assert session.query(Widget).count() == 1


def test_rolls_back_and_reraises_on_other_errors(session):
    with pytest.raises(ValueError):
        with transactional(session):
            session.add(Widget(name="b"))
            raise ValueError("boom")

    assert session.query(Widget).count() == 0
