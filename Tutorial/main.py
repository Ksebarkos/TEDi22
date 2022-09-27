from fastapi import FastAPI, Depends, Request, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import schema
import errors
from typing import List
from db import get_db
import logic

origins = ["http://localhost/"]
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(errors.JsonException)
async def unicorn_exception_handler(
    request: Request, exc: errors.JsonException
):
    return JSONResponse(
        status_code=exc.code,
        content={
            "message": exc.message,
            "detail": exc.details,
            "data": exc.data,
        },
    )


@app.get("/users/", response_model=List[schema.User])
def get_users(db: Session = Depends(get_db), token: str = Header(None)):
    return logic.get_users(db, token)


@app.post("/users/", response_model=schema.User)
def create_user(body: schema.UserCreate, db: Session = Depends(get_db)):
    return logic.create_user(db, body)


@app.put("/admin/validate-user/", response_model=schema.User)
def validate_user(
    body: schema.UserId, db: Session = Depends(get_db),
    token: str = Header(None)
):
    return logic.validate_user(db, body.user_id, token)


@app.post("/login/", response_model=schema.LoginToken)
def login(
    body: schema.LoginCredentials, db: Session = Depends(get_db),
):
    return logic.login(db, body)


@app.get("/auctions/", response_model=List[schema.Auction])
def get_auctions(
    db: Session = Depends(get_db), token: str = Header(None),
    page: schema.Pagination = Depends()
):
    return logic.get_auctions(db, token)


@app.post("/register-auction/", response_model=schema.Auction)
def create_auction(
    body: schema.AuctionCreate, db: Session = Depends(get_db),
    token: str = Header(None)
):
    return logic.create_auction(db, body, token)


@app.post("/modify-auction/", response_model=schema.Auction)
def modify_auction(
    body: schema.ModifyAuction, db: Session = Depends(get_db),
    token: str = Header(None)
):
    return logic.modify_auction(db, body, token)


@app.post("/modify-auction-category/", response_model=schema.Auction)
def modify_auction_category(
    body: schema.ModifyAuctionCategories, db: Session = Depends(get_db),
    token: str = Header(None)
):
    return logic.modify_auction_categories(db, body, token)


@app.post("/modify-auction-photos/", response_model=schema.Auction)
def modify_auction_photo(
    body: schema.ModifyAuctionPhoto, db: Session = Depends(get_db),
    token: str = Header(None)
):
    return logic.modify_auction_photo(db, body, token)


@app.post('/bid/', response_model=schema.Bid)
def submit_bid(
    body: schema.SubmitBid, db: Session = Depends(get_db),
    token: str = Header(None)
):
    return logic.submit_bid(db, body, token)


@app.post('/message/', response_model=schema.Message)
def send_message(
    body: schema.SendMessage, db: Session = Depends(get_db),
    token: str = Header(None)
):
    return logic.send_message(db, body, token)


@app.delete('/delete-message/{message_id}/', response_model=dict)
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    token: str = Header(None)
):
    return logic.delete_message(db, message_id, token)


if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
