from sqlalchemy import (
    Column, Integer, String, ForeignKey, Boolean, Float, Table, DateTime
)
from sqlalchemy.orm import relationship
from db import Base


auction_category = Table(
    'auction_category', Base.metadata,
    Column('auction_id', Integer, ForeignKey('Auctions.id')),
    Column('category_id', Integer, ForeignKey('Categories.id'))
)


class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    afm = Column(String, nullable=False)
    validated = Column(Boolean, nullable=False)
    role = Column(String, nullable=False)
    seller_rating = Column(Float, nullable=True)
    bidder_rating = Column(Float, nullable=True)
    location = Column(String, nullable=False)
    country = Column(String, nullable=False)


class TokenSession(Base):
    __tablename__ = "TokenSessions"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, nullable=False, unique=True, index=True)
    active = Column(Boolean, nullable=False)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    user = relationship("User")


class Auction(Base):
    __tablename__ = "Auctions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    currently = Column(Float, nullable=False)
    buy_price = Column(Float, nullable=False)
    first_bid = Column(Float, nullable=False)
    number_of_bids = Column(Float, nullable=False)
    start = Column(DateTime(timezone=True), nullable=False)
    ends = Column(DateTime(timezone=True), nullable=False)
    description = Column(String, nullable=True)
    seller_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    seller = relationship("User")
    location = Column(String, nullable=True)
    country = Column(String, nullable=True)
    longtitude = Column(String, nullable=False)
    latitude = Column(String, nullable=False)
    normalised_description = Column(String, nullable=False)

    categories = relationship("Category", secondary=auction_category)

    photos = relationship("Photo")

    bids = relationship("Bid")


class Category(Base):
    __tablename__ = "Categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    auctions = relationship("Auction", secondary=auction_category)


class Photo(Base):
    __tablename__ = "Photos"

    id = Column(Integer, primary_key=True, index=True)
    URL = Column(String, nullable=False)
    auction_id = Column(Integer, ForeignKey("Auctions.id"), nullable=False)
    auction = relationship("Auction")


class Bid(Base):
    __tablename__ = "Bids"

    id = Column(Integer, primary_key=True, index=True)
    auction_id = Column(Integer, ForeignKey("Auctions.id"), nullable=False)
    auction = relationship("Auction")
    bidder_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    bidder = relationship("User")
    time = Column(DateTime(timezone=True), nullable=False)
    amount = Column(Float, nullable=False)


class Location(Base):
    __tablename__ = "Locations"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longtitude = Column(Float, nullable=False)
    Address = Column(String, nullable=False)
    Country = Column(String, nullable=False)


class Message(Base):
    __tablename__ = "Messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    sender = relationship("User", foreign_keys=[sender_id])
    receiver_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    receiver = relationship("User", foreign_keys=[receiver_id])
    message = Column(String, nullable=False)
    read = Column(Boolean, nullable=False)
    # auction_id = Column(Integer, ForeignKey("Auctions.id"), nullable=False)
    # auction = relationship("Auction")
