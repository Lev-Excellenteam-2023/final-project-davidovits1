import os
from datetime import datetime
from pathlib import Path
from sqlalchemy import Enum, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker, scoped_session, declarative_base
from typing import List, Optional
from sqlalchemy import create_engine
from uuid import uuid4

UPLOADS_FOLDER = "uploads"
OUTPUT_FOLDER = 'outputs'


# Create the engine
engine = create_engine('sqlite:///db/db.sqlite3')

# Create a scoped session to manage sessions for each request
Session = scoped_session(sessionmaker(bind=engine))

# Base class for the models
Base = declarative_base()


class UploadStatus:
    done = "done"
    pending = "pending"


def generate_uid() -> str:
    return str(uuid4())


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    uploads: Mapped[List["Upload"]] = relationship("Upload", backref='user', lazy=True, cascade='all, delete-orphan')


class Upload(Base):
    __tablename__ = "upload"
    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[str] = mapped_column(String(36), default=generate_uid, nullable=False, unique=True)
    filename: Mapped[str] = mapped_column(String(128), nullable=False)
    upload_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    finish_time: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    status: Mapped[UploadStatus] = mapped_column(Enum(UploadStatus.pending, UploadStatus.done),
                                                 default=UploadStatus.pending)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('user.id'))


def save_upload(file):
    with Session() as session:
        anonymous_upload = Upload(filename=file.filename, upload_time=datetime.now())
        session.add(anonymous_upload)
        session.commit()
        _, file_type = os.path.splitext(file.filename)
        file.save(os.path.join(UPLOADS_FOLDER, f"{anonymous_upload.uid}{file_type}"))
        return anonymous_upload.uid


def save_upload_with_user(file, email: str):
    with Session() as session:
        user = session.query(User).filter_by(email=email).first()
        if not user:
            user = User(email=email)
            session.add(user)
            session.commit()
        user_upload = Upload(filename=file.filename, upload_time=datetime.now(), user=user)
        session.add(user_upload)
        session.commit()
        _, file_type = os.path.splitext(file.filename)
        file.save(os.path.join(UPLOADS_FOLDER, f"{user_upload.uid}{file_type}"))
        return user_upload.uid


def set_path():
    Path('db').mkdir(parents=True, exist_ok=True)
    Path(UPLOADS_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)


def create_all():
    Base.metadata.create_all(engine)
