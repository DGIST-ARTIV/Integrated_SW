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
        temp_node_ref = item[2]
        temp_coords = []
        for node_id in temp_node_ref:
            for node in nodes:
                if node_id==node[1]:
                    temp_coords.append((node[3],node[2]))
        temp_poly = Polygon(temp_coords)
        polygons.append(temp_poly)
    return polygons

#횡단보도 (5321: 횡단보도)
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
        if way[4]['Kind'] == '5321':
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
        temp_node_ref = item[2]
        temp_coords = []
        for node_id in temp_node_ref:
            for node in nodes:
                if node_id==node[1]:
                    temp_coords.append((node[3],node[2]))
        temp_poly = Polygon(temp_coords)
        polygons.append(temp_poly)
    return polygons

#횡단보도 (533: 고원식횡단보도)
def bump_crosswalks(location=default):
    if location == 'k_city':
        osm_data = OSMHandler.OSM_data(cwd+ k_city + "B3_SURFACEMARK_cut.osm")
    elif location == 'dgist':
        osm_data = OSMHandler.OSM_data(cwd+ dgist + "B3_SURFACEMARK_cut.osm")

    ways = []
    for data in osm_data:
        if data[0] == 'way':
            ways.append(data)

    bump_crosswalks = []
    for way in ways:
        if way[4]['Kind'] == '533':
            bump_crosswalks.append(way)

    return bump_crosswalks

def bump_crosswalks_polygons(location=default):
    if location == 'k_city':
        osm_data = OSMHandler.OSM_data(cwd+ k_city + "B3_SURFACEMARK_cut.osm")
    elif location == 'dgist':
        osm_data = OSMHandler.OSM_data(cwd+ dgist + "B3_SURFACEMARK_cut.osm")

    bump_crosswalks_polygons_list = bump_crosswalks(location)

    nodes = []
    for data in osm_data:
        if data[0] == 'node':
            nodes.append(data)

    polygons = []
    for item in bump_crosswalks_polygons_list:
        temp_node_ref = item[2]
        temp_coords = []
        for node_id in temp_node_ref:
            for node in nodes:
                if node_id==node[1]:
                    temp_coords.append((node[3],node[2]))
        temp_poly = Polygon(temp_coords)
        polygons.append(temp_poly)
    return polygons

#횡단보도 (534: 자전거 횡단보도)
def bicycle_crosswalks(location=default):
    if location == 'k_city':
        osm_data = OSMHandler.OSM_data(cwd+ k_city + "B3_SURFACEMARK_cut.osm")
    elif location == 'dgist':
        osm_data = OSMHandler.OSM_data(cwd+ dgist + "B3_SURFACEMARK_cut.osm")

    ways = []
    for data in osm_data:
        if data[0] == 'way':
            ways.append(data)

    bicycle_crosswalks = []
    for way in ways:
        if way[4]['Kind'] == '534':
            bicycle_crosswalks.append(way)

    return bicycle_crosswalks

def bicycle_crosswalks_polygons(location=default):
    if location == 'k_city':
        osm_data = OSMHandler.OSM_data(cwd+ k_city + "B3_SURFACEMARK_cut.osm")
    elif location == 'dgist':
        osm_data = OSMHandler.OSM_data(cwd+ dgist + "B3_SURFACEMARK_cut.osm")

    bicycle_crosswalks_polygons_list = bicycle_crosswalks(location)

    nodes = []
    for data in osm_data:
        if data[0] == 'node':
            nodes.append(data)

    polygons = []
    for item in bicycle_crosswalks_polygons_list:
        temp_node_ref = item[2]
        temp_coords = []
        for node_id in temp_node_ref:
            for node in nodes:
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
        temp_node_ref = item[2]
        temp_coords = []
        for node_id in temp_node_ref:
            for node in nodes:
                if node_id==node[1]:
                    temp_coords.append((node[3],node[2]))
        temp_poly = Polygon(temp_coords)
        polygons.append(temp_poly)
    return polygons

#STOP_LINE (AUTHOR : JUNSANG RYU)
def stoplines(location=default):
    if location == 'k_city':
        osm_data = OSMHandler.OSM_data(cwd+ k_city + "B2_SURFACELINEMARK_cut.osm")
    elif location == 'dgist':
        osm_data = OSMHandler.OSM_data(cwd+ dgist + "B2_SURFACELINEMARK_cut.osm")

    ways = []
    for data in osm_data:
        if data[0] == 'way':
            ways.append(data)

    stoplines = []
    for way in ways:
        if way[4]['Kind'] == '530':
            stoplines.append(way)

    return stoplines

def stoplines_linestrings(location=default):
    if location == 'k_city':
        osm_data = OSMHandler.OSM_data(cwd+ k_city + "B2_SURFACELINEMARK_cut.osm")
    elif location == 'dgist':
        osm_data = OSMHandler.OSM_data(cwd+ dgist + "B2_SURFACELINEMARK_cut.osm")

    stoplines_linestrings_list = stoplines(location)

    nodes = []
    for data in osm_data:
        if data[0] == 'node':
            nodes.append(data)

    LineStrings = []
    for item in stoplines_linestrings_list:
        temp_node_ref = item[2]
        temp_coords = []
        for node_id in temp_node_ref:
            for node in nodes:
                if node_id==node[1]:
                    temp_coords.append((node[3],node[2]))
        temp_poly = LineString(temp_coords)
        LineStrings.append(temp_poly)
    return LineStrings


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

#주행유도선 (각 way를 LineString의 형태로 담은 list를 return)
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
        for node_id in temp_node_ref:
            for node in nodes:
                if node_id==node[1]:
                    temp_coords.append((node[3],node[2]))
        temp_poly = LineString(temp_coords)
        linestrings.append(temp_poly)
    return linestrings


#미션구간 (준상이가 새롭게 만든 osm 파일 기반, 09.03 added)
def mission_sections(location=default):
    if location == 'k_city':
        osm_data = OSMHandler.OSM_data(cwd+ k_city + "A4_MISSIONSECTION.osm")
    elif location == 'dgist':
        osm_data = OSMHandler.OSM_data(cwd+ dgist + "A4_MISSIONSECTION.osm")

    ways = []
    for data in osm_data:
        if data[0] == 'way':
            ways.append(data)

    mission_sections = []
    for way in ways:
        if 1: # 이 부분은 태그 추가하면 조건을 달아주도록.
            mission_sections.append(way)

    return mission_sections

def mission_sections_polygons(location=default):
    if location == 'k_city':
        osm_data = OSMHandler.OSM_data(cwd+ k_city + "A4_MISSIONSECTION.osm")
    elif location == 'dgist':
        osm_data = OSMHandler.OSM_data(cwd+ dgist + "A4_MISSIONSECTION.osm")

    mission_sections_polygons_list = mission_sections(location)

    nodes = []
    for data in osm_data:
        if data[0] == 'node':
            nodes.append(data)

    polygons = []
    for item in mission_sections_polygons_list:
        temp_node_ref = item[2]
        temp_coords = []
        for node_id in temp_node_ref:
            for node in nodes:
                if node_id==node[1]:
                    temp_coords.append((node[3],node[2]))
        temp_poly = Polygon(temp_coords)
        polygons.append(temp_poly)
    return polygons


def isin(polygons, latitude, longitude):
    temp_point = Point(longitude, latitude)
    isin = 0.0
    for polygon in polygons:
        if temp_point.intersects(polygon):
            isin = 1.0
            break
    return isin

if __name__ == '__main__':
    a = crosswalks_polygons('dgist')
    print(a)
    b = bump_crosswalks_polygons('dgist')
    print(b)
    c = bicycle_crosswalks_polygons('dgist')
    print(c)
    longitude, latitude = 128.4667133, 35.6920711
    print(isin(a,latitude,longitude))
