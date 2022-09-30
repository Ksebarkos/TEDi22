import models
import errors
import crud
import uuid
import utils


def get_users(db, token):
    utils._token_is_admin(db, token)
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
    utils._token_is_admin(db, token)
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


def get_auctions(db, token, query_params):
    utils._existing_token_and_active(db, token)
    return crud.get_object_list(
        db, models.Auction, **query_params.dict())


def create_auction(db, body, token):
    db_user = utils._token_user_is_validated(db, token)
    data, categories, photos = utils._prepare_auction_creation_data(
        db_user.id, body
    )
    db_auction = crud.create_object(db, models.Auction, data, commit=False)
    for x in categories:        # adding categories
        db_category = crud.get_object_or_none(
            db,
            models.Category,
            filters={"name": x})
        if not db_category:
            db_category = crud.create_object(db, models.Category, {"name": x})
        db_auction.categories.append(db_category)
    for y in photos:        # adding photos
        object = {"auction_id": db_auction.id, "URL": y}
        crud.create_object(db, models.Photo, object, commit=False)
    db.commit()
    db.refresh(db_auction)
    return db_auction


def modify_auction(db, body, token):
    db_auction = utils._token_user_is_auction_creator(db, body, token)
    utils._allowed_modified_timer(db_auction)
    if body.categories:
        utils._modify_auction_categories(db, db_auction, body.categories)
        categories = body.categories
    else:
        categories = [
            db_category.name for db_category in db_auction.categories]
    if body.photos:
        utils._modify_auction_photos(db, db_auction, body.photos)
    data = body.dict()
    db_auction.normalised_description = utils._create_normalized_description(
        data["description"], data["name"], categories
    )
    data.pop("photos")
    data.pop("categories")
    return crud.edit_object(db, db_auction, data)


def submit_bid(db, body, token):
    db_user = utils._token_user_is_validated(db, token)
    db_auction = crud.get_object_or_none(
        db, models.Auction, filters={"id": body.auction_id}
    )
    if not db_auction:
        raise errors.JsonException(errors.INVALID_AUCTION, code=404)
    utils._auction_is_active(db, db_auction)
    data = body.dict()
    data["bidder_id"] = db_user.id
    return crud.create_object(db, models.Bid, data)


def send_message(db, body, token):
    db_user = utils._token_user_is_validated(db, token)
    utils._user_related_to_auction(db, db_user.id, body.auction_id)
    data = body.dict()
    data["read"] = False
    data["sender_id"] = db_user.id
    return crud.create_object(db, models.Message, data)


def delete_message(db, message_id, token):
    db_user = utils._token_user_is_validated(db, token)
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
            errors.USER_NOT_RELATED, code=400
        )
    return crud.remove_object(db, models.Message, message_id)


def is_auction_winner(db, token, auction_id):
    db_user = utils._token_user_is_validated(db, token)
    db_auction = crud.get_object_or_none(
        db, models.Auction, filters={"id": auction_id}
    )
    if not db_auction:
        raise errors.JsonException(errors.AUCTION_NOT_FOUND, code=404)
    return utils._user_won_auction(db, db_user.id, db_auction)


def unread_messages(db, token):
    db_user = utils._token_user_is_validated(db, token)
    return crud.get_object_list(
        db, models.Message, filters={"receiver_id": db_user.id, "read": False}
    )


def get_users_auction(db, token):
    db_user = utils._token_user_is_validated(db, token)
    return crud.get_object_list(
        db, models.Auction, filters={"seller_id": db_user.id}
    )


def get_auction(db, auction_id):
    db_auction = crud.get_object_or_none(
        db, models.Auction, filters={"id": auction_id})
    if not db_auction:
        raise errors.JsonException(errors.AUCTION_NOT_FOUND, code=404)
    return db_auction


def get_active_conversations(db, token):
    db_user = utils._token_user_is_validated(db, token)
    message_list = crud.get_object_list(
        db, models.Message, filters={"sender_id": db_user.id}
    )
    receiver_ids = set([message.receiver.id for message in message_list])
    return crud.get_object_list(
        db, models.User,
        complex_filters=[models.User.id.in_(list(receiver_ids))]
    )


def get_auction_wins(db, token):
    db_user = utils._token_user_is_validated(db, token)
    bid_list = crud.get_object_list(
        db, models.Bid, filters={"bidder_id": db_user.id}
    )
    auction_ids = set([bid.auction_id for bid in bid_list])
    auction_list = crud.get_object_list(
        db, models.Auction,
        complex_filters=[models.Auction.id.in_(list(auction_ids))]
    )
    return_list = []
    for auction in auction_list:
        result = utils._user_won_auction(db, db_user.id, auction)
        if result["is_auction_winner"]:
            return_list.append(auction)
    return return_list


def admin_get_auction(db, auction_id, token):
    utils._token_is_admin(db, token)
    db_auction = crud.get_object_or_none(
        db, models.Auction, filters={"id": auction_id})
    if not db_auction:
        raise errors.JsonException(errors.AUCTION_NOT_FOUND, code=404)
    return db_auction


def Search_Αuction(db, query_params):
    text_query = []
    if query_params.free_text:
        text_query = utils._normalize_text_data(query_params.free_text)
    if query_params.category:
        for category in query_params.category:
            text_query.append(utils._normalize_text_data(str(category)))
    db_auction_list = crud.get_object_list(db, models.Auction)
    search_list = []
    return_list = []
    for db_auction in db_auction_list:
        result = utils._compare_list_elements(
            db_auction.normalised_description.split(), text_query)
        if result:
            search_list.append((db_auction.id, result))
    search_list = utils._Sort_Tuple_List(search_list)
    start = query_params.skip * query_params.limit
    if start >= len(search_list):
        raise errors.JsonException(errors.INVALID_PAGE, code=400)
    for i in range(start-1, start+query_params.limit):
        if start >= len(search_list):
            break
        auction_tuple = search_list.pop(start)
        return_list.append(crud.get_object_or_none(
            db, models.Auction, filters={"id": auction_tuple[0]})
            )
    return return_list
