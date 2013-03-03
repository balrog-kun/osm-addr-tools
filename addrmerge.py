#! /usr/bin/python

import os
import sys
import math
import xml.etree.cElementTree as ElementTree
import codecs

miasto = sys.argv[1]

newroot = ElementTree.parse(miasto + '.osm').getroot()
origroot = ElementTree.parse(miasto + '-osm.osm').getroot()

waynodes = {}
existingaddrs = {}
for elem in origroot:
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
	if 'addr:housenumber' not in tags:
		continue
	if 'addr:street' not in tags and 'addr:place' not in tags:
		continue
	if elem.tag == 'node' and 'amenity' in tags:
		continue
	num = tags['addr:housenumber'].replace(' ', '').lower()
	if 'addr:street' in tags:
		strt = tags['addr:street'].lower()
	else:
		strt = tags['addr:place'].lower()
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
	if num not in existingaddrs:
	   existingaddrs[num] = []
	existingaddrs[num].append(( lat, lon, strt ))
origroot = None

todel = []
for elem in newroot:
	tags = {}
	for sub in elem:
		if sub.tag != 'tag':
			continue
		tags[sub.attrib['k']] = sub.attrib['v']
	if 'addr:housenumber' not in tags:
		continue
	if 'addr:street' not in tags and 'addr:place' not in tags:
		continue
	num = tags['addr:housenumber'].replace(' ', '').lower()
	if 'addr:street' in tags:
		strt = tags['addr:street'].lower()
	else:
		strt = tags['addr:place'].lower()
	if elem.tag not in [ 'node' ]:
		continue

	if num not in existingaddrs:
		continue
	lat = float(elem.attrib['lat'])
	lon = float(elem.attrib['lon'])
	words = strt.lower().replace('-', ' ').split()
	same = 0
	for elat, elon, estrt in existingaddrs[num]:
		if math.hypot(lat - elat, lon - elon) > 0.001: # about 0.1km
	       		continue
		for w in [ words[-1] ]:
			if w in estrt:
				same = 1
				todel.append(elem)
				break
		if same:
			break
for elem in todel:
	newroot.remove(elem)

sys.stdout.write('Writing .osm\'s\n')
ElementTree.ElementTree(newroot).write(miasto  +'-filtered.osm', 'utf-8')
