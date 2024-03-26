from model.database.table import BaseTable
from sqlalchemy import Column, String, Integer


class Records(BaseTable):
    __tablename__ = "records"

    timestamp = Column(
        Integer,
        name="timestamp",
        primary_key=True,
        autoincrement=True,
    )
    message = Column(
        String,
        name="item_id",
    )
    typecode = Column(
        Integer,
        name="typecode",
    )
    icao = Column(
        String,
        name="icao",
    )
