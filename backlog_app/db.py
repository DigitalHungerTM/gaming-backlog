from typing import Optional, List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Text, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# declare a base class that we can sub-class to let SQLAlchemy know which classes represent
# our ORM. By writing this base class, we enable ourselves to edit meta settings.
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


def init_app(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()


# Declare ORM classes
class User(Base):
    pass
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))


class Game(Base):
    __tablename__ = "game"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    launcher_id: Mapped[int] = mapped_column(ForeignKey("launcher.id"))
    status_id: Mapped[int] = mapped_column(ForeignKey("status.id"))
    rating: Mapped[Optional[float]]
    man: Mapped[Optional[int]]
    review: Mapped[Optional[str]] = mapped_column(Text)
    proton_id: Mapped[int] = mapped_column(ForeignKey("proton.id"))
    queue_order: Mapped[Optional[int]] = mapped_column()

    status: Mapped["Status"] = relationship(back_populates="games")
    proton: Mapped["Proton"] = relationship(back_populates="games")
    launcher: Mapped["Launcher"] = relationship(back_populates="games")


class Launcher(Base):
    __tablename__ = "launcher"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    games: Mapped[List["Game"]] = relationship(back_populates="launcher")


class Status(Base):
    __tablename__ = "status"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    hex_color: Mapped[str]
    games: Mapped[List["Game"]] = relationship(back_populates="status")


class Proton(Base):
    __tablename__ = "proton"

    id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[str] = mapped_column(unique=True)
    hex_color: Mapped[str]
    games: Mapped[List["Game"]] = relationship(back_populates="proton")