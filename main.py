from fastapi import FastAPI, Depends, Request, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uvicorn
import schema
import errors
from typing import List
from db import get_db
import logic

app = FastAPI()


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


@app.get("/auctions/", response_model=List[schema.GetAuction])
def get_auctions(
    db: Session = Depends(get_db), token: str = Header(None)
):
    return logic.get_auctions(db, token)  # , page)


# @app.post("/register-auction/", response_model=schema.LoginToken)
# def create_auction(
#     body: schema.AuctionCreate, db: Session = Depends(get_db),
# ):
#     return logic.create_auction(db, body)


if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
