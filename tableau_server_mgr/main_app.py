import config as cfg
from tabsrvr import TabServer
import util
# import tabsrvr
from connect import DB
from hybrid_wkbk import WBhybrid as WBH
# imports below might change
import data_dict as dd

from tqdm import tqdm

def update_data_dict(wbh_list: list) -> None:
    """Updates the Data Dictionary from the DLed workbooks

    Args:
        wbh_list (list): List of workbook objects to get field info from
    """
    db = DB()
    d = dd.DataDict(wbh_list, db_object=db)
    report, field, bridge = d.data_structs()
    #### Need to break out db operations
    #### to implement updating instead of drop/insert
    
    db.drop_tables()
    db.build_tables()
    db.insert_values(report, field, bridge)
    d.get_sql_queries()
    # db.conn.close()


###############################
# CLI Menu for proc execution #
#       Manages/executes      #
#         other classes       #
###############################
class Menu ():
    dev_test = True
    def __init__(self, *args, **kwargs) -> None:
        """Le Menu"""        
        self.init_run = True
        self.TS = None
        self.wbhs = []
        self.connect = util.uprompt2('Connect to Tableau Server? y/n', y=True, n=False, q=None)
        if self.connect == 'quit' or self.connect is None:
            print('[= quitting | thank you =]')
            return
        if self.connect:
            self.TS = TabServer(**kwargs)
        self.main_menu(connected=self.connect)
        
    #### Pass through 'main' menu
    def main_menu(self, connected: bool=False) -> None:
        """Pass through main menu

        Args:
            connected (bool, optional): Determines which menu to direct to. Defaults to False.
        """        
        if not connected:
            self.document_menu()
        else:
            self.catalogue = self.TS.get_list_catalogue()
            self.TS.build_update_check()
            self.updated_wb_ids, self.no_update_wb_ids = self.TS.compare_update_at()
            #### Launch the Tableau server menu           
            self.ts_menu()
        
    #### Tableau Server methods   
    def ts_menu(self) -> None:
        """Tableau Server actions
        - Workbooks -> redirects to document menu
        - TODO: implement other methods
        """        
       #### Needs base case if not logged into ts
        print('[:< Tableau Server api Menu >:]')
        task = util.uprompt2(
            '[w]orkbooks, [d]atasources, [u]sers, [g]roups, [s]ubscriptions',
            w=self.document_menu, d='s_datasources', u='s_users', g='s_groups', s='s_subscriptions')
        try:
            # if task is a class method then call the class method
            task()
        except:
            # otherwise get the server object type
            print(f'[:< {task[2:]} methods are still under development')
            #### meanwhile the tab_srvr_objs contains the server object for each component
            server_obj = self.TS.tab_srvr_objs.get(task)
        #### TODO: Implement other methods for tableau server
        self.document_menu()

    def dl_wbs(self, update_all: bool=True) -> list:
        """Downloads the workbooks in chunks -- TODO: selective download option

        Returns:
            list: filenames of downloaded workbooks
        """        
        if update_all:
            self.updated_wb_ids += self.no_update_wb_ids
        fpath_list = self.TS.download_wkbks(self.updated_wb_ids)
        return fpath_list
    
    def get_wbhs(self, update_all: bool=True) -> bool:
        """Load (or download workbooks) workbook hybrid objects

        Returns:
            bool: False it won't download/load every time the document menu is accessed
        """        
        if self.dev_test:
            path_dict = cfg.TEST_WKBK_DICT
        else:
            path_dict = cfg.WKBK_DICT
        
        if self.TS is not None:
            #### Need to ensure entire path is returned by the download method
            path_dict = self.dl_wbs(update_all)
            for wbs, wbd in zip(self.TS.list_catalogue['s_wb'][0], path_dict):
                x = WBH(wbs_obj=wbs, wbd_obj=wbd)
        else:
            print('[:< Loading workbook objects >:]')
            for wbd in tqdm(path_dict.values(), dynamic_ncols=True): # loops through wb paths
                x = WBH(wbs_obj=None, wbd_obj=wbd)
        self.wbhs = x.active #### List of WBH objects
        return False
#### Menu/launcher for document api related functions
#### 
    def document_menu(self) -> None:
        """Document API menu"""        
        print('[:< Tableau Document api Menu >:]')
        
        if self.init_run:
            if self.TS is not None:
                update_all = util.uprompt2('Download [a]ll or only [u]pdated workbooks?', a=True, u=False)
            else:
                update_all = True
            self.init_run = self.get_wbhs(update_all=update_all)
        task = util.uprompt(
            '[S]QL query dl, [u]pdate SQL, [d]ata dictionary update, ([a]dd to sql-under dev)', s=self.get_sql_queries, u=self.update_sql, d=update_data_dict, a=self.add_to_query)
        try:
            task(self.wbhs)
        except Exception as e:
            print(task, e)

    def get_sql_queries(self, wb_list: list=None):
        pass

    #### Only use if making updates to all workbooks needing updating
    def update_sql(self, wb_list: list=None) -> None:

        old_item = input('[:< Old item to replace: ')
        new_item = input('[:< Replace with: ')
        # wkbk_selection = TODO
        for wb in wb_list:
            if wb.query is None:
                continue
            if old_item in wb.query:
                wb.update_sql_query(old_item, new_item)

    def add_to_query(self, wb_list: list, add_other: str=None) -> None:

        #wb_name = util.uprompt2("Which workbook? (testing currently for single workbook use) 'test_blank_wb.twb'")
        add_select = input('String to add to query: ')
        wb_name = 'test_blank_wb'

        for wb in wb_list:
            if wb_name in wb.name:
                idx = wb.query.lower().find('from')
                new_query = wb.query[:idx] + ', ' + add_select + '\n' + wb.query[idx:]
                wb.update_sql_query(wb.query, new_query)



    def update_definitions(self) -> None:
        pass




    
    


if __name__ == '__main__':
    pass

    print(cfg.intro)
    #main()
    go = Menu(cfg.TEST_TABLEAU_TOKEN)

# #### Dev sandbox:
#     print('_____________________\nConnecting to dev sandbox site...')
#     main()

#     print('_____________________\nConnecting to ConstructionReporting site...')
# #### ConstructionReporting:
#     main(site_name=cfg._TABLEAU_SERVER_INFO['site_name'], 
#         server_url=cfg._TABLEAU_SERVER_INFO['base_url'],
#         token=cfg._TABLEAU_TOKEN['token'],
#         token_name=cfg._TABLEAU_TOKEN['name'])
    