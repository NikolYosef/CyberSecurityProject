from sqlalchemy.orm import Session
from app import models


# Saves a new log record in the database.
def add_log(db: Session, user_id, action, status):
    log = models.Log(

        user_id=user_id,
        action=action,
        status=status
    )
    db.add(log)
    db.commit()
