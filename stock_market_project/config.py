# python >= 3.8.3
##################################################
# Config settings and helper functions v 0.0.0.1 #
#      For stock_market_project v 0.0.1          #
##################################################


import os

from datetime import datetime as dt
from datetime import date
from dateutil.parser import parse

# development mode switch
DEV_MODE_ON = True

# File and directory paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(ROOT_DIR, 'data')

ML_DIR = os.path.join(ROOT_DIR, 'ml')

TODAY_DATE = date.today()

STOCK_TICKER = '^GSPC'

START_DATE = '1970-01-01'

# funcs for generating file paths [don't need to import os for creating new file paths]
def new_fpath(fname, directory_var=ROOT_DIR):
    """Generates a new file path in the directory_var (does not create actual file)

    Args:
        fname (str): the new files name (e.g. new_file.txt)
        directory_var (config variable or os.path, optional) default: ROOT_DIR choose directory of file

    Returns:
        str: the full filepath
    """    
    return str(os.path.join(directory_var, fname))



# parser dates for data type id
def is_date(strings, tolerance=1):
    """Test if string is a date/time

    Args:
        strings (str, or list, array-like): The string or list of strings to be evaluated.
        tolerance (float, optional): Percent of test runs that are allowed to fail and still return True (only applies if strings is an iterable). Defaults to .5.

    Returns:
        [bool]: Whether or not the strings is/are most likely dates/times.
    """    
    
   
    def test_string(string):
        if 25 < len(str(string)) < 4:
            return None
        try:
            parse(string)
        except:
            return False
        return True
    
    if isinstance(strings, (str)):
        return test_string(strings)
    else:
        test_count = 0
        success_count = 0
        max_test = len(strings) - 1

        for string in strings:
            test1 = test_string(string)
            if test1:
                success_count += 1
                test_count += 1
            else:
                test_count += 1
        if isinstance(tolerance, int) and tolerance > 1:
            tolerance = test_count - tolerance
            if success_count >= abs(tolerance):
                return True
            else:
                return False
        if success_count / test_count >= tolerance:
            return True
        else:
            return False

            

if __name__ == '__main__':
    test = is_date(['10-15-1984', '1.1.0', '20-20-20', '12-12-1912', 'may 5 2020', 'a520', 'asbsf'])
    test2 = is_date('13-31-13')
    print(test, test2)
    print(TODAY_DATE)


