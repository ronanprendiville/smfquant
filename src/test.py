# import __hello__
# print("Use this file to practice interacting with git")
# print("Test out writing some random python")
# print("Ronan Brendan Prendiville is a fraud.")
# print("Short Tesla")
# print(2+2)
# print('Hello World')
# print('DSFSDFSDFSDFSDFf')
#
#
# """
# When you are ready to update the online version of the project
# (called as the remote repository, as opposed to your local repository which is on your computer)
# write the following commands in your terminal (found at bottom left of screen):
#
# - "git fetch": This command will go and check what the state of the remote repository is
# - "git status": This will compare your local and the remote repo and will output the status
# - "git pull": If git status says something along the lines of "you are x commits behind master",
# this means that your local repo is outdated and you will need to use git pull to update it.
# - "git add .": Run this command and git will start tracking the changes you have made.
# - "git commit -m "<insert message>" ": This will stage your changes to be uploaded. After -m insert
# a short message in quotes highlighting what was done in this commit e.g git commit -m "Wrote yahoo
# data retrieval function"
# - "git push": This pushes your local changes to the remote repository, updating it. Once this is
# done, others will need to git pull to retrieve your changes.
#
# Note: you may wish to only make an update to 1 file instead of the entire project. To do this
# use git add <filename> as opposed to git add . - the "." implies all files.
#
# """
#
# print("Hey Guys.. what's up!!!")
# print("Hey!")
# print("Testing")
#
# print("Hello Nathan")
#
# print("Hello")
#
# print("Hi")
#
# print("Mathletico > Matrix")
#
# print("Markowitz Team")
# print("git test")
#
# print("HHHHHHHHHHH")
# print("Hello")
#
# # Hey Clodagh, use the following code to insert rows into closing_prices table
# import db_functions as db
#
# # this is an example lst that. Your list needs to be of this format to insert into closing_prices
# lst = [
#         ('2017-11-02','63.107017517089844','165.0301971435547','54.87678146362305','86.27063751220703','1025.5799560546875'),
#         ('2017-11-03','63.507720947265625','169.33978271484375','54.750465393066406','84.7224349975586','1032.47998046875')
#       ]
#
# # to insert into closing_prices
# db.insert_closing_prices(lst)
#
# # prints out the rows from closing_prices
# db.select_closing_prices()
#
# # just a helper function if you want to execute any queries
# db.execute("DELETE from closing_prices")


import numpy as np
import pandas as pd
import yahoo_api as yahoo
import datetime
from sqlalchemy import create_engine

hostname = "smfquant.csu0cjmgqb8i.eu-west-1.rds.amazonaws.com"
port = '8080'
username = 'smfquantuser'
password = 'smfquant2018'
database = 'smfquant'

stocks = ["JNJ", "ABBV", "HD", "DIS"]
start = datetime.datetime(2017, 2, 11)
end = datetime.datetime(2018, 2, 11)

data = yahoo.get_price_dataframe(stocks, start, end)
print(data.head())

engine = create_engine('postgresql://'+username+':'+password+'@'+hostname+':'+port+'/'+database)
# writing to database
data.to_sql(name='data_table', con=engine, if_exists='replace', index=True)
# reading from database
data_again = pd.read_sql('SELECT * from data_table', engine)
# trim out time component from Date column
data_again['Date'] = data_again['Date'].dt.date

print(data_again.head())



           
      



