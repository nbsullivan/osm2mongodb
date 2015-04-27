import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "portland_oregon.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Way", "Terrace", "Loop", "Highway", "Circle"]



def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    users = {}
    for event, elem in ET.iterparse(osm_file, events=("start","end")):
        if event == 'end':
            elem.clear()
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


def update_name(name, mapping):
    for key in mapping.keys():
        if name.find(key) > 0:
            name = name.replace(key, mapping[key])
            print key, "=>", mapping[key]
            break
            

    return name


def test():
    st_types, users = audit(OSMFILE)
    pprint.pprint(dict(st_types))
    # pprint.pprint(users)
if __name__ == '__main__':
    test()
