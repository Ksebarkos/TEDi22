from sqlalchemy import (
    Column, Integer, String, ForeignKey, Boolean, Float, Table, DateTime
)
from sqlalchemy.orm import relationship
from db import Base


auction_category = Table(
    'auction_category', Base.metadata,
    Column('auction_id', Integer, ForeignKey('Auction.id')),
    Column('category_id', Integer, ForeignKey('Category.id'))
)

auction_bid = Table(
    'auction_bid', Base.metadata,
    Column('auction_id', Integer, ForeignKey('Auction.id')),
    Column('bid_id', Integer, ForeignKey('Bid.id'))
)

# auction_location = Table(
#     'auction_location', Base.metadata,
#     Column('auction_id', Integer, ForeignKey('Auction.id')),
#     Column('Location_id', Integer, ForeignKey('Location.id'))
# )
#
# user_location = Table(
#     'auction_location', Base.metadata,
#     Column('auction_id', Integer, ForeignKey('Auction.id')),
#     Column('Location_id', Integer, ForeignKey('Location.id'))
# )


class User(Base):
    __tablename__ = "users"

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
    location_id = Column(Integer, ForeignKey("Location.id"), nullable=False)
    location = relationship("Location")


class TokenSession(Base):
    __tablename__ = "TokenSessions"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, nullable=False, unique=True, index=True)
    active = Column(Boolean, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User")


class Auction(Base):
    __tablename__ = "Auction"

    id = Column(Integer, primary_key=True, index=True)
    Name = Column(String, nullable=False)
    currently = Column(Float, nullable=False)
    buy_price = Column(Float, nullable=False)
    first_bid = Column(Float, nullable=False)
    number_of_bids = Column(Float, nullable=False)
    started = Column(DateTime(timezone=True), nullable=False)
    ends = Column(DateTime(timezone=True), nullable=False)
    description = Column(String, nullable=True)
    seller_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    seller = relationship("User")
    location_id = Column(Integer, ForeignKey("Location.id"), nullable=False)
    location = relationship("Location")

    categories = relationship("Category", secondary=auction_category)

    bids = relationship("Bid", secondary=auction_bid)


class Category(Base):
    __tablename__ = "Category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    auctions = relationship("Auction", secondary=auction_category)


class Bid(Base):
    __tablename__ = "Bid"

    id = Column(Integer, primary_key=True, index=True)
    bidder = relationship("User")
    time = Column(DateTime(timezone=True), nullable=False)
    amount = Column(Integer, nullable=False)


class Location(Base):
    __tablename__ = "Location"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longtitude = Column(Float, nullable=False)
    Address = Column(String, nullable=False)
    Country = Column(String, nullable=False)
