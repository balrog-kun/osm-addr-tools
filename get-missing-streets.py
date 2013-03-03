#! /usr/bin/python2
# vim: fileencoding=utf-8 encoding=utf-8 et sw=4
#
# Reads an existing-highways.osm file and an addresses.osm file and
# writes an .osm file containing one node per potential missing street
# name -- such that no named highway containing every word from the
# addr:street is found within about ~1.5km
# Output name is hardcoded as missing-streets.osm
#
# The inputs can be generated with something like:
# wget -O existing-highways.osm 'http://overpass-api.de/api/xapi?way[highway=*][name=*][bbox=20.781,52.092,21.281,52.365]'
# wget -O addresses.osm 'http://overpass-api.de/api/xapi?*[addr:street=*][bbox=20.781,52.092,21.281,52.365]'
#
# Not sure about a need to escape the ':' in the second query somehow...
#

import sys
import os
import math

import xml.etree.cElementTree as ElementTree

i = 0
outroot = ElementTree.Element("osm", { "version": "0.6" })
inroot = ElementTree.parse(sys.argv[1]).getroot()

waynodes = {}
existingaddrs = {}
for elem in inroot:
    if 'id' not in elem.attrib:
        continue
    id = int(elem.attrib['id'])
    tags = {}
    for sub in elem:
        if sub.tag != 'tag':
	   continue
	tags[sub.attrib['k']] = sub.attrib['v']
    if elem.tag == 'node':
        lat = float(elem.attrib['lat'])
        lon = float(elem.attrib['lon'])
        waynodes[id] = ( lat, lon )
    if 'addr:housenumber' not in tags or 'addr:street' not in tags:
        continue
    if elem.tag == 'node' and 'amenity' in tags:
        continue
    strt = tags['addr:street'].lower()
    if elem.tag not in [ 'way', 'node' ]:
        continue
    if elem.tag == 'way':
        j = 0
        lat = 0.0
	lon = 0.0
        for sub in elem:
	    if sub.tag != 'nd':
	        continue
            ref = int(sub.attrib['ref'])
	    if ref not in waynodes:
	        continue
            j += 1
	    lat += waynodes[ref][0]
	    lon += waynodes[ref][1]
	lat /= j
	lon /= j
    existingaddrs[strt] = ( lat, lon )

byword = {}
for elem in inroot:
    if 'id' not in elem.attrib:
        continue
    id = int(elem.attrib['id'])
    tags = {}
    nodes = []
    for sub in elem:
        if sub.tag == 'nd':
	   nodes.append(waynodes[int(sub.attrib['ref'])])
        if sub.tag != 'tag':
	   continue
	tags[sub.attrib['k']] = sub.attrib['v']
    if elem.tag == 'node':
        lat = float(elem.attrib['lat'])
        lon = float(elem.attrib['lon'])
        waynodes[id] = ( lat, lon )
	continue
    elif elem.tag not in [ 'way' ]:
        continue
    if 'highway' not in tags or 'name' not in tags:
        continue
    name = tags['name'].lower().split()
    if 'alt_name' in tags:
        name += tags['alt_name'].lower().replace(';', ' ').split()
    for word in name:
        if word not in byword:
	    byword[word] = []
	byword[word].append(( name, nodes, id ))
inroot = None

i = 0
for strt in existingaddrs:
    lat, lon = existingaddrs[strt]
    all = 0
    hwys = {}
    for word in strt.split():
        all += 1
        if word in byword:
	    for hwy in byword[word]:
	        hwys[hwy[2]] = hwy
    cont = 0
    for id in hwys:
        name, nodes, _id = hwys[id]
        same = 0
        for word in strt.split():
	    if word in [ u'Księdza', u'Kapitana', u'Generała' ] or word in name:
	        same += 1
	if same == all:
	    for nlat, nlon in nodes:
	        if math.hypot(lat - nlat, lon - nlon) < 0.01: # ~1km?
		    cont = 1
		    break
	if cont:
	    break
    if cont:
        continue
    i += 1
    node = ElementTree.SubElement(outroot, "node", {
        "lat": str(lat),
        "lon": str(lon),
        "version": str(1),
        "id": str(i) })
    ElementTree.SubElement(node, "tag", {
        "k": 'addr:street', "v": strt })

sys.stdout.write("Writing .osm's\n")
ElementTree.ElementTree(outroot).write("missing-streets.osm", "utf-8")
