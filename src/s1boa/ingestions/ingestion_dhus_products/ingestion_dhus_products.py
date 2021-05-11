"""
Ingestion module for the OPDHUS_S1 files of Sentinel-1

Written by DEIMOS Space S.L. (dibb)

module s1boa
"""
# Import python utilities
import os
import argparse
from dateutil import parser
import datetime
import tempfile
import json

# Import xml parser
from lxml import etree

# Import ingestion_functions.helpers
import eboa.ingestion.functions as eboa_ingestion_functions
import siboa.ingestions.functions as siboa_ingestion_functions

# Import debugging
from eboa.debugging import debug

# Import query
from eboa.engine.query import Query

version = "1.0"

levels = {
    "RAW": "L0",
    "SLC": "L1_SLC",
    "GRD": "L1_GRD",
    "OCN": "L2_OCN",
}

def process_file(file_path, engine, query, reception_time):
    """Function to process the file and insert its relevant information
    into the DDBB of the eboa
    
    :param file_path: path to the file to be processed
    :type file_path: str
    :param engine: Engine instance
    :type engine: Engine
    :param query: Query instance
    :type query: Query
    :param reception_time: time of the reception of the file by the triggering
    :type reception_time: str

    :return: data with the structure to be inserted into the DDBB
    :rtype: dict
    """
    list_of_events = []
    list_of_annotations = []
    list_of_explicit_references = []
    list_of_completeness_events = []
    file_name = os.path.basename(file_path)

    # Get the general source entry (processor = None, version = None, DIM signature = PENDING_SOURCES)
    # This is for registrering the ingestion progress
    query_general_source = Query()
    session_progress = query_general_source.session
    general_source_progress = query_general_source.get_sources(names = {"filter": file_name, "op": "=="},
                                                               dim_signatures = {"filter": "PENDING_SOURCES", "op": "=="},
                                                               processors = {"filter": "", "op": "=="},
                                                               processor_version_filters = [{"filter": "", "op": "=="}])

    if len(general_source_progress) > 0:
        general_source_progress = general_source_progress[0]
    # end if
    
    eboa_ingestion_functions.insert_ingestion_progress(session_progress, general_source_progress, 10)

    # Replace &gt; by > and &lt; by <
    new_file_with_wrong_characters = tempfile.NamedTemporaryFile("w+t")
    new_file_with_wrong_characters_path = new_file_with_wrong_characters.name
    input_file = open(file_path, "rt")
    data = input_file.read()
    input_file.close()
    new_file_with_wrong_characters_replace = open(new_file_with_wrong_characters_path, "wt")
    new_file_with_wrong_characters_replace.write(data.replace("&gt;", ">").replace("&lt;", "<"))
    new_file_with_wrong_characters_replace.close()

    eboa_ingestion_functions.insert_ingestion_progress(session_progress, general_source_progress, 20)
    
    # Remove namespaces
    new_file = tempfile.NamedTemporaryFile()
    new_file_path = new_file.name
    eboa_ingestion_functions.remove_namespaces(new_file_with_wrong_characters_path, new_file_path)
    
    # Parse file
    parsed_xml = etree.parse(new_file_path)
    xpath_xml = etree.XPathEvaluator(parsed_xml)

    eboa_ingestion_functions.insert_ingestion_progress(session_progress, general_source_progress, 30)

    satellite = file_name[16:19]
    reported_generation_time = file_name[25:40]
    reported_validity_start = file_name[42:57]
    reported_validity_stop = file_name[58:73]
    sensing_start_nodes = xpath_xml("/feed/entry/properties/ContentDate/Start")
    sensing_stop_nodes = xpath_xml("/feed/entry/properties/ContentDate/End")
    if len(sensing_start_nodes) > 0:
        sensing_starts = [node.text for node in sensing_start_nodes]
        sensing_starts.sort()
        # Apply same margin applied for events
        validity_start = (parser.parse(sensing_starts[0]) - datetime.timedelta(seconds=1)).isoformat()
    else:
        validity_start = reported_validity_start
    # end if
    if len(sensing_stop_nodes) > 0:
        sensing_stops = [node.text for node in sensing_stop_nodes]
        sensing_stops.sort()
        validity_stop = sensing_stops[-1]
    else:
        validity_stop = reported_validity_stop
    # end if
    ingestion_completeness = "true"
    ingestion_completeness_message = ""

    eboa_ingestion_functions.insert_ingestion_progress(session_progress, general_source_progress, 40)

    dhus_products = xpath_xml("/feed/entry")
    indexed_planned_imagings = {}
    if len(dhus_products) > 0:
        # Obtain the planned imaging
        planned_imagings = query.get_events(gauge_names = {"filter": "PLANNED_IMAGING", "op": "=="},
                                            gauge_systems = {"filter": satellite, "op": "=="},
                                            start_filters = [{"date": validity_stop, "op": "<"}],
                                            stop_filters = [{"date": validity_start, "op": ">"}])

        for planned_imaging in planned_imagings:
            datatake_id_values = [value for value in planned_imaging.eventTexts if value.name == "datatake_id"]
            datatake_id = datatake_id_values[0].value
                    
            indexed_planned_imagings[datatake_id] = planned_imaging
        # end for
    # end if

    eboa_ingestion_functions.insert_ingestion_progress(session_progress, general_source_progress, 60)

    for dhus_product in dhus_products:
        ########
        # Obtain metadata
        ########
        name = dhus_product.xpath("properties/Name")[0].text
        identifier = dhus_product.xpath("properties/Id")[0].text
        ingestion_date = dhus_product.xpath("properties/IngestionDate")[0].text
        creation_date = dhus_product.xpath("properties/CreationDate")[0].text
        size = dhus_product.xpath("properties/ContentLength")[0].text
        metadata_url = dhus_product.xpath("id")[0].text
        product_url = metadata_url + "/$value"
        geometry = dhus_product.xpath("properties/ContentGeometry/Polygon/outerBoundaryIs/LinearRing/coordinates")[0].text
        orbit = str(int(name[49:55]))
        # All these elements are to remove the 0 at the left side
        datatake_id = hex(int(int(name[56:62], 16).to_bytes(4,'big').hex(),16)).replace("0x", "").upper()
        
        ########
        # Obtain timings
        ########
        start = dhus_product.xpath("properties/ContentDate/Start")[0].text
        stop = dhus_product.xpath("properties/ContentDate/End")[0].text

        ########
        # Define dhus product reference
        ########
        # Dhus product reference
        dhus_product_reference = {
            "group": "DHUS_PRODUCT",
            "name": name
        }
        list_of_explicit_references.append(dhus_product_reference)

        ########
        # Define dhus product annotations
        ########
        # Dhus publication time
        dhus_publication_annotation = {
            "explicit_reference" : name,
            "annotation_cnf": {
                "name": "DHUS_PUBLICATION_TIME",
                "insertion_type": "INSERT_and_ERASE_with_PRIORITY"
                },
            "values": [
                {"name": "dhus_publication_time",
                 "type": "timestamp",
                 "value": creation_date
                }]
        }
        list_of_annotations.append(dhus_publication_annotation)

        # Dhus metadata time
        # Correct geometry as it comes in the form of latitude,
        # longitude pairs. BOA needs longitude latitude pairs
        split_geometry = geometry.split(" ")
        corrected_geometry = [lat_lon.split(",")[1] + "," + lat_lon.split(",")[0] for lat_lon in split_geometry]

        formatted_coordinates = " ".join(corrected_geometry)

        # Split geometries crossing the antimeridian
        list_formatted_coordinates_corrected = siboa_ingestion_functions.correct_antimeridian_issue_in_footprint(formatted_coordinates)
        
        dhus_metadata_annotation = {
            "explicit_reference" : name,
            "annotation_cnf": {
                "name": "DHUS_METADATA_INFORMATION",
                "insertion_type": "SIMPLE_UPDATE"
                },
            "values": [
                {"name": "dhus_ingestion_time",
                 "type": "timestamp",
                 "value": ingestion_date
                },{"name": "dhus_identifier",
                 "type": "text",
                 "value": identifier
                },
                {"name": "dhus_metadata_url",
                 "type": "text",
                 "value": metadata_url
                },
                {"name": "dhus_product_url",
                 "type": "text",
                 "value": product_url
                },
                {"name": "datatake_id",
                 "type": "text",
                 "value": datatake_id
                },
                {"name": "orbit",
                 "type": "double",
                 "value": orbit
                 },
                {"name": "size",
                 "type": "double",
                 "value": size
                }]
        }

        # Insert geometries
        iterator = 0
        for coordinates in list_formatted_coordinates_corrected:
            dhus_metadata_annotation["values"].append(
                {"name": "coordinates_" + str(iterator),
                 "type": "geometry",
                 "value": list_formatted_coordinates_corrected[iterator].replace(",", " ")}
            )
            iterator += 1
        # end for

        list_of_annotations.append(dhus_metadata_annotation)

        ########
        # Define dhus product event
        ########
        links_dhus_product = []
        links_dhus_product_completeness = []
        alerts = []
        status = "PUBLISHED"
        if datatake_id in indexed_planned_imagings:
            # Obtain the planned imaging
            planned_imaging = indexed_planned_imagings[datatake_id]
            links_dhus_product.append({
                "link": str(planned_imaging.event_uuid),
                "link_mode": "by_uuid",
                "name": "DHUS_PRODUCT",
                "back_ref": "PLANNED_IMAGING"
            })
            links_dhus_product_completeness.append({
                "link": str(planned_imaging.event_uuid),
                "link_mode": "by_uuid",
                "name": "DHUS_PRODUCT_COMPLETENESS",
                "back_ref": "PLANNED_IMAGING"
            })
        else:
            status = "UNEXPECTED"
            alerts.append({
                "message": "The DHUS product {} could not be linked to any planned imaging".format(name),
                "generator": os.path.basename(__file__),
                "notification_time": (datetime.datetime.now()).isoformat(),
                "alert_cnf": {
                    "name": "ALERT-0200: NO PLANNED IMAGING FOR A DHUS PRODUCT",
                    "severity": "fatal",
                    "description": "Alert refers to the missing planned imaging for the corresponding DHUS product",
                    "group": "DHUS"
                }
            })
            ingestion_completeness = "false"
            ingestion_completeness_message = "MISSING_PLANNING"
        # end if

        # Dhus product event
        dhus_product_event = {
            "explicit_reference": name,
            "gauge": {
                "insertion_type": "SIMPLE_UPDATE",
                "name": "DHUS_PRODUCT",
                "system": satellite
            },
            "links": links_dhus_product,
            "alerts": alerts,
            "start": start,
            "stop": stop,
            "values": [
                {"name": "satellite",
                 "type": "text",
                 "value": satellite},
                {"name": "datatake_id",
                 "type": "text",
                 "value": datatake_id
                },
                {"name": "orbit",
                 "type": "double",
                 "value": orbit
                }
            ]
        }

        list_of_events.append(dhus_product_event)

        # Dhus product completeness event
        # Completeness timings
        completeness_start = (parser.parse(start) - datetime.timedelta(seconds=1)).isoformat()
        completeness_stop = stop
        level = levels[name[7:10]]
        dhus_product_completeness_event = {
            "explicit_reference": name,
            "gauge": {
                "insertion_type": "INSERT_and_ERASE_per_EVENT_with_PRIORITY",
                "name": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_" + level,
                "system": satellite
            },
            "links": links_dhus_product_completeness,
            "start": completeness_start,
            "stop": completeness_stop,
            "values": [
                {"name": "satellite",
                 "type": "text",
                 "value": satellite},
                {"name": "datatake_id",
                 "type": "text",
                 "value": datatake_id
                },
                {"name": "orbit",
                 "type": "double",
                 "value": orbit
                },
                {"name": "status",
                 "type": "text",
                 "value": status}
            ]
        }

        list_of_completeness_events.append(dhus_product_completeness_event)

    # end for
    
    # Build the json
    dhus_products_operation = {
        "mode": "insert",
        "dim_signature": {
            "name": "DHUS_PRODUCTS_" + satellite,
            "exec": os.path.basename(__file__),
            "version": version
        },
        "source": {
            "name": file_name,
            "reception_time": reception_time,
            "generation_time": reported_generation_time,
            "reported_validity_start": reported_validity_start,
            "reported_validity_stop": reported_validity_stop,
            "validity_start": validity_start,
            "validity_stop": validity_stop,
            "priority": 30,
            "ingestion_completeness": {
                "check": ingestion_completeness,
                "message": ingestion_completeness_message
            } 
        },
        "explicit_references": list_of_explicit_references,
        "events": list_of_events,
        "annotations": list_of_annotations
    }
    
    eboa_ingestion_functions.insert_ingestion_progress(session_progress, general_source_progress, 90)

    nppf_completeness_operation = {
        "mode": "insert",
        "dim_signature": {
            "name": "COMPLETENESS_NPPF_" + satellite,
            "exec": os.path.basename(__file__),
            "version": version
        },
        "source": {
            "name": file_name,
            "reception_time": reception_time,
            "generation_time": reported_generation_time,
            "reported_validity_start": reported_validity_start,
            "reported_validity_stop": reported_validity_stop,
            "validity_start": validity_start,
            "validity_stop": validity_stop,
            "priority": 30
        },
        "events": list_of_completeness_events
    }

    data = {"operations": [dhus_products_operation, nppf_completeness_operation]}
    
    eboa_ingestion_functions.insert_ingestion_progress(session_progress, general_source_progress, 100)

    query.close_session()

    new_file.close()
    new_file_with_wrong_characters.close()
    
    return data
