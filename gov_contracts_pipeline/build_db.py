
import sqlite3
import settings


class DB:
    '''
    Automatically builds or rebuilds database, and tables for the gov contracts data.
    Also acts as connection/cursor to sqlite database
    '''
    def __init__(self, new_build=False, row_factory_list=False):
        '''
        Creates data base connection, and cursor as well as initializes class attributes.
        args:
            new_build: (bool) whether to use as connection class or to build the database.
        '''
        db_name = settings.DB_PATH  # db filepath defined in settings.py--for non-sqlite implementation this will need to be changed.
        self.conn = sqlite3.connect(db_name)
        if row_factory_list:
            self.conn.row_factory = lambda cursor, row: [*row]
        self.cur = self.conn.cursor()
        
        self.all_tbl_cols = {}  ## Dictionary of tables and their columns get_table_dict() populates the keys & values
        
        if not new_build: ## Only using class for accessing the db
            self.get_table_dict()
        
        else:
            self.new_build_db() ## Build or rebuild db from scratch
        
        

    def ex_sql(self, *args, **kwargs):
        rows = self.cur.execute(*args)
        self.conn.commit()
        if 'SELECT' in args[0]:
            return rows.fetchall()
    
    def exmany_sql(self, *args, **kwargs):
        rows = self.cur.executemany(*args)
        self.conn.commit()
        if 'SELECT' in args[0]:
            return rows.fetchall()

    def get_tbl_cols(self, tbl_name):
        '''Gets table columns from each table
            args:
                tbl_name: (str) name of the table to get column names from
            returns (list) of column names
        '''
        q = f'PRAGMA table_info({tbl_name});'
        tbl_info = self.cur.execute(q)
        tbl_cols = [i[1] for i in tbl_info if i[1] != 'id']
        return tbl_cols

    def get_table_dict(self):
        '''Builds table dictionary with list of column names for each table'''
        db_info = self.cur.execute("SELECT * FROM sqlite_master WHERE type='table';")
        db_tbls = [i[1] for i in db_info.fetchall() if 'sqlite_sequence' not in i[1]]
        for k in db_tbls:
            self.all_tbl_cols[k] = self.get_tbl_cols(k)
    
    def new_build_db(self):
        
        drops = ['DROP TABLE IF EXISTS actions;',
            'DROP TABLE IF EXISTS awards;',
            'DROP TABLE IF EXISTS businesses;']
        for d in drops:
            self.cur.execute(d)

        build_db = ['''CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY,
            award_id VARCHAR(255),
            recipient_name VARCHAR(255),
            dollars_obligated FLOAT,
            action_date VARCHAR(11),
            FOREIGN KEY (award_id) REFERENCES awards (award_id),
            FOREIGN KEY (recipient_name) REFERENCES businesses (recipient_name)
        );''',
        '''CREATE TABLE IF NOT EXISTS awards (
            id INTEGER PRIMARY KEY,
            award_id VARCHAR(255),
            plop_city VARCHAR(255),
            plop_state_code VARCHAR(255),
            plop_country_code VARCHAR(255),
            naics_code INTEGER NOT NULL
        );''',
        '''CREATE TABLE IF NOT EXISTS businesses (
            recipient_name VARCHAR(255) PRIMARY KEY,
            recipient_city VARCHAR(255),
            recipient_zip_code_5 INTEGER,
            recipient_duns VARCHAR(20)
        );''',
        '''PRAGMA foreign_keys = ON;''']
        for build in build_db:
            self.cur.execute(build)
        self.conn.commit()
        self.get_table_dict()
    
    def count_changes(self):
        return self.conn.total_changes
    
    def close_conn(self):
        self.conn.close()

if __name__ == '__main__':
    d = DB()
    print(d.all_tbl_cols)
