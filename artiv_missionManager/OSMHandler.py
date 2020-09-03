# -*- coding: utf-8 -*-
# OSM Handler
# ref : https://docs.osmcode.org/pyosmium/latest/ref_osm.html#osmium.osm.RelationMember
# github : https://github.com/DGIST-ARTIV/Localization/blob/master/HDMap/OSMHandler/src/OSMHandler.py
# Author: Juho Song (hoya4764@dgist.ac.kr)
# Date: 2020.07.21.

import osmium as osm

class OSMHandler(osm.SimpleHandler):
    def __init__(self):
        osm.SimpleHandler.__init__(self)
        self.osm_data = []
        self.num_nodes = 0
        self.num_ways = 0
        self.num_relations = 0

    def tag_inventory_node(self, elem, elem_type):
        temp = dict()
        for tag in elem.tags:
            temp[tag.k] = tag.v

        self.osm_data.append([elem_type,
                               elem.id,
                               elem.location.lat,
                               elem.location.lon,
                               len(elem.tags),
                               temp])

    def tag_inventory_way(self, elem, elem_type):
        temp = dict()
        tempNodes = [node.ref for node in elem.nodes]
        for tag in elem.tags:
            temp[tag.k] = tag.v

        self.osm_data.append([elem_type,
                               elem.id,
                               tempNodes, #read only
                               len(elem.tags),
                               temp])

    def tag_inventory_relation(self, elem, elem_type):
        temp = dict()
        for tag in elem.tags:
            temp[tag.k] = tag.v
        temp_ref = [member.ref for member in elem.members]
        temp_role = [member.role for member in elem.members]
        temp_type = [member.type for member in elem.members]
        tempMembers = []
        for i in range(len(temp_ref)):
            tempMembers.append([temp_type[i],temp_ref[i],temp_role[i]])

        self.osm_data.append([elem_type,
                               elem.id,
                               tempMembers, #read only
                               len(elem.tags),
                               temp])

    def node(self, n):
        self.tag_inventory_node(n, "node")
        self.num_nodes += 1

    def way(self, w):
        self.tag_inventory_way(w, "way")
        self.num_ways += 1

    def relation(self, r):
        self.tag_inventory_relation(r, "relation")
        self.num_relations += 1

def OSM_data(osm_file):
    osmhandler = OSMHandler()
    osmhandler.apply_file(osm_file)
    return osmhandler.osm_data

def OSM_nodes_num(osm_file):
    osmhandler = OSMHandler()
    osmhandler.apply_file(osm_file)
    return osmhandler.num_nodes

def OSM_ways_num(osm_file):
    osmhandler = OSMHandler()
    osmhandler.apply_file(osm_file)
    return osmhandler.num_ways

def OSM_relations_num(osm_file):
    osmhandler = OSMHandler()
    osmhandler.apply_file(osm_file)
    return osmhandler.num_relations

def osm_data(osm_file):
    return OSMHandler.OSM_data(osm_file)

def nodes(osm_data):
    nodes = []
    for data in osm_data:
        if data[0] == 'node':
            nodes.append(data)
    return nodes

def ways(osm_data):
    ways = []
    for data in osm_data:
        if data[0] == 'way':
            ways.append(data)
    return ways

def sectors(ways):
    sectors = []
    for way in ways:
        if way[2][0] == way[2][-1]:
            sectors.append(way)
    return sectors

if __name__ == '__main__':
    file_name = "A3_DRIVEWAYSECTION.osm"
    osm_data = OSM_data(file_name)
    nodes_num = OSM_nodes_num(file_name)
    ways_num = OSM_ways_num(file_name)
    relations_num = OSM_relations_num(file_name)
    print(osm_data)

    ways = ways(osm_data)
    print(sectors(ways))
