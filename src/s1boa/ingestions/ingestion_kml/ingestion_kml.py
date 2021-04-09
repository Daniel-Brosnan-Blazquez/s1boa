"""
Ingestion module for the KML files of Sentinel-1

Written by DEIMOS Space S.L. (dibb)

module s1boa
"""
# Import python utilities
import os
import tempfile
import pdb

# Import xml parser
from lxml import etree

# Import ingestion_functions.helpers
import eboa.ingestion.functions as eboa_ingestion_functions
import siboa.ingestions.functions as siboa_ingestion_functions

# Import query
from eboa.engine.query import Query

version = "1.0"

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
    """
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
    
    # Remove namespaces
    new_file = tempfile.NamedTemporaryFile()
    new_file_path = new_file.name
    eboa_ingestion_functions.remove_namespaces(file_path, new_file_path)

    eboa_ingestion_functions.insert_ingestion_progress(session_progress, general_source_progress, 20)

    parsed_xml = etree.parse(new_file_path)
    xpath_xml = etree.XPathEvaluator(parsed_xml)

    eboa_ingestion_functions.insert_ingestion_progress(session_progress, general_source_progress, 30)

    # Obtain metadata of the file
    file_name = os.path.basename(file_path)    
    satellite = xpath_xml("/kml/Document/Folder/Folder/name")[0].text
    period = xpath_xml("/kml/Document/name")[0].text.split("from")[1].replace(" ", "").split("to")
    validity_start = period[0]
    validity_stop = period[1]
    generation_time = validity_start

    eboa_ingestion_functions.insert_ingestion_progress(session_progress, general_source_progress, 40)

    #pdb.set_trace()
    
    # Generate the events containing the planned imaging
    list_of_events = []
    for planned_imaging in xpath_xml("/kml/Document/Folder/Folder/Placemark"):
        coordinates = planned_imaging.xpath("LinearRing/coordinates")[0].text
        list_coordinates = [group[0:len(group)-2] for group in coordinates.split(" ")]
        formatted_coordinates = " ".join(list_coordinates)

        # Correct longitude values to be inside the range (-180, 180)
        formatted_coordinates_to_correct = siboa_ingestion_functions.correct_longitude_in_allowed_range(formatted_coordinates)

        # Split geometries crossing the antimeridian
        list_formatted_coordinates_corrected = siboa_ingestion_functions.correct_antimeridian_issue_in_footprint(formatted_coordinates_to_correct)

        # Generate event
        values = [
                {"name": "satellite",
                 "type": "text",
                 "value": satellite},
                {"name": "datatake_id",
                 "type": "text",
                 "value": planned_imaging.xpath("ExtendedData/Data[@name = 'DatatakeId']/value")[0].text},
                {"name": "mode",
                 "type": "text",
                 "value": planned_imaging.xpath("ExtendedData/Data[@name = 'Mode']/value")[0].text},
                {"name": "swath",
                 "type": "text",
                 "value": planned_imaging.xpath("ExtendedData/Data[@name = 'Swath']/value")[0].text},
                {"name": "polarisation",
                 "type": "text",
                 "value": planned_imaging.xpath("ExtendedData/Data[@name = 'Polarisation']/value")[0].text},
                {"name": "orbit",
                 "type": "double",
                 "value": planned_imaging.xpath("ExtendedData/Data[@name = 'OrbitAbsolute']/value")[0].text}
        ]
        event = {
            "gauge": {
                "insertion_type": "INSERT_and_ERASE",
                "name": "PLANNED_IMAGING_KML",
                "system": satellite
            },
            "start": planned_imaging.xpath("TimeSpan/begin")[0].text,
            "stop": planned_imaging.xpath("TimeSpan/end")[0].text,
            "values": values
        }
        iterator = 0
        for coordinates in list_formatted_coordinates_corrected:
            values.append(
                {"name": "coordinates_" + str(iterator),
                 "type": "geometry",
                 "value": list_formatted_coordinates_corrected[iterator].replace(",", " ")}
            )
            iterator += 1
        # end for

        list_of_events.append(event)
    # end for

    data = {"operations": [{
        "mode": "insert_and_erase",
        "dim_signature": {
            "name": "KML_" + satellite,
            "exec": os.path.basename(__file__),
            "version": version
        },
        "source": {
            "name": file_name,
            "reception_time": reception_time,
            "generation_time": generation_time,
            "validity_start": validity_start,
            "validity_stop": validity_stop
        },
        "events": list_of_events
    }]}

    eboa_ingestion_functions.insert_ingestion_progress(session_progress, general_source_progress, 100)

    query.close_session()

    new_file.close()
    
    return data
