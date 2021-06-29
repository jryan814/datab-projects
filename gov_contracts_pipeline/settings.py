import os

# File and directory paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(ROOT_DIR, 'data')

DEF_DATA_FILE = os.path.join(DATA_PATH, 'dirty_data.csv')

DB_PATH = os.path.join(DATA_PATH, 'gov_contracts.db')

DEF_CLEAN_PATH = os.path.join(DATA_PATH, 'cleaned_data.csv')

RUN_DB_SETUP = not os.path.isfile(DB_PATH)

DOES_CLEAN_EXIST = os.path.isfile(DEF_CLEAN_PATH)
# Data column names and name changes
rename_map = {
    'period_of_performance_start_date': 'pop_start_date',
    'recipient_duns': 'recipient_duns',
    'primary_place_of_performance_zip_4': 'plop_zip',
    'action_date_fiscal_year': 'action_date_fiscal_year',
    'contract_award_unique_key': 'contract_award_unique_key',
    'recipient_name': 'recipient_name',
    'award_id_piid': 'award_piid_ref',
    'primary_place_of_performance_state_name': 'plop_state',
    'primary_place_of_performance_congressional_district': 'plop_congressional_district',
    'award_or_idv_flag': 'award_or_idv_flag', # -> only 1 unique value
    'federal_action_obligation': 'dollars_obligated',
    'primary_place_of_performance_county_name': 'plop_county',
    'action_date': 'action_date',
    'award_type_code': 'award_type_code',
    'parent_award_agency_name': 'parent_award_agency_name',
    'parent_award_id_piid': 'award_id', ## -> primary method of identifying individual contracts
    'parent_award_modification_number': 'parent_award_mod_number',
    'parent_award_agency_id': 'parent_award_agency_id',
    'award_description': 'award_description',
    'awarding_sub_agency_name': 'awarding_sub_agency_name',
    'awarding_office_code': 'awarding_office_code', 
    'city_local_government': 'city_local_government', # -> Don't need this column
    'period_of_performance_potential_end_date': 'pop_potential_end_date',
    'number_of_actions': 'number_of_actions',
    'primary_place_of_performance_city_name': 'plop_city',
    'primary_place_of_performance_country_code': 'plop_country_code',
    'award_type': 'award_type',
    'awarding_agency_code': 'awarding_agency_code',
    'last_modified_date': 'last_modified_date',
    'primary_place_of_performance_state_code': 'plop_state_code',
    'awarding_sub_agency_code': 'awarding_sub_agency_code',
    'recipient_city_name': 'recipient_city',
    'awarding_office_name': 'awarding_office_name',
    'recipient_zip_4_code': 'recipient_zip_code',
    'primary_place_of_performance_country_name': 'plop_country_name',
    'period_of_performance_current_end_date': 'pop_end_date',
    'awarding_agency_name': 'awarding_agency_name',
    'naics_code': 'naics_code'}

top = '-'*41
opener = f'''{top}
| Government Contract Database Pipeline |
| Cleans flat file from USAspending.gov |
{top}
'''
print(opener)