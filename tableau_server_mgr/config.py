# Config file for Tableau Server ETL
# See requirements.txt for module dependencies

import os
import csv
# import cx_Oracle
import re
import sys

#############################################
# TODO: CREATE SECRETS FILE FOR CREDENTIALS #
#############################################

##############################################################################
# Directory structure:
# - main dir (tableau_server_mgr)
# | All process files (.py)
# |-- data dir
# |     |-- update log (pickle file)
# |     |-- data definitions backup (csv)
# |-- wkbks dir
# |     |-- all workbook files (.twb and .twbx)
# |-- query_files dir
# |     |-- SQL queries from workbooks (.sql)
# |-- updated_wkbks
# |____ |-- updated workbook files needing to be republished (.twb and .twbx)
###############################################################################
# Directory path of this file
MAIN_DIR = os.path.dirname(os.path.abspath(__file__)) # DO NOT EDIT

dirs = ['objs', 'query_files', 'sandbox_wkbks', 'updated_wkbks', 'wkbks']

for dir in dirs:
    if not os.path.isdir(os.path.join(MAIN_DIR, dir)):
        os.mkdir(os.path.join(MAIN_DIR, dir))


## TODO: update token and server info
TEST_TABLEAU_TOKEN = {
    'name': 'name_of_token',
    'token': '223311_ACTUAL_TOKEN_VALUE_113322'
}
# Update with actual Tableau Server info
#### Tableau test server creds
TEST_TABLEAU_SERVER_INFO = {
    'site_url': 'https://tableau-server-site.url',
    'base_url': 'https://base_url_tableau_server',
    'site_name': 'TableauServerSiteName'
}
TEST_TABLEAU_TOKEN.update(TEST_TABLEAU_SERVER_INFO)
## Prod Tableau server token (must be valid)
_TABLEAU_TOKEN = {
    'name': 'prod_token_name',
    'token': 'prod_token_value'
}
## Prod Tableau server user login
_TABLEAU_USER_LOGIN = {
    'username': None,
    'password': None
}
## Prod Tableau server info
_TABLEAU_SERVER_INFO = {
    'site_url': 'https://prod_site.url',
    'base_url': 'https://prod_base.url',
    'site_name': 'ProdSiteName'
}
## DB info
db_connector = 'cx_Oracle'
_creds = {
    'user': 'username',
    'password': 'password',
    'dsn': cx_Oracle.makedsn("oracle_host", 1521, service_name="oracle_service_name")
}

dev_creds = {
    'user': 'username',
    'password': 'password',
    'dsn': cx_Oracle.makedsn("oracle_host", 1521, service_name="oracle_service_name")
}
##### 
# _LIB_DIR and _CFG_DIR NEED TO BE UPDATED to local environment #
# TODO: built-in support for these dependencies
######



#########################################
# Not neccessary to edit anything below #
#########################################


orlib_path = os.path.join(MAIN_DIR, 'objs')
#### TNSNAMES.ORA and Oracle instant client required for implementation
_LIB_DIR = os.path.join(orlib_path, 'orlib', 'instantclient_19_12')

_CFG_DIR = orlib_path



# Directory path of the data folder
DATA_DIR = os.path.join(MAIN_DIR, 'data')

# list of files in the data folder
DATA_FILES = os.listdir(DATA_DIR)

# list of file paths in the data folder
DATA_FILE_PATHS = [os.path.join(DATA_DIR, i) for i in DATA_FILES]

# file path for data definitions (eventually deprecated)
DEFS_FROM_FILE = os.path.join(DATA_DIR, 'rebuilt_data.csv') # Must first be created
DEFS_BACKUP = os.path.join(DATA_DIR, 'defs_backup.csv') # Must first be created

# directory path of wkbks folder
WKBK_DIR = os.path.join(MAIN_DIR, 'wkbks')

# directory of sandbox wkbks folder
TEST_WKBK_DIR = os.path.join(MAIN_DIR, 'sandbox_wkbks')
TEST_WKBK_LIST = os.listdir(TEST_WKBK_DIR)
TEST_WKBK_PATHS = [os.path.join(TEST_WKBK_DIR, i) for i in TEST_WKBK_LIST]
TEST_WKBK_DICT = {k[:k.index('.')]: v for k, v in zip(TEST_WKBK_LIST, TEST_WKBK_PATHS)}

# list of files in the wkbk directory
WKBK_LIST = os.listdir(WKBK_DIR)

# list of file paths in the wkbks folder
WKBK_PATHS = [os.path.join(WKBK_DIR, i) for i in WKBK_LIST]

# dict of workbook names and their file path
WKBK_DICT = {k[:k.index('.')]: v for k, v in zip(WKBK_LIST, WKBK_PATHS)}

# directory path of query_files
SQL_DIR = os.path.join(MAIN_DIR, 'query_files')

# list of files in query files dir
SQL_LIST = os.listdir(SQL_DIR)

# list of query_files file paths
SQL_PATHS = [os.path.join(SQL_DIR, i) for i in SQL_LIST]

# dict of sql file names (no extension) and their file path
SQL_DICT = {k[:k.index('.')]: v for k, v in zip(SQL_LIST, SQL_PATHS)}

# list of connection types that have sql queries (aka database connections)
DB_TYPES = [
    'oracle',
    'sqlserver',
    'snowflake',
    'redshift',
    'googlecloudsql',
    'mysql',
    'postgres',
    'genericodbc',
    # Insert additional values here [Not currently needed]
    # [see tableaudocumentapi.dbclass.KNOWN_DB_CLASSES for valid options]
]

DEFAULT_UPDATE_FILE = os.path.join(MAIN_DIR, 'definition_updates.csv')

REPORT_UPDATES_FILE = os.path.join(DATA_DIR, 'wb_update_check.p')
UPDATED_WB_DIR = os.path.join(MAIN_DIR, 'updated_wkbks')
###################################################
# convenience function for generating a file path #
###################################################
def get_fpath(fname: str, directory: str=MAIN_DIR) -> str:
    return os.path.join(directory, fname)


###############
# intro print #
###############
h_spacer = '-'
v_spacer = '|'
intro_phrase = 'Tableau Server Manager'
version_n = 'version 0.0.8 alpha'
date_dev = '2022.02.10'
intro_txt_len = len(intro_phrase) + 4
intro = f"""
    {h_spacer*intro_txt_len}
    {v_spacer} {intro_phrase} {v_spacer}
    {v_spacer}  {version_n}   {v_spacer}
    {v_spacer} build date: {date_dev} {v_spacer}
    {h_spacer*intro_txt_len}
       
"""



if __name__ == '__main__':
   pass



