#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ 'version', 'changeset', 'timestamp', 'user', 'uid']

mapping = { "St": "Street",
            "St.": "Street",
            "Ave" : "Avenue",
            "Rd." : "Road",
            "Ave." : "Avenue",
            "Blvd" : "Boulevard",
            "Blvd." : "Boulevard",
            "Dr" : "Drive",
            "Dr." : "Drive",
            "Hwy" : "Highway",
            "Ln" : "Lane",
            "Pkwy" : "Parkway",
            "Pky" : "Parkway",
            "Rd" : "Road",
            "Rd." : "Road",
            "St" : "Street",
            "St." : "Street",
            "Street," : "Street",
            "ave" : "Avenue",
            "street" : "Street"
            }


def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        node = element.attrib
        if node == {}:
            element.clear()
            return None
        node['type'] = element.tag
        node['created'] = {}
        node['pos'] = []
        for each in CREATED:
            if each in node.keys():
                node['created'][each] = element.attrib[each]
                del node[each]
        if 'lat' in node.keys() and 'lon' in node.keys():
            node['pos'].append(float(node['lat']))
            node['pos'].append(float(node['lon']))
            del node['lat']
            del node['lon']
        node['address'] = {}
        if node['type'] == 'way':
            node['node_refs'] = []
        for child in element:
            if child.tag == 'nd':
                node['node_refs'].append(child.attrib['ref'])
                
            if child.tag == 'tag':
                if problemchars.search(child.attrib['k']) == None:
                    if child.attrib['k'][:5] == "addr:" and child.attrib['k'].count(':') == 1:
                        node['address'][child.attrib['k'][5:]] = child.attrib['v']
                    else:
                        node[child.attrib['k']] = child.attrib['v']

        if node['address'] != {}:
            if node['address'].has_key('street'):
                for key in mapping.keys():
                    if key in node['address']['street']:
                        newaddress = replace_last(node['address']['street'], key, mapping[key])
                        node['address']['street'] = newaddress
                        break
        if node['address'] == {}:
            del node['address']
        return node
    else:
        return None

def replace_last(source, old, new):
    head, sep, tail = source.rpartition(old)
    return head + new

def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for event, element in ET.iterparse(file_in, events = ("start", "end")):
            if event == 'end':
                element.clear()
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    data = process_map('sample.osm')

if __name__ == "__main__":
    test()
