
import settings
import build_db
import pandas as pd
import sqlite3


# db = build_db.DB(False, True)
# # #db.conn.row_factory = lambda cursor, row: row[0]
# d = db.ex_sql('SELECT recipient_name from businesses')

# data = pd.read_csv(settings.DEF_CLEAN_PATH, usecols=['recipient_name'], low_memory=False)
# data = data.drop_duplicates(subset='recipient_name')
# tt = data[~data['recipient_name'].isin(d)]
# print(d[:5])
# # db.conn.row_factory = lambda cursor, row: list(row)
# # db.cur = db.conn.cursor()
# # rows = list(db.ex_sql("SELECT * FROM actions limit 5;"))
# # print(db.ex_sql('SELECT recipient_name from businesses limit 4'))
# # x = db.ex_sql('SELECT recipient_name FROM businesses WHERE recipient_name = ;', )
# print(tt)

# d = pd.read_csv(settings.DEF_CLEAN_PATH)
# print(d.head(), d.shape)

def test_print(phrase):
    top = '-'*30
    print(top)
    i = input(phrase)
    return i

# r = test_print('Overwrite existing file? ')
# print(r)
