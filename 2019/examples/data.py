import os

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import class_mapper

Base = declarative_base()


class DictMixin(object):
    def asdict(self):
        return dict((col.name, getattr(self, col.name))
                    for col in class_mapper(self.__class__).mapped_table.c)


class Assignment(Base, DictMixin):
    __tablename__ = 'assignments'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    @classmethod
    def from_dict(cls, value):
        result = Assignment(name=value['name'])
        if 'id' in value:
            result.id = value['id']

        return result

    def update(self, value):
        self.name = value['name']
        return self


host = os.environ.get('DB_HOST', 'localhost')

engine = create_engine('mysql://root:1qaz2wsx@{host}/university2'.format(host=host))

Base.metadata.create_all(engine)
