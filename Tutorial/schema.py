from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from typing_extensions import Literal


class User(BaseModel):
    id: int
    username: str
    password: str
    email: str
    name: str
    surname: str
    phone: str
    location: str
    country: str
    afm: str
    role: str
    validated: bool

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    name: str
    surname: str
    phone: str
    location: str
    country: str
    afm: str
    role: str


class UserId(BaseModel):
    user_id: int


class Pagination(BaseModel):
    skip: Optional[int]
    limit: Optional[int]


class ItemQueryParams(Pagination):
    order_by: Optional[Literal["expiration_date"]]


class LoginCredentials(BaseModel):
    username: str
    password: str


class LoginToken(BaseModel):
    token: str
    role: str


class Photo(BaseModel):
    id: str
    auction_id: str
    URL: str

    class Config:
        orm_mode = True


class Bid(BaseModel):
    id: int
    auction_id: int
    bidder_id: int
    time: datetime
    amount: float

    class Config:
        orm_mode = True


class Category(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Auction(BaseModel):
    id: str
    name: str
    currently = 0.0
    buy_price: float
    first_bid = 0.0
    number_of_bids = 0
    location: str
    country: str
    start: datetime  # YYYY-MM-DD[T]HH:MM
    ends: datetime
    description: str
    longtitude: str
    latitude: str
    categories: List[Category]
    photos: List[Photo]
    bids: List[Bid]

    class Config:
        orm_mode = True


class ModifyAuction(BaseModel):
    id: int
    name: str
    buy_price: float
    location: str
    country: str
    start: datetime
    ends: datetime
    description: str
    longtitude: str
    latitude: str


class SubmitBid(BaseModel):
    auction_id: int
    time: datetime
    amount: float


class ModifyAuctionCategories(BaseModel):
    id: int
    categories: list
    start: datetime


class ModifyAuctionPhoto(BaseModel):
    id: int
    photo: list
    start: datetime


class AuctionCreate(BaseModel):
    name: str
    currently = 0.0
    buy_price: float
    first_bid = 0.0
    number_of_bids = 0
    location: str
    country: str
    latitude: str
    longtitude: str
    start: datetime  # YYYY-MM-DD[T]HH:MM
    ends: datetime
    description: str
    photo: list
    category: list


class Message(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    message: str
    read: bool

    class Config:
        orm_mode = True


class SendMessage(BaseModel):
    receiver_id: int
    message: str
    auction_id: int


class DeleteMessage(BaseModel):
    id: int
