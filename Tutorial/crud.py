from sqlalchemy.exc import NoResultFound


def get_object_or_none(
    db, model, filters={}, complex_filters=[], for_update=False
):
    try:
        queryset = db.query(model).filter_by(**filters).filter(
            *complex_filters)
        if for_update:
            queryset = queryset.with_for_update()
        db_object = queryset.one()
        return db_object
    except NoResultFound:
        return None


def get_object_list(
    db, model, filters={}, complex_filters=[],
    order_by=None, skip=None, limit=None,
):
    queryset = db.query(model).filter_by(**filters).filter(
        *complex_filters)
    if order_by:
        queryset = queryset.order_by(getattr(model, order_by).desc())
    queryset = queryset.order_by(model.id.desc())
    if skip:
        queryset = queryset.offset(skip)
    if limit:
        queryset = queryset.limit(limit)
    db_objects = queryset.all()
    return db_objects


def create_object(db, model, data, commit=True):
    db_object = model(**data)
    db.add(db_object)
    db.flush()
    if commit:
        db.commit()
    db.refresh(db_object)
    return db_object


def edit_object(db, db_object, data, commit=True):
    for key, item in data.items():
        setattr(db_object, key, item)
    db.flush()
    if commit:
        db.commit()
    db.refresh(db_object)
    return db_object


def remove_object(db, model, object_id, commit=True):
    deleted = db.query(model).filter_by(id=object_id).delete()
    db.flush()
    if commit:
        db.commit()
    return {"deleted": deleted}
