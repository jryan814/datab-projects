##########################
# Tableau Server methods #
# v 2022.01.28 - revampt #
##########################
import datetime as dt
from tqdm import tqdm
import tableauserverclient as TSC
#import tableaudocumentapi as TDA

import config as cfg
#from hybrid_wkbk import WBhybrid
#from sql_repo import SQLfile
import util

class UpdateCheck ():
    active = []
    def __init__(self, s_wb: TSC.WorkbookItem) -> None:
        
        self.checked_date = dt.datetime.strftime(dt.datetime.today(), '%Y.%m.%d')
        #### workbook obj id ####
        self.id = s_wb.id
        #### date of last update ####
        self.last_update = s_wb.updated_at
        self.last_update_str = dt.datetime.strftime(s_wb.updated_at, '%Y.%m.%d')
        
        self.active.append(self)
    
    def __repr__(self) -> str:
        i = self.active.index(self)
        return f'<wkbk_{i}|updated:{self.last_update_str}>'

# Class for Tableau Server methods & attributes
# TODO: method for downloading all workbooks or just updated ones -> create WBH's for each
class TabServer ():
    """New Version for Tableau Server connection"""    
    # to determine chunk size
    n_workers = 8
    def __init__(self, site_name: str=cfg.TEST_TABLEAU_SERVER_INFO['site_name'], 
                       server_url: str=cfg.TEST_TABLEAU_SERVER_INFO['base_url'],
                       token: str=cfg.TEST_TABLEAU_TOKEN['token'],
                       token_name: str=cfg.TEST_TABLEAU_TOKEN['name'],
                       username_auth: bool=False) -> None:

        # site name for __repr__
        self.site_name = site_name
        if username_auth:
        # Generates access auth from username and password
            self.tab_auth = TSC.TableauAuth(**cfg._TABLEAU_USER_LOGIN, site=self.site_name)
        else:
        # Generates access auth from PAT
            self.tab_auth = TSC.PersonalAccessTokenAuth(token_name, token, site_name)
        # server is the main object for interacting with tableau server [not very surprising]
        self.server = TSC.Server(server_url, use_server_version=True)
        # sign in to server using tab_auth
        self.server.auth.sign_in(self.tab_auth) 
        # catalogue of lists as they are generated
        self.list_catalogue = {}
        self.update_objs = None
        #### dict of tableau server api objects
        self.tab_srvr_objs = {
            's_wb': self.server.workbooks,
            's_users': self.server.users,
            's_groups': self.server.groups,
            's_projects': self.server.projects,
            's_subscriptions': self.server.subscriptions,
            's_datasources': self.server.datasources,
            's_schedules': self.server.schedules
        }
        # probably not needed:
        for k, v in self.tab_srvr_objs.items():
            setattr(self, k, v)

    #### generate the catalogue of obj lists
    def get_list_catalogue(self) -> dict:
        """Primary method for getting Tableau Server object lists

        Returns:
            dict: generated tab_srvr_obj = (list(objects), total number of objs)
        """
        for k in self.tab_srvr_objs:
            self._get_item_list(k)
        return self.list_catalogue
    
    #### private function for handling routine
    def _get_item_list(self, item: str='s_wb', *args, **kwargs) -> list:
    # generates the list for a 'single' item (aka object class)
        """Generates item list

        Args:
            item (str, optional): type of object class to get list of all. Defaults to 's_wb'.

        Returns:
            list: obj list
        """    
        _, pagination_item = self.tab_srvr_objs[item].get()
        total_items = pagination_item.total_available
        all_items = [i for i in TSC.Pager(self.tab_srvr_objs[item])]

        if item in ['s_wb', 's_datasources', 's_groups']:
            if item == 's_groups':
                for i in all_items:
                    self.tab_srvr_objs[item].populate_users(i)
            else:
                for i in all_items:
                    self.tab_srvr_objs[item].populate_connections(i)

        self.list_catalogue[item] = (all_items, total_items)
    
    #### Builds the values for update checking
    def build_update_check(self) -> None:
        """Get's workbook objects from catalogue and creates list of UpdateCheck objects"""        
        self.check_new_updates = {}
        for wb in self.list_catalogue['s_wb'][0]:
            update_objs = UpdateCheck(wb)
            self.check_new_updates[update_objs.id] = update_objs.last_update
        self.update_objs = update_objs.active
    
    #### Saves the updated update values
    def _save_update_check(self) -> None:
        """Saves the updated_at dates"""  
        if self.update_objs is not None:      
            util.save_update_check(self.update_objs)

    #### Compare updated_at vs local log
    def compare_update_at(self) -> tuple:
        """Creates a list of wkbk ids that need to be downloaded

        Returns:
            list: workbook ids that have been updated (need to be downloaded)
        """        
        self.no_update_ids = []
        self.update_ids = []
        try:
            last_saved_list = util.load_update_check()
        #### If the file doesn't exist one is created with the current updated_at dates
        except FileNotFoundError:
            print(f']= update check file does not exist\n]= saving now to {cfg.REPORT_UPDATES_FILE}')
            #### utility func for saving the pickle object
            util.save_update_check(self.update_objs)
            for wb in self.update_objs:
                self.update_ids.append(wb.id)
            return self.update_ids
        
        for obj in last_saved_list:
            if obj.last_update == self.check_new_updates[obj.id]:
                self.no_update_ids.append(obj.id)
            else:
                self.update_ids.append(obj.id)
        return (self.update_ids, self.no_update_ids)
    
    #### Update dest_dir
    def download_wkbks(self, wkbk_ids: list, dest_dir: str=cfg.TEST_WKBK_DIR) -> list:
        dl_list = []
        wkbk_id_chunks = util.get_chunks(wkbk_ids, self.list_catalogue['s_wb'][1]//self.n_workers)
        for chunk in tqdm(wkbk_id_chunks, dynamic_ncols=True):
            dl_list += self._download_wkbks(chunk, dest_dir)
        return dl_list
    
    #### private function for downloading chunks of workbooks
    def _download_wkbks(self, wkbk_id_chunk: list, dest_dir: str) -> list:
        retlist = []
        for wb_id in wkbk_id_chunk:
            retlist.append(self.tab_srvr_objs['s_wb'].download(wb_id, dest_dir))
        return retlist

    #### Publish workbooks to server
    def publish_wkbks(self, wb_items: list, mode: str='Overwrite') -> None:
        pub_list = []
        wb_chunks = util.get_chunks(wb_items, len(wb_items)//self.n_workers)
        for chunk in tqdm(wb_chunks, dynamic_ncols=True):
            pub_list += self._publish_wkbks(chunk, mode)
        return pub_list

    def _publish_wkbks(self, wb_chunk: list, mode: str='Overwrite') -> list:
        retlist = []
        for wb in wb_chunk:
            retlist.append(self.tab_srvr_objs['s_wb'].publish(wb, wb.wbd.filename, mode))
        return retlist
    def __repr__(self) -> str:
        return f'<TabServer | site_name:{self.site_name}>'        


if __name__ == '__main__':
    pass

