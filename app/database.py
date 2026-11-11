"""SQLAlchemy repository: cache and timestamp provider responses."""
import json
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class CachedResponse(Base):
    __tablename__ = 'cached_responses'
    key: Mapped[str] = mapped_column(String(300), primary_key=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class RateRepository:
    def __init__(self, url):
        options = {'connect_args': {'check_same_thread': False}} if url.startswith('sqlite') else {}
        self.engine = create_engine(url, **options)
        Base.metadata.create_all(self.engine)

    def get(self, key):
        with Session(self.engine) as session:
            row = session.get(CachedResponse, key)
            if row is None:
                return None
            return json.loads(row.payload), row.fetched_at.replace(tzinfo=timezone.utc)

    def put(self, key, payload, now):
        with Session(self.engine) as session:
            session.merge(CachedResponse(key=key, payload=json.dumps(payload), fetched_at=now))
            session.commit()
