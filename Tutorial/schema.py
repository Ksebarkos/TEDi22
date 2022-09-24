from pydantic import BaseModel
from datetime import datetime


class User(BaseModel):
    id: int
    username: str
    password: str
    email: str
    name: str
    surname: str
    phone: str
    address: str
    postcode: str
    city: str
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
    address: str
    postcode: str
    city: str
    afm: str
    role: str


class UserId(BaseModel):
    user_id: int


class LoginCredentials(BaseModel):
    username: str
    password: str


class LoginToken(BaseModel):
    token: str
    role: str


class GetAuction(BaseModel):
    token: str
    page: int


# class AuctionCreate(BaseModel):
#     token: str
#     name: str
#     category: list
#     currently = 0.0
#     buy_price: float
#     first_bid = 0.0
#     number_of_bids = 0
#     location: str
#     country: str
#     position: str
#     started: datetime.datetime = "0000-00-00[T]00:00"  # YYYY-MM-DD[T]HH:MM
#     ends: datetime.datetime = "0000-00-00[T]00:00"
#     description: str
#     photo: list
