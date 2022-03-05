##############################################
# Connection classes 
# Currently only tableau server
# in a test environment
# Using personal access token
##############################################
# Connecting the database requires cx_Oracle
# (and an oracle database to connect to)

import config as cfg
import tableauserverclient as TSC
import cx_Oracle


        
############################
#  Database Connection &   #
#    SQL execution class   #
############################
class DB ():

    def __init__(self, creds: dict=cfg.dev_creds) -> None:

        try:
            cx_Oracle.init_oracle_client(lib_dir=cfg._LIB_DIR, config_dir=cfg._CFG_DIR)
        except Exception as e:
            print('->', e, '<-')
            return
        
        self.conn = cx_Oracle.connect(**creds)
        self.cur = self.conn.cursor()

    def build_tables(self) -> None:

        # TODO: develop more dynamic method to create tables
        self.create_queries = [
            
            ## fields table
            """
            CREATE TABLE tab_fields (
                field_id NUMBER GENERATED AS IDENTITY,
               -- 
                field_name varchar2(255),
                field_description varchar2(255),
                field_dtype varchar2(12),
                field_tag varchar2(12),
                CONSTRAINT tab_fields_pk PRIMARY KEY(field_id)
                
            )
            """, ## fields table
            ## reports table
            """
            CREATE TABLE tab_reports (
                report_id NUMBER GENERATED AS IDENTITY,
               -- 
                report_name varchar2(255),
                project_name varchar2(255),
                -- server_report_id varchar2(255),
                -- last_update date,
                -- owner_id varchar2(255),
                CONSTRAINT tab_reports_pk PRIMARY KEY(report_id)
            )
            """, ## reports table
            ## bridge staging table
            """
            CREATE TABLE tab_bridge_staging (
                report varchar(255),
                field varchar(255)
            )
            """,
            ## bridge table
            """
            CREATE TABLE tab_report_fields (
                report_id INT NOT NULL,
                field_id INT NOT NULL,

                CONSTRAINT fk_reports
                FOREIGN KEY(report_id) REFERENCES tab_reports(report_id)
                ON DELETE CASCADE,

                CONSTRAINT fk_fields
                FOREIGN KEY(field_id) REFERENCES tab_fields(field_id)
                ON DELETE CASCADE
            )
            """
        ]
        for query in self.create_queries:
            self.cur.execute(query)
        self.conn.commit()
        print('--> Success creating tables <--')
    
    def build_acronym_table(self) -> None:

        acro_create = """CREATE TABLE tab_acronyms (
            acronym varchar2(5),
            definition varchar2(150),
            alternate_acronym varchar2(5)
        )
        """
        try:
            self.cur.execute(acro_create)
        except:
            print('|= Acronym table already exists.')
            return
        self.conn.commit()

    def drop_tables(self) -> None:
        
        tables = ['tab_report_fields', 'tab_reports', 'tab_fields', 'tab_bridge_staging']

        drops = [
            'DROP TABLE tab_report_fields',
            'DROP TABLE tab_reports',
            'DROP TABLE tab_fields',
            'DROP TABLE tab_bridge_staging',
            ]
        for i, drop in enumerate(drops):
            try:
                self.cur.execute(drop)
            except Exception as x:
                if tables[i] != 'tab_bridge_staging':
                    print(x, ' -- ', tables[i])
        self.conn.commit()

    def insert_values(self, reports_data: list, fields_data: list, bridge_data: list) -> None:
        """Performs table inserts to populate db tables

        Args:
            fields_data (list): data for tab_fields table
            reports_data (list): data for tab_reports table
            bridge_data (list): data for tab_bridge_staging table
        """
        try:
            # Fields table
            self.cur.executemany('''INSERT INTO tab_fields (field_name, field_description, field_dtype, field_tag) VALUES(:f_name, :f_descrip, :f_dtype, :f_tag)''', fields_data)
        except Exception as e:
            print(f'Fields table failed to populate - {e}')
        
        try:
            self.cur.executemany('''INSERT INTO tab_reports (report_name, project_name) VALUES(:r_name, :p_name)''', reports_data)
        except Exception as e:
            print(f'Reports table failed to populate - {e}')
        
        try:
            self.cur.executemany('''INSERT INTO tab_bridge_staging (report, field) VALUES(:rep, :field)''', bridge_data)
        except Exception as e:
            print(f'Bridge staging failed to populate - {e}')
        
        build_bridge_table = """
        INSERT INTO tab_report_fields
        SELECT 
            tr.report_id,
            tf.field_id
        FROM
            tab_bridge_staging bs
        LEFT JOIN tab_reports tr ON tr.report_name = bs.report
        LEFT JOIN tab_fields tf ON tf.field_name = bs.field
        """
        try:
            self.cur.execute(build_bridge_table)
        except Exception as e:
            print('Bridge table issue: ', e)
        try:
            self.cur.execute('DROP TABLE tab_bridge_staging')
        except:
            pass
        self.conn.commit()
        self.table_check()


    def table_check(self) -> None:

        fields = self.cur.execute('SELECT COUNT(field_id) FROM tab_fields').fetchall()
        reports = self.cur.execute('SELECT COUNT(report_id) FROM tab_reports').fetchall()
        report_fields = self.cur.execute('SELECT COUNT(field_id) FROM tab_report_fields').fetchall()
        print(f"""
        ----------
            fields table: {fields[0][0]} rows
           reports table: {reports[0][0]} rows
            bridge table: {report_fields[0][0]} rows
        ----------
        """)
        self.conn.close()

    def retrieve_definitions(self) -> list:

        rows = self.cur.execute('SELECT * FROM tab_fields')
        cols = [col[0] for col in self.cur.description]
        _data = {row[1]: dict(zip(cols, row)) for row in rows.fetchall()}
        return _data
    
    def _retrieve_definitions(self) -> list:

        rows = self.cur.execute('SELECT * FROM tab_fields')
        cols = [col[0] for col in self.cur.description]
        _data = [dict(zip(cols, row)) for row in rows.fetchall()]
        return _data



if __name__ == '__main__':
    pass
    db = DB()
    # db.drop_tables()
    # db.build_tables()

   