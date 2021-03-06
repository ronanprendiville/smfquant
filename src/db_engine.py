import json
import base64
import pandas as pd
from sqlalchemy import create_engine

class DbEngine:

    def __init__(self):
        """
        Class to create sqlalchemy engine that creates a connection
        to the postgresql database
        """
        with open('config.json') as config:
            data = json.load(config)

        password = self.decode_password(data['db']['password'])
        db_conn_string = 'postgresql://' + data['db']['username'] + ':' + password + '@' + \
                     data['db']['hostname'] + ':' + data['db']['port'] + '/' + data['db']['database']

        self.engine = create_engine(db_conn_string)
        try:
            conn = self.engine.connect()
            if conn is not None:
                print("-I- Successful Database Connection")
        except Exception as e:
            print("-W- " + str(e))

    @staticmethod
    def decode_password(p):
        res = base64.b64decode(p)
        return res.decode("utf-8")


    def create_db_dataframe(self, df, table_name):
        """
        Create a new DB table for the DataFrame
        Arguments: pandas DataFrame, DB table_name
        :return: None
        """
        try:
            print("-I- Writing " + table_name + " with DataFrame")
            df.to_sql(name=table_name, con=self.engine, if_exists='replace', index=True)
            print("-I- Write complete.")
        except Exception as e:
            print("-W- " + str(e))

    def append_db_dataframe(self, df, table_name):
        """
        Appends DataFrame to the specified table
        :param df: pandas DataFrame with data to append
        :param table_name: DB table to append
        :return: None
        """
        try:
            print("-I- Appending " + table_name + " with DataFrame")
            df.to_sql(name=table_name, con=self.engine, if_exists='append', index=True)
            print("-I- Append complete.")
        except Exception as e:
            print("-W- " + str(e))

    def fetch_db_dataframe(self, table_name):
        """
        Fetch table rows as DataFrame from DB
        :param table_name: table to query
        :return: DataFrame
        """
        try:
            df = pd.read_sql("SELECT * from " + table_name, self.engine)
            print("-I- Completed read of DataFrame from " + table_name)
            return df
        except Exception as e:
            print("-W- " + str(e))

    def delete_table(self, table_name):
        """
        Function to drop a table from database
        :param table_name: DB table to drop
        :return: None
        """
        try:
            conn = self.engine.connect()
            conn.execute("DROP table " + table_name)
            print("-I- Deleted table " + table_name)
        except Exception as e:
            print("-W- " + str(e))

