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
        """,
        """
        CREATE TABLE closing_prices (
            date DATE NOT NULL DEFAULT CURRENT_DATE,
            well FLOAT,
            aapl FLOAT,
            wfc FLOAT,
            wdc FLOAT,
            goog FLOAT
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

# manual execute function
def execute(sql):
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute(sql)
        cur.close()
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()

# insert into closing_prices
def insert_closing_prices(lst):
    """ insert into closing prices takes a list of type -
        lst = [
            ('2017-11-02','63.107017517089844','165.0301971435547','54.87678146362305','86.27063751220703','1025.5799560546875'),
            ('2017-11-03','63.507720947265625','169.33978271484375','54.750465393066406','84.7224349975586','1032.47998046875')
          ]
    """
    sql = """ INSERT into closing_prices VALUES (%s,%s,%s,%s,%s,%s) """
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        cur.executemany(sql, lst)
        cur.close()
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()

# fetch rows from closing_prices
def select_closing_prices():
    sql = """ SELECT * from closing_prices """
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            print(row)
        cur.close()
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()

#execute("DROP TABLE stock_prices")
#execute("DROP TABLE stocks")


#create_tables()
#test_insert(cur, 'test11', 'test12')
#test_select(cur, 'testtable')
#conn.commit()
#cur.close()
#conn.close()