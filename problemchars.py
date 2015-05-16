import xml.etree.ElementTree as ET
import pprint
import re

###### I am leaking memory from somewhere its a slow leak but might be worrysome at some point.

"""
results

{'lower': 1763346,
 'lower_colon': 1488116,
 'other': 163770,
 'problemchars': 2,
 'probs': ['food cart', 'food cart']}

"""
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys, event):
    
    if element.tag == "tag":
        if problemchars.search(element.attrib['k']):
            keys["problemchars"] += 1
            keys['probs'].append(element.attrib['k'])            
        elif lower_colon.search(element.attrib['k']):
            keys["lower_colon"] += 1
        elif lower.search(element.attrib['k']):
            keys["lower"] += 1
        else:
            keys["other"] += 1
    if event == 'end':
        element.clear()
        
        pass
        
    return keys



def problem_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0, 'probs' : []}
    for event, element in ET.iterparse(filename, events = ("start","end")):
        keys = key_type(element, keys, event)

    return keys



def test():
    keys = problem_map('portland_oregon.osm')
    pprint.pprint(keys)


if __name__ == "__main__":
    test()
