#############################
# Managing and updating the #
#      Data Dictionary      #
#############################
#---------------------------#
#> Run this script directly #
#> to circumvent the server #
#> connection/objects       #
#---------------------------#

import config as cfg
#from connect import ConnTab as CT
from util import get_chunks
import util
#import tableauserverclient as TSC
import tableaudocumentapi as TDA
#import re
from connect import DB
from hybrid_wkbk import WBhybrid as WBH
from sql_repo import SQLfile
import csv



##################################################
# ONLY for files that already exist in wkbks dir #
##################################################
class DataDict ():

    def __init__(self, wbh_list: list, from_file: bool=False, db_object: DB=None) -> None:
        
        self.db = db_object
        self.report_objs = wbh_list
        self.all_fields = []
        self.col_report_dict = {}
       # self.flist = cfg.WKBK_PATHS
        self.from_file = from_file
        self.data_definitions = self.data_dict_lookup(self.from_file)
        self.quick_build()
        self.get_all_fields()

    def quick_build(self) -> None:
        self.report_names = [i.name for i in self.report_objs]
    
    def get_all_fields(self) -> None:

        self.data_dict = self.data_dict_lookup(self.from_file)

        for rep in self.report_objs:
            self.all_fields += rep.get_fields()
        self.raw_fields = self.all_fields
        self.all_fields = list(set(self.all_fields))

        for field in self.all_fields:
            if field not in self.data_dict:
                self.data_dict[field] = 'No definition'
            if field not in self.col_report_dict:
                self.col_report_dict[field] = []
            for r in self.report_objs:
                if field in r.field_list:
                    self.col_report_dict[field].append(r.name)
        return self.col_report_dict

    def get_sql_queries(self) -> None:

        for wb in self.report_objs:
            wb.create_sql_file()

    def data_structs(self, build_defs_file: bool=False) -> tuple:

        # report_table = report_name, project_name
        # field_table = field_name, definition, *other fields tbd
        # bridge_table = report_name, field_name
        data_dict = self.data_dict_lookup(self.from_file)

        reports = [(rep_name, '01 Productivity') for rep_name in self.report_names]
        
        fields = [(k, v, self.data_types[k], self.data_tags[k]) for k, v in data_dict.items()]
        bridge = []
        for col, r_list in self.col_report_dict.items():
            if col not in data_dict:
                fields.append((col, None, None, None))
                
            for r in r_list:
                bridge.append((r, col))

        if build_defs_file:
            header = [('COL_NAME', 'FIELD_DESCRIPTION', 'DTYPE', 'TAGS')]
            with open(cfg.DEFS_BACKUP, 'w', newline='') as f:
                csv_writer = csv.writer(f)
                csv_writer.writerows(header + fields)
        
        return reports, fields, bridge

    def data_dict_lookup(self, from_file: bool) -> dict:

        data_definitions = {}
        self.data_types = {}
        self.data_tags = {}
        cn = 'COL_NAME'
        dt = 'DTYPE'
        ft = 'TAGS'
        if from_file:
            with open(cfg.DEFS_BACKUP, 'r') as f:
                reader = list(csv.DictReader(f))
        else:
            reader = self.db._retrieve_definitions()
            cn = 'FIELD_NAME'
            dt = 'FIELD_DTYPE'
            ft = 'FIELD_TAG'

        for k in reader:
            data_definitions[k[cn]] = k['FIELD_DESCRIPTION']
            self.data_types[k[cn]] = k[dt]
            self.data_tags[k[cn]] = k[ft]
        
        return data_definitions



if __name__ == '__main__':
    pass
    go = False # util.user_yn('Will drop and rebuild tables based on local files only! proceed? y/n')
    if go:
        manual_local_etl()
    pass        
    