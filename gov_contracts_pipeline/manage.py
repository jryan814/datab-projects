# 

from multiprocessing import freeze_support
import settings
import build_db
import gov_contract_data_cleaner as gcdc
from pandas import DataFrame
from time import time


class Pipeline ():
    """## Task Pipeline (linear)"""
    def __init__(self):
        self.tasks = []
        
    def task(self, depends_on: object=None) -> object:
        """## Adds tasks to the task list

        Args:
            depends_on (object, optional): Dependencies of the current process. Defaults to None.

        Returns:
            object: Inner function.
        """        
        idx = 0
        if depends_on:
            idx = self.tasks.index(depends_on) + 1
        def inner(f):
            self.tasks.insert(idx, f)
            return f
        return inner

    def run(self, x: DataFrame) -> DataFrame:
        """## Runs pipeline tasks

        Args:
            x (DataFrame): The dataframe arg passed between tasks

        Returns:
            DataFrame: Processed dataframe
        """        
        for i in self.tasks:
            start = time()
            x = i(x)
            end = time()
            print(f'{str(i.__name__)}: {end-start} secs')
        return x

start = time()
# Initiates the pipeline
pipeline = Pipeline()

@pipeline.task()
def first_task(fn: str=None) -> DataFrame:
    """## Runs the multiprocessor transformer pipeline

    Args:
        fn (str, optional): Filename to clean. Defaults to None.

    Returns:
        (DataFrame): Cleaned dataframe
    """
    data = gcdc.exec_pool(fn)
    return data

@pipeline.task(depends_on=first_task)
def second_task(data: DataFrame) -> DataFrame:
    """## DB setup

    TODO: Transition DB to postgres instead of SQLite

    Args:
        data (DataFrame): Dataframe to be passed to next task.

    Returns:
        DataFrame: Passes dataframe to next task.
    """    
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
def last_task(data: DataFrame) -> DataFrame:
    """## Updates the DB

    Args:
        data (DataFrame): Data to be inserted/updated

    Returns:
        DataFrame: [description]
    """    
    sql_data = {}
    db = build_db.DB(False, True)
    num_rows_to_insert = data.shape[0]
    
    # Insertion loops
    # TODO: Update below for use with postgreSQL
    # Sorts table columns alphabetically to lineup with insertion order
    for k in db.all_tbl_cols:
        db.all_tbl_cols[k] = sorted(db.all_tbl_cols[k])
    # Extracts data to be inserted
    for table, cols in db.all_tbl_cols.items():
        sql_data[table] = tuple(list(data[cols].to_records(index=False)))
    # Inserts data for each table
    for table, values in sql_data.items():
        val_ = ('?,'*len(values[0])).rstrip(',')
        col_names = (','.join(db.all_tbl_cols[table]).rstrip(','))
        query = f'''INSERT OR IGNORE INTO {table} ({col_names}) VALUES ({val_})'''
        db.exmany_sql(query, values)

    number_action_rows = db.ex_sql('SELECT COUNT(*) FROM actions')
    # Prints DB statistics
    print('\n', '-'*30)
    print('Total DB rows modified:', db.count_changes())
    print('Rows in actions table:', number_action_rows[0][0])
    print('Number of rows in dataset:', num_rows_to_insert)    
    db.close_conn()
    return data

if __name__ == '__main__':
    # For multiprocessing Pool execution
    freeze_support()
    # Executes the pipeline tasks in correct order
    pipeline.run(None)

    end = time()
    print('-'*30)
    print('seconds to complete:', round(end-start, 1))
    print('-'*30)