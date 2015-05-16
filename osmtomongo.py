import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import codecs
import json


#filepath and re
OSMFILE = "portland_oregon.osm"                     
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')




#list of expected street types, streets with these as the last words will not be looked at. if you find any street types in the data that are proper add them to this list.
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Way", "Terrace", "Loop", "Highway", "Circle"]

#building this up with auditstreetnames()
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


class MongoLoader(object):
	'''
	class for loading data from osm files to json for going into a mongodb instance
	'''

	def shape_element(element):
 	   node = {}
    	if element.tag == "node" or element.tag == "way" :
        	node = element.attrib
        	#make sure the node isnt empty
        	if node == {}:
           		element.clear()
            	return None
        
        	#start building up the keys of the node
        	node['type'] = element.tag
        	node['created'] = {}
        	node['pos'] = []
        	#grab up the data from fields in created
        	for each in CREATED:
        	    if each in node.keys():
        	        node['created'][each] = element.attrib[each]
        	        del node[each]
        	#translate the lat and lon as a array
        	if 'lat' in node.keys() and 'lon' in node.keys():
        	    node['pos'].append(float(node['lat']))
        	    node['pos'].append(float(node['lon']))
        	    del node['lat']
        	    del node['lon']
        	#make the address subdict
        	node['address'] = {}
        	#if it is a way get a node_refs array
        	if node['type'] == 'way':
        	    node['node_refs'] = []
        	for child in element:
        	    #loop over the subtags and put in the apporiate node_refs or address data            
        	    if child.tag == 'nd':
        	        node['node_refs'].append(child.attrib['ref'])
                
        	    if child.tag == 'tag':
        	        if problemchars.search(child.attrib['k']) == None:
        	            if child.attrib['k'][:5] == "addr:" and child.attrib['k'].count(':') == 1:
        	                node['address'][child.attrib['k'][5:]] = child.attrib['v']
        	            else:
        	                node[child.attrib['k']] = child.attrib['v']

        	#now the fun street name replacement 
        	if node['address'] != {}:
        	    if node['address'].has_key('street'):
        	        for key in mapping.keys():
        	            if key in node['address']['street']:
        	                newaddress = replace_last(node['address']['street'], key, mapping[key])
        	                node['address']['street'] = newaddress
        	                break
        	#if an address was not found remove the field
        	if node['address'] == {}:
        	    del node['address']
        	return node
    	#if its not a tag or a way return nothing    
    	else:
    	    return None

	#for replacing street names
	def replace_last(source, old, new):
	    head, sep, tail = source.rpartition(old)
	    return head + new



	def process_map(file_in, pretty = False):
	    file_out = "{0}.json".format(file_in)
	    data = []
	    #write out the convereted osm to a json, probably should not be storing the whole thing in the data varible, this is probably why I am leaking so much memory
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


	def get_element(osm_file, tags=('node', 'way', 'relation')):
	    """Yield element if it is the right type of tag

	    Reference:
    	http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    	"""
    	context = ET.iterparse(osm_file, events=('start', 'end'))
    	_, root = next(context)
    	for event, elem in context:
    	    if event == 'end' and elem.tag in tags:
    	        yield elem
    	        root.clear()

   	#this chunk needs to be integrated currently not working
   	'''
	with open(SAMPLE_FILE, 'wb') as output:
	    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
	    output.write('<osm>\n  ')

	    # Write every 10th top level element
	    for i, element in enumerate(get_element(OSM_FILE)):
	        if i % 10 == 0:
	            output.write(ET.tostring(element, encoding='utf-8'))

    	output.write('</osm>')
    ''''
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


   	