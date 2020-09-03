# -*- coding: utf-8 -*-
#mission trigger들을 osm 파일로부터 불러오는 모듈

import os
import OSMHandler
from shapely.geometry import Point, Polygon, LineString

cwd = os.getcwd()
default = 'k_city'
dgist = "/hd_map/dgist/"
k_city = "/hd_map/k_city/"
# 보호구역(노인,어린이,장애인)
def protected_areas(location=default):
    if location == 'dgist':
        osm_data = OSMHandler.OSM_data(cwd+ dgist + "A3_DRIVEWAYSECTION_cut.osm")
    elif location == 'k_city':
        osm_data = OSMHandler.OSM_data(cwd+ k_city + "A3_DRIVEWAYSECTION_cut.osm")

    ways = []
    for data in osm_data:
        if data[0] == 'way':
            ways.append(data)

    if location == 'dgist':
        protected_ways = []
        for way in ways:
            if way[4]['Kind'] == '7':
                protected_ways.append(way)

    elif location == 'k_city':
        protected_ways = []
        for way in ways:
            if way[4]['Kind'] == '1':
                protected_ways.append(way)

    return protected_ways

def protected_areas_polygons(location=default):
    if location == 'dgist':
        osm_data = OSMHandler.OSM_data(cwd+ dgist + "A3_DRIVEWAYSECTION_cut.osm")
    elif location == 'k_city':
        osm_data = OSMHandler.OSM_data(cwd+ k_city + "A3_DRIVEWAYSECTION_cut.osm")

    protected_areas_list = protected_areas(location)

    nodes = []
    for data in osm_data:
        if data[0] == 'node':
            nodes.append(data)

    polygons = []
    for item in protected_areas_list:
        temp_node_ref = item[2][0:-1]
        temp_coords = []
        for node in nodes:
            for node_id in temp_node_ref:
                if node_id==node[1]:
                    temp_coords.append((node[3],node[2]))
        temp_poly = Polygon(temp_coords)
        polygons.append(temp_poly)
    return polygons

#횡단보도 (5321: 횡단보도, 533: 고원식횡단보도, 534: 자전거 횡단보도)
def crosswalks(location=default):
    if location == 'k_city':
        osm_data = OSMHandler.OSM_data(cwd+ k_city + "B3_SURFACEMARK_cut.osm")
    elif location == 'dgist':
        osm_data = OSMHandler.OSM_data(cwd+ dgist + "B3_SURFACEMARK_cut.osm")

    ways = []
    for data in osm_data:
        if data[0] == 'way':
            ways.append(data)

    crosswalks = []
    for way in ways:
        if way[4]['Kind'] == '5321' or way[4]['Kind'] == '533' or way[4]['Kind'] == '534':
            crosswalks.append(way)

    return crosswalks

def crosswalks_polygons(location=default):
    if location == 'k_city':
        osm_data = OSMHandler.OSM_data(cwd+ k_city + "B3_SURFACEMARK_cut.osm")
    elif location == 'dgist':
        osm_data = OSMHandler.OSM_data(cwd+ dgist + "B3_SURFACEMARK_cut.osm")

    crosswalks_polygons_list = crosswalks(location)

    nodes = []
    for data in osm_data:
        if data[0] == 'node':
            nodes.append(data)

    polygons = []
    for item in crosswalks_polygons_list:
        temp_node_ref = item[2][0:-1]
        temp_coords = []
        for node in nodes:
            for node_id in temp_node_ref:
                if node_id==node[1]:
                    temp_coords.append((node[3],node[2]))
        temp_poly = Polygon(temp_coords)
        polygons.append(temp_poly)
    return polygons

#과속 방지턱
def speedbumps(location=default):
    if location == 'k_city':
        osm_data = OSMHandler.OSM_data(cwd+ k_city + "C4_SPEEDBUMP_cut.osm")
    elif location == 'dgist':
        osm_data = OSMHandler.OSM_data(cwd+ dgist + "C4_SPEEDBUMP_cut.osm")

    ways = []
    for data in osm_data:
        if data[0] == 'way':
            ways.append(data)

    speedbumps = []
    for way in ways:
        if way[4]['Type'] == '1':
            speedbumps.append(way)

    return speedbumps

def speedbumps_polygons(location=default):
    if location == 'k_city':
        osm_data = OSMHandler.OSM_data(cwd+ k_city + "C4_SPEEDBUMP_cut.osm")
    elif location == 'dgist':
        osm_data = OSMHandler.OSM_data(cwd+ dgist + "C4_SPEEDBUMP_cut.osm")

    speedbumps_polygons_list = speedbumps(location)

    nodes = []
    for data in osm_data:
        if data[0] == 'node':
            nodes.append(data)

    polygons = []
    for item in speedbumps_polygons_list:
        temp_node_ref = item[2][0:-1]
        temp_coords = []
        for node in nodes:
            for node_id in temp_node_ref:
                if node_id==node[1]:
                    temp_coords.append((node[3],node[2]))
        temp_poly = Polygon(temp_coords)
        polygons.append(temp_poly)
    return polygons

#평면교차로
def intersections(location=default):
    if location == 'k_city':
        osm_data = OSMHandler.OSM_data(cwd+ k_city + "A1_NODE_cut.osm")
    elif location == 'dgist':
        osm_data = OSMHandler.OSM_data(cwd+ dgist + "A1_NODE_cut.osm")

    nodes = []
    for data in osm_data:
        if data[0] == 'node':
            nodes.append(data)

    intersections = []
    for node in nodes:
        if node[5]['NodeType'] == '1':
            intersections.append(node)

    return intersections

#회전교차로
def traffic_roundabouts(location=default):
    if location == 'k_city':
        osm_data = OSMHandler.OSM_data(cwd+ k_city + "A1_NODE_cut.osm")
    elif location == 'dgist':
        osm_data = OSMHandler.OSM_data(cwd+ dgist + "A1_NODE_cut.osm")

    nodes = []
    for data in osm_data:
        if data[0] == 'node':
            nodes.append(data)

    traffic_roundabouts = []
    for node in nodes:
        if node[5]['NodeType'] == '10':
            traffic_roundabouts.append(node)

    return traffic_roundabouts

#교통표지판 (osm 파일에 있는 모든 노드가 각각 SubType으로 구분된 교통표지판임.)
def traffic_signs(location=default):
    if location == 'k_city':
        osm_data = OSMHandler.OSM_data(cwd+ k_city + "B1_SAFETYSIGN_cut.osm")
    elif location == 'dgist':
        osm_data = OSMHandler.OSM_data(cwd+ dgist + "B1_SAFETYSIGN_cut.osm")

    nodes = []
    for data in osm_data:
        if data[0] == 'node':
            nodes.append(data)

    return nodes

#신호등 (osm 파일에 있는 모든 노드가 각각 Type으로 구분된 신호등임.)
def traffic_lights(location=default):
    if location == 'k_city':
        osm_data = OSMHandler.OSM_data(cwd+ k_city + "C1_TRAFFICLIGHT_cut.osm")
    elif location == 'dgist':
        osm_data = OSMHandler.OSM_data(cwd+ dgist + "C1_TRAFFICLIGHT_cut.osm")

    nodes = []
    for data in osm_data:
        if data[0] == 'node':
            nodes.append(data)

    return nodes

def guide_lines_linestrings(location=default):
    if location == 'dgist':
        osm_data = OSMHandler.OSM_data(cwd+ dgist + "A2_LINK_cut.osm")
    elif location == 'k_city':
        osm_data = OSMHandler.OSM_data(cwd+ k_city + "A2_LINK_cut.osm")

    nodes = []
    for item in osm_data:
        if item[0] == 'node':
            nodes.append(item)

    ways = []
    for item in osm_data:
        if item[0] == 'way':
            ways.append(item)

    linestrings = []
    for item in ways:
        temp_node_ref = item[2]
        temp_coords = []
        for node in nodes:
            for node_id in temp_node_ref:
                if node_id==node[1]:
                    temp_coords.append((node[3],node[2]))
        temp_poly = LineString(temp_coords)
        linestrings.append(temp_poly)
    return linestrings

if __name__ == '__main__':
    a = guide_lines_linestrings()
    print(a)
    print(a[0])
