#!/usr/bin/env python 3.8.3
# coding: utf-8

# # Government Contracts Data Cleaning
# Pipeline for cleaning the government contracts data downloaded from [USAspending.gov](https://usaspending.gov).  
# Should work on most downloaded datasets with similar criteria (filtered by NAICS code, and small business).

# imports
from multiprocessing import freeze_support, Pool
import pandas as pd
import os
from time import time


# import various settings
from settings import DEF_DATA_FILE, DATA_PATH, rename_map, DEF_CLEAN_PATH

start = time()

def pipeline(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    """Initial transformations

    Args:
        df (pd.DataFrame): Raw dataset

    Returns:
        pd.DataFrame: Initial processed data
    """    
    # No longer needed
    # keep_list = [k for k in rename_map]
    # df = df[keep_list] 
    
    df = df.rename(columns=rename_map)
    df = df.drop(columns=['city_local_government',
                                'award_or_idv_flag',
                                'parent_award_mod_number'])
    df = df[df.columns.sort_values()]

    # Removes any actions with 0 dollars_obligated
    df = df[df['dollars_obligated'] != 0].copy()
    return df

def fill_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """## Clunky NaN resolution (names, ids, and descriptions)
    imputes nan values with data from other columns

    Args:
        df (pd.DataFrame): The data

    Returns:
        pd.DataFrame: Resolved data
    """    
    df['parent_award_agency_name'] = df['parent_award_agency_name'].fillna(df['awarding_agency_name'])
    df['awarding_agency_name'] = df['awarding_agency_name'].fillna(df['parent_award_agency_name'])
    df['parent_award_agency_id'] = df['parent_award_agency_id'].fillna(df['awarding_sub_agency_code'])
    df['award_description'] = df['award_description'].fillna('unknown')
    df['award_id'] = df['award_id'].fillna(df['award_piid_ref'])
    return df

# resolve missing data for international places of performance
def fix_international(df: pd.DataFrame) -> pd.DataFrame:
    """## Fills missing locale info due to internationality

    Args:
        df (pd.DataFrame): The data

    Returns:
        pd.DataFrame: Data with fixed locale data
    """    
    for col in df.columns:
        if 'plop' in col:
            df[col] = df[col].fillna(df['plop_country_code'])
    return df

# Resolve minor name variations
def reformat_names(name: str) -> str:
    """## Resolves most naming inconsistencies

    Args:
        name (str): name string

    Returns:
        str: Resolved name string
    """    
    if pd.isnull(name):
        return 'missing'
    name = name.replace(
        ',', '').replace(
        '.','').replace(
        'INCORPORATED', 'INC').replace(
        'LIMITED LIABILITY COMPANY', 'LLC')
    return name

# Impute missing/err values
def fix_date_issues(date_: str) -> str:
    """## Fixes the date formatting issue/inconsistency
    pandas to_datetime() was unable to resolve some of the date formats

    Args:
        date_ (str): Date string

    Returns:
        str: Reformatted date string
    """    
    if pd.isnull(date_):
        return
    date_ = str(date_)
    if int(date_[:4]) < 2000 or int(date_[:4]) > 2100:
        date_ = '20' + date_[2:]
    return date_

# convert date columns to datetime dtype
def dtype_conversions(df: pd.DataFrame) -> pd.DataFrame:
    """## Converts date columns to datetime

    Args:
        df (pd.DataFrame): target data

    Returns:
        pd.DataFrame: trsnsformed data
    """    
    for col in df.columns:
        if 'fiscal_year' in col:
            continue
        if 'date' in col:
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                print('error with conversion:', col)
    df['year'] = df['action_date'].dt.year
    return df

# add 5 digit zip code
def add_zip_str(df: pd.DataFrame) -> pd.DataFrame:
    """## Creates new column with formatted zip

    Args:
        df (pd.DataFrame): Raw data

    Returns:
        pd.DataFrame: Transformed data
    """    
    cols = df.columns
    for col in cols:
        if 'zip' in col and '_5' not in col:
            series_col = df[col].astype(str)
            df[col + '_5'] = series_col.str[:5]
    return df

# Runs the rest of the pipeline
def run_pipeline2(df: pd.DataFrame) -> pd.DataFrame:
    """## Runs entire pipeline

    Args:
        df (pd.DataFrame): The data to transform.

    Returns:
        pd.DataFrame: Transformed data
    """    
    df = pipeline(df)
    df = fill_nulls(df)
    df = fix_international(df)
    df.loc[:,'recipient_name'] = df.loc[:,'recipient_name'].apply(reformat_names)
    
    date_cols = []
    for col in df.columns:
        if 'date' in col and 'pop' in col:
            date_cols.append(col)

    for d in date_cols:
        df[d] = df[d].fillna(df['action_date'])
        df[d] = df[d].apply(fix_date_issues)

    df = dtype_conversions(df)
    df = add_zip_str(df)
    return df

def make_csv(data: pd.DataFrame, fname: str=None, update: bool=True):
    if update:
        if not fname:
            fname = DEF_CLEAN_PATH
        else:
            fname = os.path.join(DATA_PATH, fname)
        data.to_csv(fname, index=False)


def exec_pipeline(fn: str=None) -> pd.DataFrame:
    """## Execute cleaning pipeline (slow non-parallel version)

    Args:
        fn (str, optional): Filename of dirty data. Defaults to None.

    Returns:
        pd.DataFrame: Cleaned data
    """    
    if fn:
        if '/' in fn or '\\' in fn:
            file_name = fn
        else:
            file_name = os.path.join(DATA_PATH, fn)
    else:
        file_name = DEF_DATA_FILE
    data = pd.read_csv(file_name, usecols=[c for c in rename_map], low_memory=False)
    # data = pipeline(data)
    data = run_pipeline2(data)
    data = data.fillna('unknown')
    make_csv(data)
    return data

def exec_pool(fn: str=None, num_processes: int=5) -> pd.DataFrame:
    """## Executes the Data Cleaning pipeline using multiprocessing pools

    Args:
        fn (str, optional): Filename. Defaults to None.
        num_processes (int, optional): Number of processes and chunks. Defaults to 5.

    Returns:
        pd.DataFrame: Cleaned dataframe
    """
    if not fn:
        fn = os.path.join(DATA_PATH, 'USAspending_award_summaries.csv')
    else:
        fn = os.path.join(DATA_PATH, fn)

    chunks = pd.read_csv(fn, chunksize=100000, usecols=[c for c in rename_map], low_memory=False)
    
    with Pool(num_processes) as pool:
        chunk_results = pool.map(run_pipeline2, chunks)
  
    data = pd.concat(chunk_results)
    data = data.fillna('unknown')

    return data

if __name__ == '__main__':
    # exec_pipeline(os.path.join(DATA_PATH, 'USAspending_award_summaries.csv'))
    freeze_support()
    exec_pool()
    end = time()
    print(f'{end-start} secs')
    