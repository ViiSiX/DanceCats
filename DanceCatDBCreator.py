"""Use to initiate application database."""
# pylint: disable=W0611
from DanceCat import db, Models
# pylint: enable=W0611

db.create_all()
