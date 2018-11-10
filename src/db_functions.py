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
        
#connecting to database
def connect():
    try:
        conn = psycopg2.connect(database=database, user=username, host=hostname, port=port, password=password)
        print("Connected to db")
        cur = conn.cursor()
        return cur, conn

    except Exception as e:
        print("I am unable to connect to the database:", e)
        return None

cur, conn = connect()
test_insert(cur, 'test11', 'test12')
test_select(cur, 'testtable')
conn.commit()
cur.close()
conn.close()