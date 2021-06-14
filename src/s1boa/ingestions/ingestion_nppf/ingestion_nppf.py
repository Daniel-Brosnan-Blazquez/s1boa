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

# Import xml parser
from lxml import etree

# Import ingestion_functions.helpers
import eboa.ingestion.functions as eboa_ingestion_functions
import siboa.ingestions.functions as siboa_ingestion_functions
import s1boa.ingestions.functions as s1boa_ingestion_functions

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
    "MPPASTH1": "PASS_THROUGH",
    "MPPASTHD": "PASS_THROUGH_SAR",
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
def _generate_imaging_events(xpath_xml, source, events_per_imaging_mode, completeness_events_per_imaging_mode):
    """
    Method to generate the events for the imaging operations
    :param xpath_xml: source of information that was xpath evaluated
    :type xpath_xml: XPathEvaluator
    :param source: information of the source
    :type xpath_xml: dict
    :param events_per_imaging_mode: dict to store the events per imaging mode
    :type events_per_imaging_mode: dict
    :param completeness_events_per_imaging_mode: dict to store the completeness events per imaging mode
    :type completeness_events_per_imaging_mode: dict
    """

    satellite = source["name"][0:3]

    # Imaging operations (calibrations are skipped for the moment)
    imaging_operations = xpath_xml("/Earth_Explorer_File/Data_Block/List_of_EVRQs/EVRQ[RQ/RQ_Name='MPSARRFB' or RQ/RQ_Name='MPSARRFC' or RQ/RQ_Name='MPSARDT2' or RQ/RQ_Name='MPPASTH1' or RQ/RQ_Name='MPPASTHD']")
    imaging_operations = xpath_xml("/Earth_Explorer_File/Data_Block/List_of_EVRQs/EVRQ[RQ/RQ_Name='MPSARDT2' or RQ/RQ_Name='MPPASTH1' or RQ/RQ_Name='MPPASTHD']")

    for imaging_operation in imaging_operations:

        ########
        # Obtain metadata
        ########
        # Request
        imaging_request = imaging_operation.xpath("RQ/RQ_Name")[0].text
        imaging_request_operation = imaging_request_operations[imaging_request]

        # Request id
        request_id = imaging_operation.xpath("RQ/List_of_RQ_Attributes/RQ_Attribute[RQ_Attribute_Name = 'RQ_ID']/RQ_Attribute_Value")[0].text

        # Imaging mode
        ecc = imaging_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'ECCPRNR']/RQ_Parameter_Value")[0].text
        imaging_mode = imaging_modes[ecc]

        # Warm up
        warmup = imaging_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'WARM_UP']/RQ_Parameter_Value")[0].text

        # Polarisation
        polarisation_code = imaging_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'POLAR']/RQ_Parameter_Value")[0].text
        polarisation = polarisations[polarisation_code]

        # ORB_SWTH, BAQXXX, SDI time (WI_TO_FL, IN_TO_FL, I_TO_VAL, W_TO_VAL) metadata not yet understood if needed
        
        # Datatake ID
        datatake_id_code = imaging_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'DT_ID']/RQ_Parameter_Value")[0].text
        # The datatake id is corresponding to the 23 most significant bits. As the value has 32, to obtain the datatake id the 9 least significant bits are discarded
        datatake_id = hex(int((int(datatake_id_code,16) >> 9).to_bytes(4,'big').hex(), 16)).replace("0x", "").upper()

        # Number of chops
        number_of_chops = imaging_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'N_PG_REP']/RQ_Parameter_Value")[0].text
        
        ########
        # Obtain timings, orbit and angle
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

        # print("{};{};{};{};{};{}".format(imaging_start.split(".")[0], datatake_id, ecc, imaging_mode["short_name"], number_of_chops, duration))

        ########
        # Define imaging event
        ########        
        # Imaging event
        imaging_event_values = [
            {"name": "satellite",
             "type": "text",
             "value": satellite},
            {"name": "request_id",
             "type": "text",
             "value": request_id},
            {"name": "request",
             "type": "text",
             "value": imaging_request},
            {"name": "imaging_operation",
             "type": "text",
             "value": imaging_request_operation},
            {"name": "start_orbit",
             "type": "double",
             "value": imaging_start_orbit},
            {"name": "start_angle",
             "type": "double",
             "value": imaging_start_angle},
            {"name": "ecc",
             "type": "text",
             "value": ecc},
            {"name": "imaging_mode",
             "type": "text",
             "value": imaging_mode["short_name"]},
            {"name": "imaging_mode_long_name",
             "type": "text",
             "value": imaging_mode["long_name"]},
            {"name": "warmup",
             "type": "text",
             "value": warmup},
            {"name": "polarisation",
             "type": "text",
             "value": polarisation},
            {"name": "datatake_id",
             "type": "text",
             "value": datatake_id},
            {"name": "number_of_chops",
             "type": "double",
             "value": number_of_chops},
        ]
        imaging_event_link_ref = "PLANNED_IMAGING_" + imaging_start
        imaging_event = {
            "link_ref": imaging_event_link_ref,
            "gauge": {
                "insertion_type": "INSERT_and_ERASE",
                "name": "PLANNED_IMAGING",
                "system": satellite
            },
            "start": imaging_start,
            "stop": imaging_stop,
            "values": imaging_event_values
        }

        ########
        # Define packet storage
        ########        
        # Packet store ids (enabled by ENA_PS_V and ENA_PS_H -
        # supposed to be always activated, otherwise values will be
        # empty and not inserted in the event)
        if imaging_request == "MPSARDT2":
            h_packet_store_id_node = imaging_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'PS_ID_H']/RQ_Parameter_Value")
            if len(h_packet_store_id_node) > 0:
                h_packet_store_id = h_packet_store_id_node[0].text
                imaging_event_values.append({
                    "name": "h_packet_store_id",
                    "type": "double",
                    "value": int(h_packet_store_id)})
            # end if
            v_packet_store_id_node = imaging_operation.xpath("RQ/List_of_RQ_Parameters/RQ_Parameter[RQ_Parameter_Name = 'PS_ID_V']/RQ_Parameter_Value")
            if len(v_packet_store_id_node) > 0:
                v_packet_store_id = v_packet_store_id_node[0].text
                imaging_event_values.append({
                    "name": "v_packet_store_id",
                    "type": "double",
                    "value": int(v_packet_store_id)})
            # end if
        # end if

        # Insert event
        s1boa_ingestion_functions.insert_event(imaging_event, events_per_imaging_mode, imaging_mode["short_name"], source)

        ########
        # Define completeness events
        ########
        # Completeness values
        completeness_event_values = imaging_event_values + [
            {"name": "status",
             "type": "text",
             "value": "MISSING"}]

        # Completeness timings
        start = (imaging_start_datetime + datetime.timedelta(seconds=10)).isoformat()
        stop = (imaging_stop_datetime - datetime.timedelta(seconds=20)).isoformat()

        if start > stop:
            start = imaging_start
            stop = (imaging_start_datetime + datetime.timedelta(seconds=1)).isoformat()
        # end if

        # DHUS product completeness events
        # L0
        if imaging_mode["group"] != "WV":
            completeness_event = {
                "gauge": {
                    "insertion_type": "INSERT_and_ERASE_INTERSECTED_EVENTS_with_PRIORITY",
                    "name": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0",
                    "system": satellite
                },
                "links": [{
                    "link": imaging_event_link_ref,
                    "link_mode": "by_ref",
                    "name": "DHUS_PRODUCT_COMPLETENESS",
                    "back_ref": "PLANNED_IMAGING"
                }],
                "start": start,
                "stop": stop,
                "values": completeness_event_values,
                "alerts": [{
                    "message": "The L0 product related to the datatake id {} and corresponding to the planned imaging with mode {} and timings {}_{} over orbit {} has not been published".format(datatake_id, imaging_mode["long_name"], imaging_start, imaging_stop, int(imaging_start_orbit)),
                    "generator": os.path.basename(__file__),
                    "notification_time": (imaging_start_datetime + datetime.timedelta(hours=24)).isoformat(),
                    "alert_cnf": {
                        "name": "ALERT-0001: MISSING L0 DHUS PRODUCT",
                        "severity": "fatal",
                        "description": "Alert refers to the missing L0 product published in DHUS",
                        "group": "S1_PLANNING"
                    }
                }]
            }
            # Insert event
            s1boa_ingestion_functions.insert_event(completeness_event, completeness_events_per_imaging_mode, imaging_mode["short_name"], source)

        # end if

        # L1 SLC
        if imaging_mode["group"] != "EW":
            completeness_event = {
                "gauge": {
                    "insertion_type": "INSERT_and_ERASE_INTERSECTED_EVENTS_with_PRIORITY",
                    "name": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC",
                    "system": satellite
                },
                "links": [{
                    "link": imaging_event_link_ref,
                    "link_mode": "by_ref",
                    "name": "DHUS_PRODUCT_COMPLETENESS",
                    "back_ref": "PLANNED_IMAGING"
                }],
                "start": start,
                "stop": stop,
                "values": completeness_event_values,
                "alerts": [{
                    "message": "The L1 SLC product related to the datatake id {} and corresponding to the planned imaging with mode {} and timings {}_{} over orbit {} has not been published".format(datatake_id, imaging_mode["long_name"], imaging_start, imaging_stop, int(imaging_start_orbit)),
                    "generator": os.path.basename(__file__),
                    "notification_time": (imaging_start_datetime + datetime.timedelta(hours=24)).isoformat(),
                    "alert_cnf": {
                        "name": "ALERT-0002: MISSING L1 SLC DHUS PRODUCT",
                        "severity": "fatal",
                        "description": "Alert refers to the missing L1 SLC product published in DHUS",
                        "group": "S1_PLANNING"
                    }
                }]
            }
            # Insert event
            s1boa_ingestion_functions.insert_event(completeness_event, completeness_events_per_imaging_mode, imaging_mode["short_name"], source)
        # end if

        # L1 GRD
        if imaging_mode["group"] != "WV":
            completeness_event = {
                "gauge": {
                    "insertion_type": "INSERT_and_ERASE_INTERSECTED_EVENTS_with_PRIORITY",
                    "name": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD",
                    "system": satellite
                },
                "links": [{
                    "link": imaging_event_link_ref,
                    "link_mode": "by_ref",
                    "name": "DHUS_PRODUCT_COMPLETENESS",
                    "back_ref": "PLANNED_IMAGING"
                }],
                "start": start,
                "stop": stop,
                "values": completeness_event_values,
                "alerts": [{
                    "message": "The L1 GRD product related to the datatake id {} and corresponding to the planned imaging with mode {} and timings {}_{} over orbit {} has not been published".format(datatake_id, imaging_mode["long_name"], imaging_start, imaging_stop, int(imaging_start_orbit)),
                    "generator": os.path.basename(__file__),
                    "notification_time": (imaging_start_datetime + datetime.timedelta(hours=24)).isoformat(),
                    "alert_cnf": {
                        "name": "ALERT-0003: MISSING L1 GRD DHUS PRODUCT",
                        "severity": "fatal",
                        "description": "Alert refers to the missing L1 GRD product published in DHUS",
                        "group": "S1_PLANNING"
                    }
                }]
            }
            # Insert event
            s1boa_ingestion_functions.insert_event(completeness_event, completeness_events_per_imaging_mode, imaging_mode["short_name"], source)
        # end if

        # L2 OCN
        if imaging_mode["group"] != "SM":
            completeness_event = {
                "gauge": {
                    "insertion_type": "INSERT_and_ERASE_INTERSECTED_EVENTS_with_PRIORITY",
                    "name": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L2_OCN",
                    "system": satellite
                },
                "links": [{
                    "link": imaging_event_link_ref,
                    "link_mode": "by_ref",
                    "name": "DHUS_PRODUCT_COMPLETENESS",
                    "back_ref": "PLANNED_IMAGING"
                }],
                "start": start,
                "stop": stop,
                "values": completeness_event_values,
                "alerts": [{
                    "message": "The L2 OCN product related to the datatake id {} and corresponding to the planned imaging with mode {} and timings {}_{} over orbit {} has not been published".format(datatake_id, imaging_mode["long_name"], imaging_start, imaging_stop, int(imaging_start_orbit)),
                    "generator": os.path.basename(__file__),
                    "notification_time": (imaging_start_datetime + datetime.timedelta(hours=24)).isoformat(),
                    "alert_cnf": {
                        "name": "ALERT-0004: MISSING L2 OCN DHUS PRODUCT",
                        "severity": "fatal",
                        "description": "Alert refers to the missing L2 OCN product published in DHUS",
                        "group": "S1_PLANNING"
                    }
                }]
            }
            # Insert event
            s1boa_ingestion_functions.insert_event(completeness_event, completeness_events_per_imaging_mode, imaging_mode["short_name"], source)
        # end if

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
    :param tgz_filename: file name of the original TGZ file
    :type tgz_filename: str
    """
    events_per_imaging_mode = {}
    completeness_events_per_imaging_mode = {}
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
    deletion_queue = xpath_xml("/Earth_Explorer_File/Data_Block/List_of_EVRQs/EVRQ[RQ/RQ_Name='MGDHQDEL']")

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
    _generate_imaging_events(xpath_xml, source, events_per_imaging_mode, completeness_events_per_imaging_mode)

    eboa_ingestion_functions.insert_ingestion_progress(session_progress, general_source_progress, 40)

    list_of_events_with_footprints = s1boa_ingestion_functions.associate_footprints(events_per_imaging_mode, satellite)

    list_of_completeness_events_with_footprints = s1boa_ingestion_functions.associate_footprints(completeness_events_per_imaging_mode, satellite)
    
    # Build the json
    nppf_operation = {
        "mode": "insert_and_erase",
        "dim_signature": {
            "name": "NPPF_" + satellite,
            "exec": os.path.basename(__file__),
            "version": version
        },
        "source": source,
        "events": list_of_events_with_footprints
    }

    eboa_ingestion_functions.insert_ingestion_progress(session_progress, general_source_progress, 50)

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
            "generation_time": generation_time,
            "reported_generation_time": reported_generation_time,
            "validity_start": validity_start,
            "reported_validity_start": reported_validity_start,
            "validity_stop": validity_stop,
            "priority": 10
        },
        "events": list_of_completeness_events_with_footprints
    }

    data = {"operations": [nppf_operation, nppf_completeness_operation]}
    
    eboa_ingestion_functions.insert_ingestion_progress(session_progress, general_source_progress, 100)

    query.close_session()
    
    return data
