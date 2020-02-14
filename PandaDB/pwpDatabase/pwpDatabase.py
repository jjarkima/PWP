from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

# Global Variables
SQLITE = 'sqlite'

# Table Names
USERS  = 'users'
TOPICS = 'topics'
MESSAGES = 'messages'


class PWPDatabase:
    DB_ENGINE = {
        SQLITE: 'sqlite:///{DB}'
    }

    # Main DB Connection Ref Obj
    db_engine = None

    def __init__(self, dbtype, dbname=''):
        dbtype = dbtype.lower()

        if dbtype in self.DB_ENGINE.keys():
            engine_url = self.DB_ENGINE[dbtype].format(DB=dbname)

            self.db_engine = create_engine(engine_url)
            print(self.db_engine)

        else:
            print("DBType is not found in DB_ENGINE")

    # Creating Database tables
    def create_db_tables(self):
        metadata = MetaData()
        users = Table(USERS, metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', String),
                      Column('password', String),
                      Column('posted_topics', String, ForeignKey('topics.id')),
                      Column('posted_messages', String, ForeignKey('messages.id'))
                      )

        topics = Table(TOPICS, metadata,
                       Column('id', Integer, primary_key=True),
                       Column('header', String),
                       Column('message', String),
                       Column('time', String)
                       )
        messages = Table(MESSAGES, metadata,
                        Column('id', Integer, primary_key=True),
                        Column('parent_topic_id', String, ForeignKey('topics.id')),
                        Column('message', String),
                        Column('time', String)
                        )

        #Try catch for creating .db file
        try:
            metadata.create_all(self.db_engine)
            print("Tables created")
        except Exception as e:
            print("Error occurred during Table creation!")
            print(e)

    # Handling Insert, Update, Delete queries
    def execute_query(self, query=''):
        if query == '' : return

        print (query)
        with self.db_engine.connect() as connection:
            try:
                connection.execute(query)
            except Exception as e:
                print(e)

    # Prints all data from the database
    def print_all_data(self, table='', query=''):
        query = query if query != '' else "SELECT * FROM '{}';".format(table)
        print(query)

        with self.db_engine.connect() as connection:
            try:
                result = connection.execute(query)
            except Exception as e:
                print(e)
            else:
                for row in result:
                    print(row)  # print(row[0], row[1], row[2])
                result.close()

        print("\n")

    # Sample queries for Insert, Update, Delete cases

    #Sample query to retrieve a specific record
    def retrieve_query(self):
        # Sample Query
        query = "SELECT * FROM USERS WHERE name = 'dille1';"
        self.print_all_data(query=query)

    #Sample query to Insert a record
    def insert_query(self):
        # Insert Data
        query = "INSERT INTO USERS(name, password, posted_topics, posted_messages) VALUES ('dille6', 'dille', '1,2,3', '1,2,3');"
        self.execute_query(query)
        self.print_all_data(USERS)

    # Sample query to Update a record
    def update_query(self):
        # Update Data
        query = "UPDATE USERS set password='pervo' WHERE id=3"
        self.execute_query(query)
        self.print_all_data(USERS)

    # Sample query to Delete a record
    def delete_query(self):
        # Delete Data by Id
        query = "DELETE FROM USERS WHERE id=6"
        self.execute_query(query)
        self.print_all_data(USERS)

