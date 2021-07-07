#!/usr/bin/env python
# coding: utf-8

# # Government Contracts Data Cleaning
# Pipeline for cleaning the government contracts data downloaded from [USAspending.gov](https://usaspending.gov).  
# Should work on most downloaded datasets with similar criteria (filtered by NAICS code, and small business).

# imports
import pandas as pd
import os
# import numpy as np
# import datetime as dt

from settings import DEF_DATA_FILE, DATA_PATH, rename_map, DEF_CLEAN_PATH



def pipeline(df, *args, **kwargs):
    keep_list = [k for k in rename_map]
    df = df[keep_list]
    df = df.rename(columns=rename_map)
    df = df.drop(columns=['city_local_government',
                                'award_or_idv_flag',
                                'parent_award_mod_number'])
    df = df[df.columns.sort_values()]
    df = df[df['dollars_obligated'] != 0].copy()
    return df

def fill_nulls(df):
    df['parent_award_agency_name'] = df['parent_award_agency_name'].fillna(df['awarding_agency_name'])
    df['awarding_agency_name'] = df['awarding_agency_name'].fillna(df['parent_award_agency_name'])
    df['parent_award_agency_id'] = df['parent_award_agency_id'].fillna(df['awarding_sub_agency_code'])
    df['award_description'] = df['award_description'].fillna('unknown')
    df['award_id'] = df['award_id'].fillna(df['award_piid_ref'])
    df['recipient_duns'] =  df['recipient_duns'].astype('object')
    return df

# resolve missing data for international places of performance
def fix_international(df):
    for col in df.columns:
        if 'plop' in col:
            df[col] = df[col].fillna(df['plop_country_code'])
    return df

# Resolve minor name variations
def reformat_names(name):
    if pd.isnull(name):
        return 'missing'
    name = name.replace(
        ',', '').replace(
        '.','').replace(
        'INCORPORATED', 'INC').replace(
        'LIMITED LIABILITY COMPANY', 'LLC')
    return name

# Impute missing/err values
def fix_date_issues(date_):
    if pd.isnull(date_):
        return
    date_ = str(date_)
    if int(date_[:4]) < 2000 or int(date_[:4]) > 2100:
        date_ = '20' + date_[2:]
    return date_

# convert date columns to datetime dtype
def dtype_conversions(df):
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
def add_zip_str(df):
    cols = df.columns
    for col in cols:
        if 'zip' in col and '_5' not in col:
            series_col = df[col].astype(str)
            df[col + '_5'] = series_col.str[:5]
    return df

# Runs the rest of the pipeline
def run_pipeline2(df):
    
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

def make_csv(data, fname=None, update=True):
    if update:
        if not fname:
            fname = DEF_CLEAN_PATH
        else:
            fname = os.path.join(DATA_PATH, fname)
        data.to_csv(fname, index=False)

def exec_pipeline(fn=None):
    '''
    Executes the entire cleaning of the data.
    Creates new csv_file of the cleaned data (named 'cleaned_data.csv' in the data directory)
    args:
        fn: (str, or path-like) file name for dirty data
    returns:
        cleaned data
    '''
    if fn:
        if '/' in fn or '\\' in fn:
            file_name = fn
        else:
            file_name = os.path.join(DATA_PATH, fn)
    else:
        file_name = DEF_DATA_FILE
    data = pd.read_csv(file_name, low_memory=False)
    data = pipeline(data)
    data = run_pipeline2(data)
    data = data.fillna('unknown')
    make_csv(data)
    return data

       
    

    

    
    
