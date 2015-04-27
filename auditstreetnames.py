import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

"""
This script will return a list of street types that are not part of the expected list. Use this for making the mapping used in mongodb prep and street clean file. the audit function will also return a list of user ids with number of controbutions.
"""

#filepath and re
OSMFILE = "portland_oregon.osm"                     
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


#list of expected street types, streets with these as the last words will not be looked at. if you find any street types in the data that are proper add them to this list.
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Way", "Terrace", "Loop", "Highway", "Circle"]


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

#this probably doesn't need its own function
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    users = {}

    #loop over elems in osm_file find the uids and check the streets against expected. 
    for event, elem in ET.iterparse(osm_file, events=("start","end")):        
        if event == 'end':
            elem.clear()
            #without clearing the elems memory leaks very quickly
        if elem.attrib.has_key("uid"):
            if users.has_key(elem.attrib['uid']):
                users[elem.attrib['uid']] += 1
            else:
                users[elem.attrib['uid']] = 1
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types, users



def test():
    st_types, users = audit(OSMFILE)
    pprint.pprint(dict(st_types))
    # pprint.pprint(users)
if __name__ == '__main__':
    test()
