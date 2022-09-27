import models
import errors
import crud
import uuid
import re
import nltk
from datetime import datetime
from nltk.corpus import stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

AUCTION_PAGE_LIMIT = 10


def _existing_token_and_active(db, token):
    db_token = crud.get_object_or_none(
        db, models.TokenSession, filters={"token": token})
    if not db_token:
        raise errors.JsonException(errors.INVALID_TOKEN, code=404)
    if not db_token.active:
        raise errors.JsonException(errors.TOKEN_EXPIRED, code=404)
    return db_token


def _token_user_is_validated(db, token):
    db_token = _existing_token_and_active(db, token)
    db_user = crud.get_object_or_none(
        db, models.User, filters={"id": db_token.user_id}
    )
    if not db_user:
        raise errors.JsonException(errors.USER_NOT_FOUND, code=404)
    if not db_user.validated:
        raise errors.JsonException(errors.USER_NOT_VALIDATED, code=401)
    return db_user


def _token_user_is_auction_creator(db, body, token):
    db_user = _token_user_is_validated(db, token)
    db_auction = crud.get_object_or_none(
        db,
        models.Auction,
        filters={"id": body.id}
    )
    if not db_auction:
        raise errors.JsonException(errors.AUCTION_NOT_FOUND, code=404)
    if db_auction.seller_id != db_user.id:
        raise errors.JsonException(errors.USER_NOT_AUTHORISED, code=401)
    return db_auction


def _allowed_modified_timer(db_auction):
    if db_auction.number_of_bids > 0:
        raise errors.JsonException(errors.AUCTION_ALREADY_STARTED, code=400)
    return


def _auction_is_active(db, db_auction):
    if db_auction.start >= datetime.now():
        raise errors.JsonException(errors.AUCTION_HASNT_STARTED, code=400)
    if db_auction.ends <= datetime.now():
        raise errors.JsonException(errors.AUCTION_ALREADY_ENDED, code=400)
    MaxBid = crud.get_object_list(
        db, models.Bid, filters={"auction_id": db_auction.id},
        order_by="amount", limit=1)
    if not MaxBid:
        return
    if MaxBid[0].amount > db_auction.buy_price:
        raise errors.JsonException(errors.AUCTION_ALREADY_ENDED, code=400)
    return


def _normalize_text_data(data):   # code from https://www.geeksforgeeks.org
    lower_data = data.lower()
    no_number_data = re.sub(r'\d+', '', lower_data)
    no_punc_data = re.sub(r'[^\w\s]', '', no_number_data)
    no_wspace_data = no_punc_data.strip()
    lst_data = [no_wspace_data][0].split()
    no_stopwords_data = ""
    for i in lst_data:
        if i not in stop_words:
            no_stopwords_data += i+' '

    no_stopwords_data = no_stopwords_data[:-1]

    # output
    return no_stopwords_data


def _token_is_admin(db, token):
    db_token = _existing_token_and_active(db, token)
    if db_token.user.role != "admin":
        raise errors.JsonException(errors.USER_NOT_ADMIN, code=400)


def _user_related_to_auction(db, user_id, auction_id):
    db_auction = crud.get_object_or_none(
        db, models.Auction, filters={"id": auction_id}
    )
    if not db_auction:
        raise errors.JsonException(errors.AUCTION_NOT_FOUND, code=404)
    if db_auction.seller_id == user_id:
        return
    MaxBid = crud.get_object_list(
        db, models.Bid, filters={"auction_id": db_auction.id, },
        order_by="amount", limit=1)
    if not MaxBid:
        raise errors.JsonException(errors.AUCTION_NOT_STARTED, code=400)
    if MaxBid[0].bidder_id != user_id:
        raise errors.JsonException(
            errors.USER_NOT_RELATED_TO_AUCTION, code=400
        )
        return


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


def get_auctions(db, token):  # needs workto return bids, categories and photos
    _existing_token_and_active(db, token)
    return crud.get_object_list(db, models.Auction, limit=AUCTION_PAGE_LIMIT)


def create_auction(db, body, token):
    db_token = _existing_token_and_active(db, token)
    db_user = crud.get_object_or_none(
        db, models.User, filters={"id": db_token.user_id}
    )
    if not db_user:
        raise errors.JsonException(errors.USER_NOT_FOUND, code=404)
    if not db_user.validated:
        raise errors.JsonException(errors.USER_NOT_AUTHORISED, code=401)
    data = body.dict()
    data["seller_id"] = db_user.id
    data["normalised_description"] = data["description"]
    categories = data.pop("category")
    photos = data.pop("photo")
    db_auction = crud.create_object(db, models.Auction, data, commit=False)
    for x in categories:
        db_category = crud.get_object_or_none(
            db,
            models.Category,
            filters={"name": x})
        if not db_category:
            db_category = crud.create_object(db, models.Category, {"name": x})
        # object = {"auction_id": db_auction.id, "db_category": db_category.id}
        db_auction.categories.append(db_category)
        # crud.create_object(db, models.auction_category, object, commit=False)
    for y in photos:
        object = {"auction_id": db_auction.id, "URL": y}
        crud.create_object(db, models.Photo, object, commit=False)
    db.commit()
    db.refresh(db_auction)
    return db_auction


def modify_auction(db, body, token):
    db_auction = _token_user_is_auction_creator(db, body, token)
    _allowed_modified_timer(db_auction)
    data = body.dict()
    return crud.edit_object(db, db_auction, data)


def modify_auction_categories(db, body, token):
    db_auction = _token_user_is_auction_creator(db, body, token)
    _allowed_modified_timer(db_auction)
    db_categories = []
    for x in body.categories:
        db_category = crud.get_object_or_none(
            db,
            models.Category,
            filters={"name": x})
        if not db_category:
            db_category = crud.create_object(
                db,
                models.Category,
                {"name": x},
                commit=False
            )
        db_categories.append(db_category)
    db_auction.categories = db_categories
    db.commit()
    db.refresh(db_auction)
    return db_auction


def modify_auction_photo(db, body, token):
    db_auction = _token_user_is_auction_creator(db, body, token)
    _allowed_modified_timer(db_auction)
    for db_photo in db_auction.photos:
        crud.remove_object(db, models.Photo, db_photo.id, commit=False)
    for photo in body.photo:
        photodata = {"auction_id": db_auction.id, "URL": photo}
        crud.create_object(db, models.Photo, photodata)
    db.commit()
    db.refresh(db_auction)
    return db_auction


def submit_bid(db, body, token):
    db_user = _token_user_is_validated(db, token)
    db_auction = crud.get_object_or_none(
        db, models.Auction, filters={"id": body.auction_id}
    )
    if not db_auction:
        raise errors.JsonException(errors.INVALID_AUCTION, code=404)
    _auction_is_active(db, db_auction)
    data = body.dict()
    data["bidder_id"] = db_user.id
    return crud.create_object(db, models.Bid, data)


def send_message(db, body, token):
    db_user = _token_user_is_validated(db, token)
    _user_related_to_auction(db, db_user.id, body.auction_id)
    data = body.dict()
    data["read"] = False
    data["sender_id"] = db_user.id
    return crud.create_object(db, models.Message, data)


def delete_message(db, message_id, token):
    db_user = _token_user_is_validated(db, token)
    db_message = crud.get_object_or_none(
        db, models.Message, filters={"id": message_id}
    )
    if not db_message:
        raise errors.JsonException(
            errors.MESSAGE_NOT_FOUND, code=404
        )
    if (db_message.sender_id != db_user.id and
            db_message.receiver_id != db_user.id):
        raise errors.JsonException(
            errors.USER_NOT_RELATED_TO_AUCTION, code=400
        )
    return crud.remove_object(db, models.Message, message_id)
