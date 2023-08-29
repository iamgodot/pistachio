from __future__ import annotations

from abc import ABC, abstractmethod
from contextvars import ContextVar
from typing import Self

from sqlalchemy.orm import sessionmaker
from werkzeug.local import LocalProxy

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
    _session_var = ContextVar("session", default=None)
    session = LocalProxy(_session_var)
    _query_var = ContextVar("query", default=None)
    query = LocalProxy(_query_var)

    def __init__(self, session_factory=None, query_cls=None) -> None:
        self.session_factory = session_factory or DEFAULT_SESSION_FACTORY
        self.query_cls = query_cls or Query

    def __enter__(self) -> Self:
        if self._session_var.get() is None:
            self._session_var.set(self.session_factory())
            self._query_var.set(self.query_cls(self.session))
        return self

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def close(self):
        self.session.close()
        self._session_var.set(None)
        self._query_var.set(None)


session_manager = SessionManager()
