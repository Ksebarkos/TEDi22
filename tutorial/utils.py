import models
import errors
import crud
from datetime import datetime
import re
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))


def _existing_token_and_active(db, token):
    db_token = crud.get_object_or_none(
        db, models.TokenSession, filters={"token": token})
    if not db_token:
        raise errors.JsonException(errors.INVALID_TOKEN, code=404)
    if not db_token.active:
        raise errors.JsonException(errors.TOKEN_EXPIRED, code=404)
    return db_token


def _prepare_auction_creation_data(user_id, body):
    data = body.dict()
    data["seller_id"] = user_id
    data["normalised_description"] = _create_normalized_description(
        data["description"], data["name"], data["category"]
    )
    categories = data.pop("category")
    photos = data.pop("photo")
    return data, categories, photos,


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


def _modify_auction_categories(db, db_auction, categories):
    db_categories = []
    for x in categories:
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
    db.flush()
    return db_auction


def _modify_auction_photos(db, db_auction, photos):
    for db_photo in db_auction.photos:
        crud.remove_object(db, models.Photo, db_photo.id, commit=False)
    for photo in photos:
        photodata = {"auction_id": db_auction.id, "URL": photo}
        crud.create_object(db, models.Photo, photodata)
    db.flush()
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
    return no_stopwords_data  # string


def _create_normalized_description(description, name, categories):
    search_list = _normalize_text_data(description)
    search_list += f" {_normalize_text_data(name)}"
    for i in categories:
        search_list += f" {_normalize_text_data(i)}"
    return search_list


def _compare_list_elements(list1, list2):
    value = len(list(set(list1).intersection(set(list2))))
    return value


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
            errors.USER_NOT_RELATED, code=400
        )
        return


def _user_won_auction(db, user_id, db_auction):
    MaxBid = crud.get_object_list(
        db, models.Bid, filters={"auction_id": db_auction.id},
        order_by="amount", limit=1)
    if not MaxBid:
        raise errors.JsonException(errors.AUCTION_NOT_STARTED, code=400)
    if MaxBid[0].bidder_id != user_id:
        return {"is_auction_winner": False}
    return {"is_auction_winner": True}


def _Sort_Tuple_List(tup):   # code from https://www.geeksforgeeks.org
    lst = len(tup)
    for i in range(0, lst):
        for j in range(0, lst-i-1):
            if (tup[j][1] > tup[j + 1][1]):
                temp = tup[j]
                tup[j] = tup[j + 1]
                tup[j + 1] = temp
    return tup
