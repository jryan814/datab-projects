# sql_repo.py
# created on 2022.01.26
# Creates .sql files by extracting queries from tableau workbook**
# **Requires local copy of workbook
####################################
# TODO: Implement git capabilities #           
####################################
import config as cfg
              
#### TODO: add sql update method?

class SQLfile ():

    def __init__(self, wbh_name: str, query: str) -> None:
        
        self.file_name = wbh_name
        self.query = query

    def write_file(self, file_dir: str=cfg.SQL_DIR) -> None:

        fpath = cfg.get_fpath(self.file_name, file_dir)
        with open(fpath, 'w') as f:
            f.writelines(self.query)


if __name__ == '__main__':
    pass
