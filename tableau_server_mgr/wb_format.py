#################################################
# EARLY development for wkbk formatting updates #
#################################################
import config as cfg
from hybrid_wkbk import WBhybrid as WBH
import util
import re


list_colors = []
twbx = []
for k, v in cfg.WKBK_DICT.items():
    if '.twbx' in v:
        twbx.append(k)
        continue
    with open(v, 'r') as f:
        #print(k)
        try:
            for line in f.readlines():
                if re.search(r'([#][0-9a-gA-G]{6})', line):
                    list_colors += re.findall(r'([#][0-9a-gA-G]{6})', line)
        except Exception as e:
            print(k, '----')
            print(e, line)
colors = list(set(list_colors))

print(twbx)


format_elements = {
    'format': {'attr': 'background-color', 'scope': 'cols', 'value': '#e6ecf0'},
    'run': {'font-color': '#000000'}
}