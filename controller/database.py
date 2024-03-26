from typing import Dict, List, Type
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ColumnExpressionArgument, create_engine
from sqlalchemy.orm import declarative_base
from model.database.table import BaseTable


class Database:
    """Database class which handles the connection to the database

    This class is used to connect to the PostgreSQL database and execute queries, it also handles the disconnection

    Attributes:
        db_name (str): Database name
        engine (str): Database engine
        username (str): Username
        password (str): Password
        host (str): Host
        port (str): Port
        tables (List[Type[BaseTable]]): List of tables to be created in the database
    """

    def __init__(self, db_name: str, engine: str, username: str, password: str, host: str, port: str, tables: List[Type[BaseTable]]) -> None:
        self.db_name = db_name
        self.engine = engine
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.dsn = {
            "sqlite": f"sqlite:///{db_name}",
            "postgresql": f"postgresql://{username}:{password}@{host}:{port}/{db_name}",
            "mysql": f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}?charset=utf8mb4&collation=utf8mb4_unicode_ci"
        }.get(engine)
        self.tables = tables

    def connect(self) -> bool:
        """Connect to the database

        This method will connect to the database

        Returns:
            bool: True if the connection failed, False if the connection succeeded
        """
        try:
            self.engine = create_engine(self.dsn)
            self.session = sessionmaker(bind=self.engine)()
            return False
        except:
            return True

    def disconnect(self) -> None:
        """Disconnect from the database

        This method will disconnect from the database

        Returns:
            None
        """
        if self.session:
            self.session.close()
            self.session = None
        if self.engine:
            self.engine.dispose()
            self.engine = None

    def migrate(self) -> None:
        """Migrate the database

        This method will initialize the database by creating the tables and inserting the default values

        Returns:
            None
        """
        Base = declarative_base()
        for i, table in enumerate(self.tables):
            type(f"{table.__name__}_{i}", (Base, table), {})
        Base.metadata.create_all(self.engine)

    def insert(self, data: BaseTable) -> bool:
        """Insert a record to the database

        This method will add a record to the database

        Returns:
            True if error occurred, False if no error occurred
        """
        try:
            class wrapper(declarative_base(), data.__class__):
                pass
            w = wrapper().set_attrs(data.get_attrs())
            self.session.add(w)
            self.session.commit()
            return False
        except:
            return True

    def query(self, model: Type[BaseTable], *args: ColumnExpressionArgument[bool]) -> List[BaseTable]:
        """Query the database

        This method will query the database with the given conditions

        Returns:
            List of records
        """
        try:
            class wrapper(declarative_base(), model):
                pass
            return self.session.query(wrapper).filter(*args).all()
        except:
            return []

    def update(self, model: Type[BaseTable], data: Dict, *args) -> bool:
        """Update the database

        This method will update the database with the given conditions

        Returns:
            True if error occurred, False if no error occurred
        """
        try:
            class wrapper(declarative_base(), model):
                pass
            self.session.query(wrapper).filter(*args).update(data)
            self.session.commit()
            return False
        except:
            return True

    def delete(self, model: Type[BaseTable], *args) -> bool:
        """Delete a record from the database

        This method will delete record(s) from the database with the given conditions

        Returns:
            True if error occurred, False if no error occurred
        """
        try:
            class wrapper(declarative_base(), model):
                pass
            self.session.query(wrapper).filter(*args).delete()
            self.session.commit()
            return False
        except:
            return True
