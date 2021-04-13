"""
Ingestion module for the NPPF files of Sentinel-1

Written by DEIMOS Space S.L. (dibb)

module s1boa
"""
# Import python utilities
import os
import argparse
from dateutil import parser
import datetime
import json
import pdb

# Import xml parser
from lxml import etree

# Import ingestion_functions.helpers
import eboa.ingestion.functions as eboa_ingestion_functions
import siboa.ingestions.functions as siboa_ingestion_functions

# Import debugging
from eboa.debugging import debug

# Import logging
from eboa.logging import Log

# Import query
from eboa.engine.query import Query

logging_module = Log(name = __name__)
logger = logging_module.logger

version = "1.0"
# chop_duration, warmup, preamble and postamble defined in RDB_SES_...xsl
imaging_modes={
    "0": {"group": "R", "short_name": "R", "long_name": "RESERVED", "chop_duration": 1, "warmup": 1, "preamble": 1, "postamble": 1},
    "1": {"group": "SM", "short_name": "S1", "long_name": "STRIPMAP1", "chop_duration": 5.000909, "warmup": 1.000182, "preamble": 1.299007, "postamble": 0.294014},
    "2": {"group": "SM", "short_name": "S2", "long_name": "STRIPMAP2", "chop_duration": 5.000620, "warmup": 1.000124, "preamble": 1.298983, "postamble": 0.341022},
    "3": {"group": "SM", "short_name": "S3", "long_name": "STRIPMAP3", "chop_duration": 5.000104, "warmup": 1.000021, "preamble": 1.298728, "postamble": 0.285720},
    "4": {"group": "SM", "short_name": "S4", "long_name": "STRIPMAP4", "chop_duration": 4.999485, "warmup": 0.999897, "preamble": 1.298654, "postamble": 0.333299},
    "5": {"group": "SM", "short_name": "S5N", "long_name": "STRIPMAP5_NORTHERN_HEMISPHERE", "chop_duration": 4.999631, "warmup": 0.999926, "preamble": 1.299009, "postamble": 0.289605},
    "6": {"group": "SM", "short_name": "S6", "long_name": "STRIPMAP6", "chop_duration": 4.998557, "warmup": 0.999711, "preamble": 1.299084, "postamble": 0.330632},
    "7": {"group": "R", "short_name": "R", "long_name": "RESERVED", "chop_duration": 5.000909, "warmup": 1.000182, "preamble": 1.299007, "postamble": 0.294014},
    "8": {"group": "IW", "short_name": "IW", "long_name": "INTERFEROMETRIC_WIDE_SWATH", "chop_duration": 5.516546, "warmup": 0.999924, "preamble": 1.298761, "postamble": 0.786299},
    "9": {"group": "WV", "short_name": "WV", "long_name": "WAVE", "chop_duration": 29.293952, "warmup": 0.999897, "preamble": 1.298654, "postamble": 0.556306},
    "10": {"group": "SM", "short_name": "S5S", "long_name": "STRIPMAP5_SOUTHERN_HEMISPHERE", "chop_duration": 5.000212, "warmup": 1.000042, "preamble": 1.298942, "postamble": 0.291480},
    "11": {"group": "SM", "short_name": "S1_WO_CAL", "long_name": "STRIPMAP1_WITHOUT_CALIBRATION", "chop_duration": 5.000909, "warmup": 1.000182, "preamble": 1.299007, "postamble": 0.294014},
    "12": {"group": "SM", "short_name": "S2_WO_CAL", "long_name": "STRIPMAP2_WITHOUT_CALIBRATION", "chop_duration": 5.000620, "warmup": 1.000124, "preamble": 1.298983, "postamble": 0.341022},
    "13": {"group": "SM", "short_name": "S3_WO_CAL", "long_name": "STRIPMAP3_WITHOUT_CALIBRATION", "chop_duration": 5.000104, "warmup": 1.000021, "preamble": 1.298728, "postamble": 0.285720},
    "14": {"group": "SM", "short_name": "S4_WO_CAL", "long_name": "STRIPMAP4_WITHOUT_CALIBRATION", "chop_duration": 4.999485, "warmup": 0.999897, "preamble": 1.298654, "postamble": 0.333299},
    "15": {"group": "CAL", "short_name": "RFC", "long_name": "RFC", "chop_duration": 1.020495, "warmup": 1.000182, "preamble": 1.299007, "postamble": 0.294014},
    "16": {"group": "TEST", "short_name": "TEST", "long_name": "TEST", "chop_duration": 0.012603, "warmup": 1.000000, "preamble": 1.299000, "postamble": 0.001000},
    "17": {"group": "SM", "short_name": "EN3", "long_name": "ELEVATION_NOTCH_STRIPMAP3", "chop_duration": 5.000715, "warmup": 1.000143, "preamble": 1.298756, "postamble": 0.291201},
    "18": {"group": "SM", "short_name": "AN1", "long_name": "AZIMUTH_NOTCH_STRIPMAP1", "chop_duration": 5.000909, "warmup": 1.000182, "preamble": 1.299007, "postamble": 0.294014},
    "19": {"group": "SM", "short_name": "AN2", "long_name": "AZIMUTH_NOTCH_STRIPMAP2", "chop_duration": 5.000620, "warmup": 1.000124, "preamble": 1.298983, "postamble": 0.341022},
    "20": {"group": "SM", "short_name": "AN3", "long_name": "AZIMUTH_NOTCH_STRIPMAP3", "chop_duration": 5.000104, "warmup": 1.000021, "preamble": 1.298728, "postamble": 0.285720},
    "21": {"group": "SM", "short_name": "AN4", "long_name": "AZIMUTH_NOTCH_STRIPMAP4", "chop_duration": 4.999485, "warmup": 0.999897, "preamble": 1.298654, "postamble": 0.333299},
    "22": {"group": "SM", "short_name": "AN5N", "long_name": "AZIMUTH_NOTCH_STRIPMAP5_NORTHERN_HEMISPHERE", "chop_duration": 4.999631, "warmup": 0.999926, "preamble": 1.299009, "postamble": 0.289605},
    "23": {"group": "SM", "short_name": "AN5S", "long_name": "AZIMUTH_NOTCH_STRIPMAP5_SOUTHERN_HEMISPHERE", "chop_duration": 5.000212, "warmup": 1.000042, "preamble": 1.298942, "postamble": 0.291480},
    "24": {"group": "SM", "short_name": "AN6", "long_name": "AZIMUTH_NOTCH_STRIPMAP6", "chop_duration": 4.998557, "warmup": 0.999711, "preamble": 1.299084, "postamble": 0.330632},
    "25": {"group": "SM", "short_name": "S5N_WO_CAL", "long_name": "STRIPMAP5_NORTHERN_HEMISPHERE_WITHOUT_CALIBRATION", "chop_duration": 4.999631, "warmup": 0.999926, "preamble": 1.299009, "postamble": 0.289605},
    "26": {"group": "SM", "short_name": "S5S_WO_CAL", "long_name": "STRIPMAP5_SOUTHERN_HEMISPHERE_WITHOUT_CALIBRATION", "chop_duration": 5.000212, "warmup": 1.000042, "preamble": 1.298942, "postamble": 0.291480},
    "27": {"group": "SM", "short_name": "S6_WO_CAL", "long_name": "STRIPMAP6_WITHOUT_CALIBRATION", "chop_duration": 4.998557, "warmup": 0.999711, "preamble": 1.299084, "postamble": 0.330632},
    "28": {"group": "R", "short_name": "R", "long_name": "RESERVED", "chop_duration": 1, "warmup": 0.003667, "preamble": 0, "postamble": 0.003667},
    "29": {"group": "R", "short_name": "R", "long_name": "RESERVED", "chop_duration": 1, "warmup": 0.009016, "preamble": 0, "postamble": 0.009016},
    "30": {"group": "R", "short_name": "R", "long_name": "RESERVED", "chop_duration": 1.5, "warmup": 0.011000, "preamble": 0, "postamble": 0.011000},
    "31": {"group": "SM", "short_name": "EN3_WO_CAL", "long_name": "ELEVATION_NOTCH_STRIPMAP3_WITHOUT_CALIBRATION", "chop_duration": 5.000715, "warmup": 1.000143, "preamble": 1.298756, "postamble": 0.291201},
    "32": {"group": "EW", "short_name": "EW", "long_name": "EXTRA_WIDE_SWATH", "chop_duration": 3.038376, "warmup": 1.000049, "preamble": 1.298707, "postamble": 1.160363},
    "33": {"group": "SM", "short_name": "AN1_WO_CAL", "long_name": "AZIMUTH_NOTCH_STRIPMAP1_WITHOUT_CALIBRATION", "chop_duration": 5.000909, "warmup": 1.000182, "preamble": 1.299007, "postamble": 0.294014},
    "34": {"group": "SM", "short_name": "AN3_WO_CAL", "long_name": "AZIMUTH_NOTCH_STRIPMAP3_WITHOUT_CALIBRATION", "chop_duration": 5.000104, "warmup": 1.000021, "preamble": 1.298728, "postamble": 0.285720},
    "35": {"group": "SM", "short_name": "AN6_WO_CAL", "long_name": "AZIMUTH_NOTCH_STRIPMAP6_WITHOUT_CALIBRATION", "chop_duration": 4.998557, "warmup": 0.999711, "preamble": 1.299084, "postamble": 0.330632},
    "36": {"group": "R", "short_name": "R", "long_name": "RESERVED", "chop_duration": 0.983607, "warmup": 0.003607, "preamble": 0, "postamble": 0.003607},
    "37": {"group": "SM", "short_name": "NS1", "long_name": "NOISE_STRIPMAP1", "chop_duration": 0.025659, "warmup": 1.000182, "preamble": 1.299007, "postamble": 0.294014},
    "38": {"group": "SM", "short_name": "NS2", "long_name": "NOISE_STRIPMAP2", "chop_duration": 0.029762, "warmup": 1.000124, "preamble": 1.298983, "postamble": 0.341022},
    "39": {"group": "SM", "short_name": "NS3", "long_name": "NOISE_STRIPMAP3", "chop_duration": 0.024936, "warmup": 1.000021, "preamble": 1.298728, "postamble": 0.285720},
    "40": {"group": "SM", "short_name": "NS4", "long_name": "NOISE_STRIPMAP4", "chop_duration": 0.029088, "warmup": 0.999897, "preamble": 1.298654, "postamble": 0.333299},
    "41": {"group": "SM", "short_name": "NS5N", "long_name": "NOISE_STRIPMAP5_NORTHERN_HEMISPHERE", "chop_duration": 0.025275, "warmup": 0.999926, "preamble": 1.299009, "postamble": 0.289605},
    "42": {"group": "SM", "short_name": "NS5S", "long_name": "NOISE_STRIPMAP5_SOUTHERN_HEMISPHERE", "chop_duration": 0.025438, "warmup": 1.000042, "preamble": 1.298942, "postamble": 0.291480},
    "43": {"group": "SM", "short_name": "NS6", "long_name": "NOISE_STRIPMAP6", "chop_duration": 0.028855, "warmup": 0.999711, "preamble": 1.299084, "postamble": 0.330632},
    "44": {"group": "EW", "short_name": "NEW", "long_name": "NOISE_EXTRA_WIDE", "chop_duration": 0.137736, "warmup": 1.000049, "preamble": 1.298707, "postamble": 1.160363},
    "45": {"group": "IW", "short_name": "NIW", "long_name": "NOISE_INTERFEROMETRIC", "chop_duration": 0.089493, "warmup": 0.999924, "preamble": 1.298761, "postamble": 0.786299},
    "46": {"group": "WV", "short_name": "NWV", "long_name": "NOISE_WAVE", "chop_duration": 0.058176, "warmup": 0.999897, "preamble": 1.298654, "postamble": 0.556306},
    "47": {"group": "R", "short_name": "R", "long_name": "RESERVED", "chop_duration": 5.000909, "warmup": 1.000182, "preamble": 1.299007, "postamble": 0.294014}
}

imaging_request_operations = {
    "MPSARRFB": "BASIC_CALIBRATION",
    "MPSARRFC": "SAR_COMBINED_RFC",
    "MPSARDT2": "NOMINAL",
    "MPPASTH1": "PASS_THOUGH",
    "MPPASTHD": "PASS_THOUGH_SAR",
}

polarisations = {
    "0": "H",
    "1": "HH",
    "2": "HV",
    "3": "HHV",
    "4": "V",
    "5": "VH",
    "6": "VV",
    "7": "VHV",
}

playback_types={
    "MPPDHS": "NOMINAL",
    "MPMMPREG": "PASS_THROUGH",
    "MPMMPBRT": "PASS_THROUGH_SAR",
}

playback_means={
    "MPPDHXON": "XBAND",
    "MPG1STRT": "OCP",
    "MPG2STRT": "OCP",
    "MPG3STRT": "OCP"
}

playback_means_by_stop={
    "MPPDHXOF": "XBAND",
    "MPOCPRDY": "OCP"
}

@debug
def _generate_imaging_events(xpath_xml, source, list_of_events):
    """
    Method to generate the events for the imaging operations
    :param xpath_xml: source of information that was xpath evaluated
    :type xpath_xml: XPathEvaluator
    :param source: information of the source
    :type xpath_xml: dict
    :param list_of_events: list to store the events to be inserted into the eboa
    :type list_of_events: list
    """

    #pdb.set_trace()

    satellite = source["name"][0:3]

    # Imaging operations
    imaging_operations = xpath_xml("/Earth_Explorer_File/Data_Block/List_of_EVRQs/EVRQ[RQ/RQ_Name='MPSARRFB' or RQ/RQ_Name='MPSARRFC' or RQ/RQ_Name='MPSARDT2' or RQ/RQ_Name='MPPASTH1' or RQ/RQ_Name='MPPASTHD']")
    imaging_operations = xpath_xml("/Earth_Explorer_File/Data_Block/List_of_EVRQs/EVRQ[RQ/RQ_Name='MPSARDT2']")

    for imaging_operation in imaging_operations:

        ########
        # Obtain metadata
        ########
        # Request
        imaging_request = imaging_operation.xpath("RQ/RQ_Name")[0].text
        imaging_request_operation = imaging_request_operations[imaging_request]
        
        # Imaging mode
        ecc = imaging_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'ECCPRNR']/RQ_Parameter_Value")[0].text
        imaging_mode = imaging_modes[ecc]

        # Warm up
        warmup = imaging_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'WARM_UP']/RQ_Parameter_Value")[0].text

        # Polarisation
        polarisation_code = imaging_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'POLAR']/RQ_Parameter_Value")[0].text
        polarisation = polarisations[polarisation_code]

        # ORBIT SWATH and BAQ metadata not yet understood
        
        # Datatake ID
        datatake_id_code = imaging_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'DT_ID']/RQ_Parameter_Value")[0].text
        # The datatake id is corresponding to the 23 most significant bits. As the value has 32, to obtain the datatake id the 9 least significant bits are discarded
        datatake_id = hex(int((int(datatake_id_code,16) >> 9).to_bytes(4,'big').hex(), 16)).replace("0x", "").upper()

        # Number of chops
        number_of_chops = imaging_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'N_PG_REP']/RQ_Parameter_Value")[0].text

        ########
        # Obtain timings
        ########
        # Imaging start information
        operation_start = imaging_operation.xpath("EVRQ_Header/EVRQ_Time")[0].text.split("=")[1]
        imaging_start_datetime = parser.parse(operation_start) + datetime.timedelta(seconds=imaging_mode["preamble"])
        if warmup == "1":
            imaging_start_datetime = imaging_start_datetime + datetime.timedelta(seconds=imaging_mode["warmup"])
        # end if
        imaging_start = imaging_start_datetime.isoformat()
        imaging_start_orbit = imaging_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'ORB_NUM']/RQ_Parameter_Value")[0].text
        imaging_start_angle = imaging_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'ORB_ANGL']/RQ_Parameter_Value")[0].text

        # Duration (if N_PG_REP = 0 -> observation will be 1 chop)
        duration = (float(number_of_chops) + 1) * imaging_mode["chop_duration"]

        # Imaging start information
        imaging_stop_datetime = imaging_start_datetime + datetime.timedelta(seconds=duration)
        imaging_stop = imaging_stop_datetime.isoformat()

        # print("{};{};{};{};{};{};{}".format(imaging_start.split(".")[0], datatake_id, ecc, imaging_mode["short_name"], number_of_chops, duration))
        
        # # Imaging event
        # imaging_event = {
        #     "link_ref": imaging_link_id,
        #     "gauge": {
        #         "insertion_type": "INSERT_and_ERASE",
        #         "name": "PLANNED_IMAGING",
        #         "system": satellite
        #     },
        #     "start": imaging_start,
        #     "stop": imaging_stop,
        #     "values": [
        #         {"name": "start_request",
        #          "type": "text",
        #          "value": imaging_start_request},
        #         {"name": "stop_request",
        #          "type": "text",
        #          "value": imaging_stop_request},
        #         {"name": "start_orbit",
        #          "type": "double",
        #          "value": imaging_start_orbit},
        #         {"name": "start_angle",
        #          "type": "double",
        #          "value": imaging_start_angle},
        #         {"name": "stop_orbit",
        #          "type": "double",
        #          "value": imaging_stop_orbit},
        #         {"name": "stop_angle",
        #          "type": "double",
        #          "value": imaging_stop_angle},
        #         {"name": "satellite",
        #          "type": "text",
        #          "value": satellite},
        #         {"name": "imaging_mode",
        #          "type": "text",
        #          "value": imaging_mode}
        #     ]
        # }

        # # Insert imaging_event
        # eboa_ingestion_functions.insert_event_for_ingestion(imaging_event, source, list_of_events)

    # end for

    return

@debug
def _generate_idle_events(xpath_xml, source, list_of_events):
    """
    Method to generate the events for the idle operation of the satellite
    :param xpath_xml: source of information that was xpath evaluated
    :type xpath_xml: XPathEvaluator
    :param source: information of the source
    :type xpath_xml: dict
    :param list_of_events: list to store the events to be inserted into the eboa
    :type list_of_events: list
    """

    satellite = source["name"][0:3]

    # Idle operations
    idle_operations = xpath_xml("/Earth_Explorer_File/Data_Block/List_of_EVRQs/EVRQ[RQ/RQ_Name='MPMSIMID' or RQ/RQ_Name='MPMSSBID']")

    for idle_operation in idle_operations:
        # Idle start information
        idle_start = idle_operation.xpath("RQ/RQ_Execution_Time")[0].text.split("=")[1]
        idle_start_orbit = idle_operation.xpath("RQ/RQ_Absolute_orbit")[0].text
        idle_start_angle = idle_operation.xpath("RQ/RQ_Deg_from_ANX")[0].text
        idle_start_request = idle_operation.xpath("RQ/RQ_Name")[0].text

        # Idle stop information
        idle_operation_stop = idle_operation.xpath("following-sibling::EVRQ[RQ/RQ_Name='MPMSSCAL' or RQ/RQ_Name='MPMSDASC' or RQ/RQ_Name='MPMSDCLO' or RQ/RQ_Name='MPMSIVIC' or RQ/RQ_Name='MPMSNOBS' or RQ/RQ_Name='MPMSIRAW' or RQ/RQ_Name='MPMSIDTS' or RQ/RQ_Name='MPMSIDSB'][1]")
        if len(idle_operation_stop) == 1:
            idle_stop_orbit = idle_operation_stop[0].xpath("RQ/RQ_Absolute_orbit")[0].text
            idle_stop_angle = idle_operation_stop[0].xpath("RQ/RQ_Deg_from_ANX")[0].text
            idle_stop = idle_operation_stop[0].xpath("RQ/RQ_Execution_Time")[0].text.split("=")[1]
            idle_stop_request = idle_operation_stop[0].xpath("RQ/RQ_Name")[0].text
            values = [
                {"name": "start_request",
                 "type": "text",
                 "value": idle_start_request},
                {"name": "stop_request",
                 "type": "text",
                 "value": idle_stop_request},
                {"name": "start_orbit",
                 "type": "double",
                 "value": idle_start_orbit},
                {"name": "start_angle",
                 "type": "double",
                 "value": idle_start_angle},
                {"name": "stop_orbit",
                 "type": "double",
                 "value": idle_stop_orbit},
                {"name": "stop_angle",
                 "type": "double",
                 "value": idle_stop_angle},
                {"name": "satellite",
                 "type": "text",
                 "value": satellite}
            ]
        else:
            idle_stop_orbit = None
            idle_stop_angle = None
            idle_stop = source["validity_stop"]
            idle_stop_request = None
            values = [
                {"name": "start_request",
                 "type": "text",
                 "value": idle_start_request},
                {"name": "start_orbit",
                 "type": "double",
                 "value": idle_start_orbit},
                {"name": "start_angle",
                 "type": "double",
                 "value": idle_start_angle},
                {"name": "satellite",
                 "type": "text",
                 "value": satellite}
            ]
        # end if

        # Idle event
        idle_event = {
            "link_ref": "idle_" + str(idle_start),
            "gauge": {
                "insertion_type": "INSERT_and_ERASE",
                "name": "PLANNED_IDLE",
                "system": satellite
            },
            "start": idle_start,
            "stop": idle_stop,
            "values": values
        }

        # Insert idle_event
        eboa_ingestion_functions.insert_event_for_ingestion(idle_event, source, list_of_events)

    # end for

    return

@debug
def _generate_playback_events(xpath_xml, source, list_of_events):
    """
    Method to generate the events for the idle operation of the satellite
    :param xpath_xml: source of information that was xpath evaluated
    :type xpath_xml: XPathEvaluator
    :param source: information of the source
    :type xpath_xml: dict
    :param list_of_events: list to store the events to be inserted into the eboa
    :type list_of_events: list

    Conceptual design of what is expected given the following inputs
    PLAYBACK MEAN      |------------XBAND------------|
    PLAYBACK MEAN                           |------------OCP-----------|
    PLAYBACK TYPES      |--NOM--||SAD|   |NOM||SAD|     |--NOM--||SAD|
    
    RESULT:
    PB MEAN EVENT 1    |------------XBAND------------|
    PB TY EVS LINKED    |--NOM--||SAD|   |NOM||SAD|
    PB MEAN EVENT 2                         |------------OCP----------
    PB TY EVS LINKED                                    |--NOM--||SAD|

    PB MEAN events and PB TY events are linked
    """
    
    satellite = source["name"][0:3]

    # Playback operations
    playback_operations = xpath_xml("/Earth_Explorer_File/Data_Block/List_of_EVRQs/EVRQ[(RQ/RQ_Name='MPXBSBOP' and boolean(following-sibling::EVRQ[RQ/RQ_Name='MPXBOPSB'])) or ((RQ/RQ_Name='MPG1STRT' or RQ/RQ_Name='MPG2STRT' or RQ/RQ_Name='MPG3STRT') and boolean(following-sibling::EVRQ[RQ/RQ_Name='MPOCPRY2']))]")

    for playback_operation in playback_operations:
        # Playback start information
        playback_start = playback_operation.xpath("RQ/RQ_Execution_Time")[0].text.split("=")[1]
        playback_start_orbit = playback_operation.xpath("RQ/RQ_Absolute_orbit")[0].text
        playback_start_angle = playback_operation.xpath("RQ/RQ_Deg_from_ANX")[0].text
        playback_start_request = playback_operation.xpath("RQ/RQ_Name")[0].text

        playback_mean = playback_means[playback_start_request]

        # Playback stop information
        if playback_mean == "XBAND":
            playback_operation_stop = playback_operation.xpath("following-sibling::EVRQ[RQ/RQ_Name='MPXBOPSB'][1]")[0]
        else:
            playback_operation_stop = playback_operation.xpath("following-sibling::EVRQ[RQ/RQ_Name='MPOCPRY2'][1]")[0]
        # end if
        playback_stop_orbit = playback_operation_stop.xpath("RQ/RQ_Absolute_orbit")[0].text
        playback_stop_angle = playback_operation_stop.xpath("RQ/RQ_Deg_from_ANX")[0].text
        playback_stop = playback_operation_stop.xpath("RQ/RQ_Execution_Time")[0].text.split("=")[1]
        playback_stop_request = playback_operation_stop.xpath("RQ/RQ_Name")[0].text

        playback_mean_link_id = "playback_mean_" + playback_stop

        # Playback event
        playback_event = {
            "link_ref": playback_mean_link_id,
            "gauge": {
                "insertion_type": "INSERT_and_ERASE",
                "name": "PLANNED_PLAYBACK_MEAN",
                "system": satellite
            },
            "start": playback_start,
            "stop": playback_stop,
            "values": [
                {"name": "start_request",
                 "type": "text",
                 "value": playback_start_request},
                {"name": "stop_request",
                 "type": "text",
                 "value": playback_stop_request},
                {"name": "start_orbit",
                 "type": "double",
                 "value": playback_start_orbit},
                {"name": "start_angle",
                 "type": "double",
                 "value": playback_start_angle},
                {"name": "stop_orbit",
                 "type": "double",
                 "value": playback_stop_orbit},
                {"name": "stop_angle",
                 "type": "double",
                 "value": playback_stop_angle},
                {"name": "satellite",
                 "type": "text",
                 "value": satellite},
                {"name": "playback_mean",
                 "type": "text",
                 "value": playback_mean}
            ]
        }

        # Insert playback_event
        eboa_ingestion_functions.insert_event_for_ingestion(playback_event, source, list_of_events)

    # end for


    # Associate the playback types to the playback means
    playback_type_start_operations = xpath_xml("/Earth_Explorer_File/Data_Block/List_of_EVRQs/EVRQ[(((RQ/RQ_Name='MPMMPNOM' or RQ/RQ_Name='MPMMPREG' or RQ/RQ_Name='MPMMPBRT' or RQ/RQ_Name='MPMMPNRT') and boolean(following-sibling::EVRQ[RQ/RQ_Name='MPMMPSTP'])) or RQ/RQ_Name='MPMMPBHK' or RQ/RQ_Name='MPMMPBSA' or RQ/RQ_Name='MPMMPBHS')  and (boolean(following-sibling::EVRQ[RQ/RQ_Name='MPXBOPSB']) or boolean(following-sibling::EVRQ[RQ/RQ_Name='MPOCPRY2']))]")

    for playback_type_start_operation in playback_type_start_operations:

        # Playback_Type start information
        playback_type_start = playback_type_start_operation.xpath("RQ/RQ_Execution_Time")[0].text.split("=")[1]
        playback_type_start_orbit = playback_type_start_operation.xpath("RQ/RQ_Absolute_orbit")[0].text
        playback_type_start_angle = playback_type_start_operation.xpath("RQ/RQ_Deg_from_ANX")[0].text
        playback_type_start_request = playback_type_start_operation.xpath("RQ/RQ_Name")[0].text

        playback_type = playback_types[playback_type_start_request]

        if playback_type in ["HKTM", "SAD", "HKTM_SAD"]:
            playback_type_stop_operation = playback_type_start_operation
        else:
            playback_type_stop_operation = playback_type_start_operation.xpath("following-sibling::EVRQ[RQ/RQ_Name='MPMMPSTP'][1]")[0]
        # end if

        # Playback_Type stop information
        playback_type_stop = playback_type_stop_operation.xpath("RQ/RQ_Execution_Time")[0].text.split("=")[1]
        playback_type_stop_orbit = playback_type_stop_operation.xpath("RQ/RQ_Absolute_orbit")[0].text
        playback_type_stop_angle = playback_type_stop_operation.xpath("RQ/RQ_Deg_from_ANX")[0].text
        playback_type_stop_request = playback_type_stop_operation.xpath("RQ/RQ_Name")[0].text

        playback_mean = playback_type_start_operation.xpath("following-sibling::EVRQ[RQ/RQ_Name='MPXBOPSB' or RQ/RQ_Name='MPOCPRY2'][1]")
        if len (playback_mean) > 0:
            playback_mean_start_request = playback_mean[0].xpath("RQ/RQ_Name")[0].text

            playback_mean = playback_means_by_stop[playback_mean_start_request]
        else:
            playback_mean = "N/A"
        # end if

        playback_mean_stop = playback_type_start_operation.xpath("following-sibling::EVRQ[RQ/RQ_Name='MPXBOPSB' or RQ/RQ_Name='MPOCPRY2'][1]")[0].xpath("RQ/RQ_Execution_Time")[0].text.split("=")[1]
        playback_mean_link_id = "playback_mean_" + playback_mean_stop

        # Playback_Type event
        playback_type_event = {
            "link_ref": "playback_" + playback_type_start,
            "gauge": {
                "insertion_type": "INSERT_and_ERASE",
                "name": "PLANNED_PLAYBACK",
                "system": satellite
            },
            "start": playback_type_start,
            "stop": playback_type_stop,
            "links": [
                {
                    "link": playback_mean_link_id,
                    "link_mode": "by_ref",
                    "name": "PLANNED_PLAYBACK",
                    "back_ref": "PLANNED_PLAYBACK_MEAN"
                }
            ],
            "values": [
                {"name": "start_request",
                 "type": "text",
                 "value": playback_type_start_request},
                {"name": "stop_request",
                 "type": "text",
                 "value": playback_type_stop_request},
                {"name": "start_orbit",
                 "type": "double",
                 "value": playback_type_start_orbit},
                {"name": "start_angle",
                 "type": "double",
                 "value": playback_type_start_angle},
                {"name": "stop_orbit",
                 "type": "double",
                 "value": playback_type_stop_orbit},
                {"name": "stop_angle",
                 "type": "double",
                 "value": playback_type_stop_angle},
                {"name": "satellite",
                 "type": "text",
                 "value": satellite},
                {"name": "playback_mean",
                 "type": "text",
                 "value": playback_mean},
                {"name": "playback_type",
                 "type": "text",
                 "value": playback_type}
            ]
        }

        parameters = []
        playback_type_event["values"].append(
            {"name": "parameters",
             "type": "object",
             "values": parameters},
        )
        if playback_type == "HKTM_SAD":
            parameters.append(
                {"name": "MEM_FRHK",
                 "type": "double",
                 "value": playback_type_start_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'MEM_FRHK']/RQ_Parameter_Value")[0].text},
            )
            parameters.append(
                {"name": "MEM_FSAD",
                 "type": "double",
                 "value": playback_type_start_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'MEM_FSAD']/RQ_Parameter_Value")[0].text},
            )
        # end if
        if playback_type in ["HKTM", "SAD", "NOMINAL", "REGULAR", "NRT", "RT"]:
            parameters.append(
                {"name": "MEM_FREE",
                 "type": "double",
                 "value": playback_type_start_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'MEM_FREE']/RQ_Parameter_Value")[0].text},
            )
        # end if
        if playback_type in ["NOMINAL", "REGULAR", "NRT"]:
            parameters.append(
                {"name": "SCN_DUP",
                 "type": "double",
                 "value": playback_type_stop_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'SCN_DUP']/RQ_Parameter_Value")[0].text},
            )
            parameters.append(
                {"name": "SCN_RWD",
                 "type": "double",
                 "value": playback_type_stop_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'SCN_RWD']/RQ_Parameter_Value")[0].text},
            )
        # end if
        if playback_type == "RT":
            parameters.append(
                {"name": "SCN_DUP_START",
                 "type": "double",
                 "value": playback_type_start_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'SCN_DUP']/RQ_Parameter_Value")[0].text},
            )
            parameters.append(
                {"name": "SCN_DUP_STOP",
                 "type": "double",
                 "value": playback_type_stop_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'SCN_DUP']/RQ_Parameter_Value")[0].text},
            )
            parameters.append(
                {"name": "SCN_RWD",
                 "type": "double",
                 "value": playback_type_stop_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'SCN_RWD']/RQ_Parameter_Value")[0].text},
            )
        # end if

        # Insert playback_type_event
        eboa_ingestion_functions.insert_event_for_ingestion(playback_type_event, source, list_of_events)

    # end for

    return

def process_file(file_path, engine, query, reception_time, tgz_filename = None):
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
    list_of_events = []
    if tgz_filename != None:
        file_name = tgz_filename
    else:
        file_name = os.path.basename(file_path)
    # end if
    parsed_xml = etree.parse(file_path)
    xpath_xml = etree.XPathEvaluator(parsed_xml)

    satellite = file_name[0:3]
    reported_generation_time = xpath_xml("/Earth_Explorer_File/Earth_Explorer_Header/Fixed_Header/Source/Creation_Date")[0].text.split("=")[1]    
    reported_validity_start = xpath_xml("/Earth_Explorer_File/Earth_Explorer_Header/Fixed_Header/Validity_Period/Validity_Start")[0].text.split("=")[1]
    validity_stop = xpath_xml("/Earth_Explorer_File/Earth_Explorer_Header/Fixed_Header/Validity_Period/Validity_Stop")[0].text.split("=")[1]
    deletion_queue = xpath_xml("/Earth_Explorer_File/Data_Block/List_of_EVRQs/EVRQ[RQ/RQ_Name='MGSYQDEL']")

    # Generation time is changed to be the validity start in case the generation time is greater than the validity start to avoid problems on completeness analysis
    generation_time = reported_generation_time
    if reported_generation_time > reported_validity_start:
        generation_time = reported_validity_start
    # end if

    validity_start = reported_validity_start
    if len(deletion_queue) == 1:
        validity_start = deletion_queue[0].xpath("RQ/RQ_Execution_Time")[0].text.split("=")[1]
    # end if

    source = {
        "name": file_name,
        "reception_time": reception_time,
        "generation_time": generation_time,
        "reported_generation_time": reported_generation_time,
        "validity_start": validity_start,
        "reported_validity_start": reported_validity_start,
        "validity_stop": validity_stop
    }

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

    # Generate imaging events
    _generate_imaging_events(xpath_xml, source, list_of_events)

    eboa_ingestion_functions.insert_ingestion_progress(session_progress, general_source_progress, 40)

    # # Generate playback events
    # _generate_playback_events(xpath_xml, source, list_of_events)

    # eboa_ingestion_functions.insert_ingestion_progress(session_progress, general_source_progress, 70)

    # # Generate idle events
    # _generate_idle_events(xpath_xml, source, list_of_events)

    # eboa_ingestion_functions.insert_ingestion_progress(session_progress, general_source_progress, 95)
    
    # Build the xml
    data = {"operations": [{
        "mode": "insert_and_erase",
        "dim_signature": {
            "name": "NPPF_" + satellite,
            "exec": os.path.basename(__file__),
            "version": version
        },
        "source": source,
        "events": list_of_events
    }]}

    eboa_ingestion_functions.insert_ingestion_progress(session_progress, general_source_progress, 100)

    query.close_session()
    
    return data
