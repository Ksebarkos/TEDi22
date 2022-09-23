import models
import errors
import crud
import uuid

AUCTION_PAGE_LIMIT = 10


def _existing_token_and_active(db, token):
    db_token = crud.get_object_or_none(
        db, models.TokenSession, filters={"token": token})
    if not db_token:
        raise errors.JsonException(errors.INVALID_TOKEN, code=404)
    if not db_token.active:
        raise errors.JsonException(errors.TOKEN_EXPIRED, code=404)
    return db_token


def _token_is_admin(db, token):
    db_token = _existing_token_and_active(db, token)
    if db_token.user.role != "admin":
        raise errors.JsonException(errors.USER_NOT_ADMIN, code=400)


def get_users(db, token):
    _token_is_admin(db, token)
    return crud.get_object_list(db, models.User)


def create_user(db, body):
    db_user = crud.get_object_or_none(
        db, models.User, filters={"username": body.username})
    if db_user:
        raise errors.JsonException(errors.USERNAME_IN_USE, code=400)
    data = body.dict()
    data["validated"] = False
    return crud.create_object(db, models.User, data)


def validate_user(db, userid, token):
    _token_is_admin(db, token)
    db_user = crud.get_object_or_none(
        db, models.User, filters={"id": userid})
    if not db_user:
        raise errors.JsonException(errors.USER_NOT_FOUND, code=404)
    return crud.edit_object(db, db_user, {"validated": True})


def login(db, creds):
    db_user = crud.get_object_or_none(
        db, models.User,
        filters={"username": creds.username, "password": creds.password})
    if not db_user:
        raise errors.JsonException(errors.WRONG_CREDENTIALS, code=404)
    db_token = crud.create_object(
        db, models.TokenSession,
        {"token": str(uuid.uuid4()), "active": True, "user_id": db_user.id})
    return {"token": db_token.token, "role": db_user.role}


# def get_auctions(db, token):
#     _existing_token_and_active(
#         db, token, skip=(body.page)-1, limit=AUCTION_PAGE_LIMIT
#     )
#     return crud.get_object_list(db, models.Auction)

def create_auction(db, body):
    db_token = _existing_token_and_active(db, body.token)
    db_user = crud.get_object_or_none(
        db, models.User, filters={"id": db_token.userid}
    )
    if not db_user:
        raise errors.JsonException(errors.USER_NOT_FOUND, code=404)
    data = body.dict()
    data["seller_id"] = db_user.seller_id
    # push in #
    return
