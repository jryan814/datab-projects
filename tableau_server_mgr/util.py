# Various utility and helper functions

import datetime as dt
import re
import os
import pickle
from sys import stdout, exit
import config as cfg

import tableauserverclient as TSC

################################
# Search for ID by object name #
# i.e. user ID, or workbook ID #
################################
def get_id(objs_to_search: list, obj_name: str, return_all: bool=False) -> str:
    """Get ids based on the obj name

    Args:
        objs_to_search (list): objects to search
        obj_name (str): The name or str to search for
        return_all (bool, optional): if dictionary of results should be returned

    Returns:
        str or dict: object id || object's id: object's name
    """    
    obj_id = {}
    obj_1 = None
    for obj in objs_to_search:
        if obj_name in obj.name:
            obj_id[obj.id] = obj.name
        if obj_1 is None:
            obj_1 = obj.id
    if return_all:
        return obj_id
    return obj_1


#########################################
# Create chunks of items for processing #
# Potentially for parallel processing   #
# but currently for efficiency/testing  #
#########################################
def get_chunks(items: list, chunk_size: int) -> list:
    """Breaks items into chunks

    Args:
        items (list): list of objects to be chunked
        chunk_size (int): size of the chunks

    Returns:
        list: list of chunks (lists)
    """
    chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
    return chunks

###################################
# Removes full path and extension #
###################################
def extract_name(fname: str) -> str:
    """Get name from full file path

    Args:
        fname (str): file path to extract from

    Returns:
        str: only the name (strips file extensions & directory paths)
    """
    fname = re.sub(r'[/\\]+', '%', fname)
    try:
        start = fname.rindex('%') + 1
    except:
        start = 0
    try:
        end = fname.rindex('.')
    except:
        end = None

    ret_name = fname[start: end]
    return ret_name

###########################################
# Get a workbook's filepath based on name #
###########################################
def generate_fpath(name: str) -> str:
    """Gets a workbook's local filepath from it's base

    Args:
        name (str): Name of workbook to find the path for

    Returns:
        str: the full filepath of the workbook
    """    
    
    if '\\' in name or '/' in name:
        if os.path.exists(name):
            return name
    
    if '.' in name:
        name = name[name.index('.')]
    try:
        fpath = cfg.WKBK_DICT[name]
    except KeyError:
        print(f'{name} does not exist in workbook directory')
        return None
    return fpath

######################
# Field name cleaner #
######################
def clean_field_names(name: str) -> str:

    field_name = re.sub(r'[\[\]]+', '', name.upper())
    field_name = re.sub(r'%', 'ZZZ', field_name)
    field_name = re.sub(r'[\W]', ' ', field_name).rstrip().strip()
    field_name = re.sub(r'ZZZ', '%', field_name)
    field_name = re.sub(r'[ ]+', '_', field_name).strip('_').rstrip('_')
    return field_name

#################################
# Create pickle file of objects #
# used to check for updated wbs #
#################################
def save_update_check(update_record_objs: dict, fname: str=cfg.REPORT_UPDATES_FILE) -> None:
    """Pickle list of wb objects updated_at

    Args:
        update_record_objs (list): list of objs to be pickled
    """
    pickle.dump(update_record_objs, open(fname, 'wb'))

def load_update_check(fname: str=cfg.REPORT_UPDATES_FILE) -> list:
    """Loads the list of wb objects updated_at

    Args:
        fname (str, optional): filename to open. Defaults to cfg.REPORT_UPDATES_FILE.

    Returns:
        list: the pickled objects
    """
    with open(fname, 'rb') as g:
        return pickle.load(g)
    #return pickle.load(open(fname, 'rb'))

##############################
# Builds the data dictionary #
# Currently only from file   #
# TODO: Query DB instead of  #
#       file for generating  #
##############################

def generate_data_dict(from_file: bool=True) -> tuple:
        import csv
        """Generates data dictionary {field name: field description}

        Args:
            from_file (bool, optional): For future use when data is in db. Defaults to True.

        Returns:
            tuple(dicts): data_definitions, data_types, data_tags
        """        
        data_definitions = {}
        data_types = {}
        data_tags = {}
        if from_file:
            with open(cfg.DEFS_FROM_FILE, 'r') as f:
                reader = csv.DictReader(f)
                for k in reader:
                    data_definitions[k['COL_NAME']] = k['FIELD_DESCRIPTION']
                    data_types[k['COL_NAME']] = k['DTYPE']
                    data_tags[k['COL_NAME']] = k['TAGS']
            return data_definitions, data_types, data_tags

def exec_loop():
    print('running')
    return 'exec_loop'

###################################
# User input convenience function #
###################################

def uprompt(prompt: str, **kwargs) -> str:
    """More advance version of user input y/n

    Args:
        prompt (str): input prompt

    Returns:
        str: value of the input
    """
    def_options = {
        'y': True,
        'n': False
        }
    
    def_options.update(kwargs)
    print(f'[:< {prompt}')
    
    # for k, v in kwargs.items():
    #     print('[:< ', end='')
    #     print(f'[{k}]={v} ')
    while True:
        uin = input('[: ').lower()
        if 'q' in uin.lower():
            break
        if def_options.get(uin) is not None:
            return def_options[uin]
    return 'quit'

def cprint(*args) -> None:

    for arg in args:
        print(f'[= {arg}')

def uprompt2(prompt: str, *args, **kwargs) -> str:

    print(f'[:>> {prompt}')
    while True:
        uin = input('[: ').lower()
        if uin == 'q':
            return exit()
        if kwargs.get(uin) is not None:
            return kwargs[uin]

if __name__ == '__main__':
    pass
    #cprint('hi', 'why')
    
    uprompt('what to do', y=False, n=exec_loop)