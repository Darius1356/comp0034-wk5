# Adapted from https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/quickstart/#define-models
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from werkzeug.security import generate_password_hash, check_password_hash

from paralympics import db


# This uses the latest syntax for SQLAlchemy, older tutorials will show different syntax
# SQLAlchemy provide an __init__ method for each model, so you do not need to declare this in your code
class Region(db.Model):
    __tablename__ = "region"
    NOC: Mapped[String] = mapped_column(db.Text, primary_key=True)
    region: Mapped[String] = mapped_column(db.Text, nullable=False)
    notes: Mapped[String] = mapped_column(db.Text, nullable=True)
    # one-to-many relationship with Event
    # https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-many
    events: Mapped[List["Event"]] = relationship(back_populates="region")
    # cascade='all, delete, delete-orphan'


class Event(db.Model):
    __tablename__ = "event"
    id: Mapped[Integer] = mapped_column(db.Integer, primary_key=True)
    type: Mapped[String] = mapped_column(db.Text, nullable=False)
    year: Mapped[Integer] = mapped_column(db.Integer, nullable=False)
    country: Mapped[String] = mapped_column(db.Text, nullable=False)
    host: Mapped[String] = mapped_column(db.Text, nullable=False)
    # add ForeignKey to Region which is the parent table
    NOC: Mapped[String] = mapped_column(ForeignKey("region.NOC"))
    # add relationship to Region table, the parent
    # https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-many
    region: Mapped["Region"] = relationship(back_populates="events")
    start: Mapped[String] = mapped_column(db.Text, nullable=True)
    end: Mapped[String] = mapped_column(db.Text, nullable=True)
    duration: Mapped[Integer] = mapped_column(db.Integer, nullable=True)
    disabilities_included: Mapped[String] = mapped_column(db.Text, nullable=True)
    countries: Mapped[Integer] = mapped_column(db.Integer, nullable=True)
    events: Mapped[Integer] = mapped_column(db.Integer, nullable=True)
    sports: Mapped[Integer] = mapped_column(db.Integer, nullable=True)
    participants_m: Mapped[Integer] = mapped_column(db.Integer, nullable=True)
    participants_f: Mapped[Integer] = mapped_column(db.Integer, nullable=True)
    participants: Mapped[Integer] = mapped_column(db.Integer, nullable=True)
    highlights: Mapped[String] = mapped_column(db.String, nullable=True)


class User(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    email: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
