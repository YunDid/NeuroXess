import json
import sqlite3
from typing import List

# from typing import List, Dict

import loguru
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, select
from sqlalchemy.orm import DeclarativeBase, Session, declarative_base
from sqlalchemy import JSON, Text, INT

Base = declarative_base()



class MetaInfo(Base):
    __tablename__ = "meta_info"

    id = Column(INT, primary_key=True, autoincrement=True)

    meta_info = Column(JSON, nullable=True, comment="")



class SortedSpikeModel(Base):
    __tablename__ = "sorted_spike"

    time = Column(INT, nullable=True, comment="", primary_key=True)
    unit_results = Column(JSON, nullable=True, comment="")
    # unit = Column(INT, nullable=True, comment="")

class SortedSpikeDao:

    def __init__(self, db_path):
        # self._db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        # self._client = sqlite3.connect(db_path)

    def insert_one(self, record:SortedSpikeModel):
        courser = self._client.cursor()
        sql = f"""INSERT INTO {self.table_name} (time, unit_results) 
VALUES ({record.time}, \"{json.dumps(record.unit_results)}\";"""
        courser.execute(sql)

    def save_meta(self, meta):
        with Session(self.engine) as session:
            session.add(meta)
            session.commit()

    def insert_many(self, records:List[SortedSpikeModel]):
        with Session(self.engine) as session:
            session.add_all(records)
            session.commit()

    def create(self):
        Base.metadata.create_all(bind=self.engine)


    def create_meta_info(self, cousor):
        sql = f"""create table meta_info(
                 meta_info TEXT NOT NULL 
                )
                """
        cousor.execute(sql)

    def create_table(self, cousor):
        sql = f"""create table {self.table_name}(
         time INT PRIMARY KEY NOT NULL,
         channels  VARCHAR(255),
         unit INT NOT NULL
        )
        """
        cousor.execute(sql)

    def select_many(self, ):
        with Session(self.engine) as session:
            stmt = select(SortedSpikeModel)
            results = []
            for user in session.scalars(stmt):
                results.append(user)
        return results




if __name__ == '__main__':
    s = SortedSpikeDao(r"D:\develop\py\mind-explorer-sorting\test\data\s_spike.mex")
    s.create()
    records = []
    for i in range(10):
        records.append(SortedSpikeModel(time=i, unit_results=[{"unit": 1, "channels": [2, 3, 4]}, {"unit": 2, "channels": [3, 12, 4]}]))
    s.insert_many(records)
    print("all done")
    s.save_meta(MetaInfo(meta_info={"channels": 1, "sample_rate": 2}))
    res = s.select_many()
    for each in res:

        print(each.unit_results)