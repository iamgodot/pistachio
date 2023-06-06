from abc import ABC, abstractmethod

from sqlalchemy import delete, select, update


class QueryBase(ABC):
    @abstractmethod
    def add(self, *args):
        raise NotImplementedError

    @abstractmethod
    def first(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def list(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def update(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def delete(self, *args, **kwargs):
        raise NotImplementedError


class Query(QueryBase):
    def __init__(self, session) -> None:
        self.session = session

    def add(self, obj):
        # TODO: consider use insert statement
        self.session.add(obj)

    def first(self, model, **filters):
        """Return first obj or None."""
        return self.session.execute(select(model).filter_by(**filters)).scalar()

    def get(self, model, **filters):
        return self.session.execute(select(model).filter_by(**filters)).scalar_one()

    def list(self, model, **filters):
        return self.session.execute(select(model).filter_by(**filters)).scalars().all()

    def update(self, model, params: dict, **filters):
        self.session.execute(update(model).filter_by(**filters).values(**params))

    def delete(self, model, **filters):
        self.session.execute(delete(model).filter_by(**filters))
