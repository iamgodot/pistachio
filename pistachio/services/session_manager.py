from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self

from sqlalchemy.orm import sessionmaker

from pistachio.adapters.query import Query, QueryBase
from pistachio.extensions import engine


class SessionManagerBase(ABC):
    query: QueryBase

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        self.close()

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError

    @abstractmethod
    def close(self):
        raise NotImplementedError


DEFAULT_SESSION_FACTORY = sessionmaker(bind=engine)


class SessionManager(SessionManagerBase):
    def __init__(self, session_factory=None, query_cls=None) -> None:
        self.session_factory = session_factory or DEFAULT_SESSION_FACTORY
        self.query_cls = query_cls or Query

    def __enter__(self) -> Self:
        # NOTE: init session&query here so we can reuse the manager
        self.session = self.session_factory()
        self.query = self.query_cls(self.session)
        return self

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def close(self):
        self.session.close()


session_manager = SessionManager()
