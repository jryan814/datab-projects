
import settings
import build_db
import gov_contract_data_cleaner as gcdc
from pandas import read_csv
from time import time



class Pipeline:
    def __init__(self):
        self.tasks = []
        
    def task(self, depends_on=None):
        idx = 0
        if depends_on:
            idx = self.tasks.index(depends_on) + 1
        def inner(f):
            self.tasks.insert(idx, f)
            return f
        return inner
    def run(self, x):
        for i in self.tasks:
            x = i(x)
        return x
start = time()
pipeline = Pipeline()

@pipeline.task()
def first_task(fn=None, ask=settings.DOES_CLEAN_EXIST):
    '''
    Runs cleaning pipeline on data
    args:
        fn: [optional] (str or path-like) if None the default './data/dirty_data.csv' is used
        returns:
            pandas.DataFrame
    '''
    # check for existing file and clean data
    if not ask:
        data = gcdc.exec_pipeline(fn)
        return data
    else:
        run_process = input('Cleaned file already exists, replace y/n? ')
        if 'y' in run_process:
            data = gcdc.exec_pipeline(fn)
            return data
        else:
            data = read_csv(settings.DEF_CLEAN_PATH, low_memory=False)
            return data
        
@pipeline.task(depends_on=first_task)
def second_task(data):
    '''
    Sets up database and closes connection
    args:
        data: Passes the data from previous function to next task
    '''
    # Check if database file exists
    need_to_create = settings.RUN_DB_SETUP
    if need_to_create:
        db = build_db.DB(True)
        db.close_conn()
    else:
        ask_rebuild = input('Rebuild database (clears all records) y/n? ')
        if 'y' in ask_rebuild:
            if 'y' in input('ARE YOU SURE YOU WANT TO CLEAR AND REBUILD DB? '):
                db = build_db.DB(True)
                db.close_conn()
    return data

@pipeline.task(depends_on=second_task)
def last_task(data):
    '''
    Inserts values into database
    '''
    fact_table = ['actions']
    dim_tables = ['businesses', 'awards']
    sql_data = {}
    db = build_db.DB(False, True)
    num_rows_to_insert = data.shape[0]
    # insertion functionsn

    for k in db.all_tbl_cols:
        db.all_tbl_cols[k] = sorted(db.all_tbl_cols[k])
    
    for table, cols in db.all_tbl_cols.items():
        sql_data[table] = tuple(list(data[cols].to_records(index=False)))
    for table, values in sql_data.items():
        val_ = ('?,'*len(values[0])).rstrip(',')
        col_names = (','.join(db.all_tbl_cols[table]).rstrip(','))
        query = f'''INSERT OR IGNORE INTO {table} ({col_names}) VALUES ({val_})'''
        db.exmany_sql(query, values)
    number_action_rows = db.ex_sql('SELECT COUNT(*) FROM actions')
    print('\n', '-'*30)
    print('Total DB rows modified:', db.count_changes())
    print('Rows in actions table:', number_action_rows[0][0])
    print('Number of rows in dataset:', num_rows_to_insert)    
    db.close_conn()
    return data

pipeline.run(None)
end = time()
print('-'*30)
print('seconds to complete:', round(end-start, 1))
print('-'*30)