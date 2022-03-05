import config as cfg

from connect import DB
import csv

import os
import util

class UpdateDataDict ():
    header_remap = {
        'FIELD_ID': 'fid',
        'FIELD_NAME': 'fn',
        'FIELD_DESCRIPTION': 'fd',
        'FIELD_DTYPE': 'dt',
        'FIELD_TAG': 'ft'
    }
    def __init__(self, update_file: str=cfg.DEFAULT_UPDATE_FILE) -> None:
        
        self.db = DB(cfg.dev_creds)        
        #### Queries database for the field table
        self.current_dd = self.db.retrieve_definitions()
        #db.conn.close()
        self.updated_dd = []
        self.updates = None
        exists = None
        try:
            exists = os.path.exists(update_file)
        except Exception as ae:
            print(']:< Could not locate file - [enter] to return, [file path] to retry')
            update_file = input('[: ')
            exists = os.path.exists(update_file)
        
        if not exists:
            self.db.conn.close()
            return

        self.update_file_path = update_file
        self.load_update_file()
    
    def compare_dict(self, updated_item: dict) -> dict:

        ret_item = {}
        fid = 'FIELD_ID'
        fn = 'FIELD_NAME'
        new_item = True
        for k, v in self.current_dd[updated_item[fn]].items():
            if k == fid:
                ret_item[k] = v
                continue
            if updated_item[k] != v or v is None:
                ret_item[k] = updated_item[k]
            else:
                ret_item[k] = v
                #continue
        return ret_item
                

    def load_update_file(self) -> list:

        with open(self.update_file_path, 'r') as f:
            self.updates = list(csv.DictReader(f))
        for d in self.updates:
            d['FIELD_NAME'] = util.clean_field_names(d['FIELD_NAME'])
        
            if d['FIELD_NAME'] in self.current_dd:
                self.updated_dd.append(self.compare_dict(d))
            else:
                self.updated_dd.append(d)
        return self.updated_dd

    #### Updates database
    def update_data_definitions(self) -> list:
        
        query = """
        UPDATE tab_fields
        SET field_name = :fn,
            field_description = :fd,
            field_dtype = :dt,
            field_tag = :ft
        WHERE field_id = :fid"""
        for k, v in self.header_remap.items():
            for x in self.updated_dd:
                x[v] = x.pop(k)
        try:
            self.db.cur.executemany(query, self.updated_dd)
        except Exception as e:
           print(e)
           self.db.conn.close()
        self.db.conn.commit()
        fids = [i['fid'] for i in self.updated_dd]
        
        cnt = 0
        for fid in fids:
            r = self.db.cur.execute('SELECT * FROM tab_fields WHERE FIELD_ID IN :ff', ff=fid)
            cnt += 1
        if cnt == len(self.updated_dd):
            print(f'[:< Successfully updated {len(self.updated_dd)} row(s)')
        self.db.conn.close()
        


if __name__ == '__main__':
    x = UpdateDataDict()
    x.update_data_definitions()
    #print(x.updated_dd)