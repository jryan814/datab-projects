import config as cfg
import tableauserverclient as TSC
import tableaudocumentapi as TDA
#import data_dict as dd
from sql_repo import SQLfile
import util
import re


class FieldInfo ():

    def __init__(self, field_obj: TDA.Field) -> None:
        self.field_obj = field_obj
        self.name = util.clean_field_names(field_obj.name)
        self.calc = field_obj.calculation
        if self.calc is None:
            self.source = 'Source Data'
        else:
            self.source = 'Calculated Field'
        self.datatype = field_obj.datatype
        self.description = field_obj.description

############################
# Combine workbook classes #
#  server workbook item &  #
#    doc workbook item     #
############################
class WBhybrid (TDA.Workbook):
    active = []
    def __init__(self, wbs_obj: TSC.WorkbookItem=None, wbd_obj: TDA.Workbook=None) -> None:
        """Combines 2 flavors of workbook objects

        Args:
            wbs_obj (TSC.WorkbookItem, optional): Tableau server WorkbookItem. Defaults to None.
            wbd_obj (TDA.Workbook, optional): Tableau document Workbook (item). Defaults to None.
        """        
        
        #### Server WorkbookItem
        self.wbs = wbs_obj
        #### Document Workbook (item)
        if isinstance(wbd_obj, str):
            wbd_obj = TDA.Workbook(wbd_obj)
        self.wbd = wbd_obj
        #### Name attribute
        if self.wbd is not None:
            self.name = util.extract_name(self.wbd.filename)
        elif self.wbs is not None:
            self.name = self.wbs.name
        else:
            self.name = 'name_error'
        #### Attempt to get SQL query
        self.query = self.get_sql()
        #### Root of the workbook xml - Not accessing the correct attr
        self.xml_root = self.wbd._workbookRoot
        self.xml_tree = self.wbd._workbookTree
        #### Add to active list
        self.active.append(self)

    def get_fields(self) -> list:
        
        self.field_list = []
        self.field_dict = {}
        #### Iterate through data sources and extract/clean field name
        for ds in self.wbd.datasources:
            #### Iterate through the 'fields' values
            for i, f in enumerate(ds.fields.values()):
                field = util.clean_field_names(f.name)
                self.field_list.append(field)
                #### self.field_dict stores the field name and its FieldInfo class
                self.field_dict[field] = FieldInfo(f)
        return self.field_list

    def get_sql(self, wkbk_obj: TDA.Workbook=None, simple: bool=True) -> str:
        """Get SQL query from workbook

        Args:
            wkbk_obj (TDA.Workbook): The workbook to extract the query from.
            simple (bool, optional): Not used, but might be for workbooks with multiple connections. Defaults to True.

        Returns:
            str: [description]
        """        
        #### Unless specified the current workbook document object is used
        if wkbk_obj is None:
            wkbk_obj = self.wbd
        if simple:
        #### Iterate through data sources
            for i, ds in enumerate(wkbk_obj.datasources):
                #### try to get sql query
                try:
                    sql_list = ds._get_custom_sql()[0]
                #### catch IndexError exception 
                except IndexError as x:
                    # if i != 0:
                    #     print(x)
                    continue
            return sql_list.text 
        else:
            return

    def create_sql_file(self) -> None:
        """### Writes SQL query to file"""
        if self.query is None:
            print(f'{self.name} query = {self.query}')
            #self.query = '--> Query is either hidden or one does not exist <--'
            return
        self.sql_file = SQLfile(self.name+'.sql', self.query)

        try:
            self.sql_file.write_file()
        except Exception as e:
            print(f'Failed to get sql query for {self.name} -- {e}')
            return    

    #### TODO: Develop/implement search method
    def search_query(self, search_term: str) -> dict:

        if self.query:
            if re.search(search_term.lower(), self.query.lower()):
                pass

    def update_sql_query(self, old_item: str, replace_with: str, dest_dir: str=cfg.UPDATED_WB_DIR, *args, **kwargs) -> object:
        """Update SQL query and resave\\
            Changing kwargs values has not been tested/implemented

        Args:
            old_item (str): item to be replaced.
            replace_with (str): what is replacing old_item

        Returns:
            object: currently returns None - might change
        """

        update_kwargs = {
            'parent_dir': 'datasources',
            'child_dir': 'connection',
            'search_tag': 'relation'
        }
        if kwargs:
            update_kwargs.update(kwargs)
        
        tree = self.wbd._workbookTree
        try:
            results = tree.findall(f".//{update_kwargs['parent_dir']}//{update_kwargs['child_dir']}/")
            
            for node in results:
                if node.text is None:
                    continue
                if update_kwargs['search_tag'] in node.tag:
                    new_txt = node.text.replace(old_item, replace_with)
                    node.text = new_txt
        except Exception as e:
            print(f'failed to update SQL query - {e}')
            return
        extension = self.wbd.filename[self.wbd.filename.index('.'):]
        
        updated_fname = cfg.get_fpath(self.name + extension, dest_dir)
        #### Writes .twb file with updated query
        self.wbd.save_as(updated_fname)
        
    
    def __repr__(self) -> str:
        
        return f'<WBH_obj: {self.name}>'

    
    


if __name__ == '__main__':
    # wbd_list = []
    # for name, fpath in cfg.WKBK_DICT.items():
    #     wbd_list.append(WBhybrid(wbd_obj=TDA.Workbook(fpath)))
    
    #### Test SQL update functionality
    wb = WBhybrid(wbs_obj=None, wbd_obj=TDA.Workbook(cfg.get_fpath('test_wb.twb', cfg.WKBK_DIR)))
    wb.update_sql_query('test_query_item', 'updated_query_item')
    ########
    
    pass
    