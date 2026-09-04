from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from buska_core.exceptions import ConflictError


@contextmanager
def transactional(session: Session) -> Generator[None]:
    try:
        yield
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise ConflictError("Violação de integridade") from e
    except Exception:
        session.rollback()
        raise
