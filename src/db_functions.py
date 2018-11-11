import psycopg2

hostname = "smfquant.csu0cjmgqb8i.eu-west-1.rds.amazonaws.com"
port = '8080'
username = 'smfquantuser'
password = 'smfquant2018'
database = 'smfquant'

#testing insert command
def test_insert(cur, column1, column2):
    sql = """ INSERT into testtable (column1, column2)
              VALUES (%s,%s); """
    cur.execute(sql, (column1, column2))

#testing select statement
def test_select(cur, table_name):
    sql = """ SELECT * from %s """
    cur.execute(sql % table_name)
    rows = cur.fetchall()
    for row in rows:
        print(row)
        
# Connect to Postgres DB
def connect():
    conn = None
    try:
        conn = psycopg2.connect(database=database, user=username, host=hostname, port=port, password=password)
        print("Connected to database")
        return conn

    except Exception as e:
        print("Unable to connect to the database:", e)
        return None

# Create tables in the DB
def create_tables():
    commands = (
        """
        CREATE TABLE stocks (
            ticker VARCHAR (255) PRIMARY KEY,
            sector VARCHAR (255),
            p_e FLOAT(4),
            ranking_score SMALLINT
            )
        """,
        """
        CREATE TABLE stock_prices (
            ticker VARCHAR (255) NOT NULL,
            date DATE NOT NULL DEFAULT CURRENT_DATE,
            prices FLOAT(4),
            FOREIGN KEY (ticker)
            REFERENCES stocks (ticker)
            ON DELETE CASCADE
            )
        """
    )
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()

        for command in commands:
            cur.execute(command)

        # close communication with DB
        cur.close()
        # commit changes to DB
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()




#create_tables()
#test_insert(cur, 'test11', 'test12')
#test_select(cur, 'testtable')
#conn.commit()
#cur.close()
#conn.close()