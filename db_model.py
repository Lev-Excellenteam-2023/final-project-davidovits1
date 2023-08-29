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
    """
    Represents the status of an uploaded file.

    Attributes:
        done (str): The status indicating that the upload is completed.
        pending (str): The status indicating that the upload is pending.

    This class provides predefined constants for different upload statuses, making it easier
    to manage and check the status of uploaded files.
    """

    done = "done"
    pending = "pending"


def generate_uid() -> str:
    """
    Generate a unique identifier (UID) as a string.

    Returns:
        str: A string containing a unique identifier generated using the UUID4 algorithm.

    This function generates a unique identifier that can be used for various purposes,
    such as creating unique filenames or identifying records in a database.
    The UUID4 algorithm provides a high likelihood of generating globally unique identifiers.
    """
    return str(uuid4())


class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (int): The primary key ID of the user.
        email (str): The email address of the user.
        uploads (List[Upload]): A list of Upload objects associated with the user.
    """
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    uploads: Mapped[List["Upload"]] = relationship("Upload", backref='user', lazy=True, cascade='all, delete-orphan')


class Upload(Base):
    """
    Represents an uploaded file and its associated data.

    Attributes:
        id (int): The primary key ID of the upload.
        uid (str): The unique identifier of the upload.
        filename (str): The name of the uploaded file.
        upload_time (datetime): The timestamp of the upload.
        finish_time (Optional[datetime]): The timestamp when the upload process finished.
        status (UploadStatus): The status of the upload.
        user_id (Optional[int]): The foreign key ID of the user associated with the upload.
    """
    __tablename__ = "upload"
    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[str] = mapped_column(String(36), default=generate_uid, nullable=False, unique=True)
    filename: Mapped[str] = mapped_column(String(128), nullable=False)
    upload_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    finish_time: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    status: Mapped[UploadStatus] = mapped_column(Enum(UploadStatus.pending, UploadStatus.done),
                                                 default=UploadStatus.pending)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('user.id'))


def save_upload(file) -> str:
    """
    Save an uploaded file and its associated data.

    Args:
        file: The uploaded file object.

    Returns:
        str: The unique identifier (UID) of the uploaded file.
    """
    with Session() as session:
        anonymous_upload = Upload(filename=file.filename, upload_time=datetime.now())
        session.add(anonymous_upload)
        session.commit()
        _, file_type = os.path.splitext(file.filename)
        file.save(os.path.join(UPLOADS_FOLDER, f"{anonymous_upload.uid}{file_type}"))
        return anonymous_upload.uid


def save_upload_with_user(file, email: str) -> str:
    """
    Save an uploaded file and associate it with a user.

    Args:
        file: The uploaded file object.
        email (str): The email address of the user.

    Returns:
        str: The unique identifier (UID) of the uploaded file.
    """
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
    """Create necessary directories if they don't exist."""
    Path('db').mkdir(parents=True, exist_ok=True)
    Path(UPLOADS_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)


def create_all():
    """Create database tables."""
    Base.metadata.create_all(engine)
