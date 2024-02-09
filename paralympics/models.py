# Adapted from https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/quickstart/#define-models
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from werkzeug.security import generate_password_hash, check_password_hash

from paralympics import db


class Region(db.Model):
    __tablename__ = "region"
    NOC: Mapped[String] = mapped_column(db.Text, primary_key=True)
    region: Mapped[String] = mapped_column(db.Text, nullable=False)
    notes: Mapped[String] = mapped_column(db.Text, nullable=True)
    # one-to-many relationship with Event
    events: Mapped[List["Event"]] = relationship(back_populates="region")


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
    password_hash: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
