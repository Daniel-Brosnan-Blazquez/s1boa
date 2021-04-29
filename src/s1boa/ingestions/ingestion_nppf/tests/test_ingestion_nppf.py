"""
Automated tests for the ingestion of the NPPF files

Written by DEIMOS Space S.L. (dibb)

module s1boa
"""
import pdb
# Import python utilities
import os
import sys
import unittest
import datetime

# Import engine of the DDBB
import eboa.engine.engine as eboa_engine
from eboa.engine.engine import Engine
from eboa.engine.query import Query

# Import ingestion
import eboa.ingestion.eboa_ingestion as ingestion

class TestEngine(unittest.TestCase):
    def setUp(self):
        # Create the engine to manage the data
        self.engine_eboa = Engine()
        self.query_eboa = Query()

        # Clear all tables before executing the test
        self.query_eboa.clear_db()

    def tearDown(self):
        # Close connections to the DDBB
        self.engine_eboa.close_session()
        self.query_eboa.close_session()

    def test_insert_nppf(self):
        filename = "S1A_OPER_MPL__NPPF__20210316T160000_20210405T180000_0001_SHORTENED.EOF"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/inputs/" + filename

        exit_status = ingestion.command_process_file("s1boa.ingestions.ingestion_nppf.ingestion_nppf", file_path, "2018-01-01T00:00:00")

        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0

        # Check number of sources inserted
        sources = self.query_eboa.get_sources()

        assert len(sources) == 2

        # Check the sources inserted
        sources = self.query_eboa.get_sources(validity_start_filters = [{"date": "2021-03-16T18:07:38.057000", "op": "=="}],
                                              validity_stop_filters = [{"date": "2021-04-05T18:00:00", "op": "=="}],
                                              reported_validity_start_filters = [{"date": "2021-03-16T16:00:00", "op": "=="}],
                                              reported_validity_stop_filters = [{"date": "2021-04-05T18:00:00", "op": "=="}],
                                              generation_time_filters = [{"date": "2021-03-16T13:05:04", "op": "=="}],
                                              reported_generation_time_filters = [{"date": "2021-03-16T13:05:04", "op": "=="}],
                                              processors = {"filter": "ingestion_nppf.py", "op": "=="},
                                              dim_signatures = {"filter": "NPPF_S1A", "op": "=="},
                                              names = {"filter": "S1A_OPER_MPL__NPPF__20210316T160000_20210405T180000_0001_SHORTENED.EOF", "op": "=="})

        assert len(sources) == 1

        sources = self.query_eboa.get_sources(validity_start_filters = [{"date": "2021-03-16T18:07:38.057000", "op": "=="}],
                                              validity_stop_filters = [{"date": "2021-04-05T18:00:00", "op": "=="}],
                                              reported_validity_start_filters = [{"date": "2021-03-16T16:00:00", "op": "=="}],
                                              reported_validity_stop_filters = [{"date": "2021-04-05T18:00:00", "op": "=="}],
                                              generation_time_filters = [{"date": "2021-03-16T13:05:04", "op": "=="}],
                                              reported_generation_time_filters = [{"date": "2021-03-16T13:05:04", "op": "=="}],
                                              processors = {"filter": "ingestion_nppf.py", "op": "=="},
                                              dim_signatures = {"filter": "COMPLETENESS_NPPF_S1A", "op": "=="},
                                              names = {"filter": "S1A_OPER_MPL__NPPF__20210316T160000_20210405T180000_0001_SHORTENED.EOF", "op": "=="})

        assert len(sources) == 1

        # Check number of events inserted
        events = self.query_eboa.get_events()

        assert len(events) == 36

        # Check number of alerts generated
        event_alerts = self.query_eboa.get_event_alerts()

        assert len(event_alerts) == 27

        # Check number of alerts generated
        filters = {}
        filters["gauge_names"] = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op": "=="}
        filters["names"] = {"filter": "ALERT-0001: MISSING L0 DHUS PRODUCT", "op": "=="}
        filters["groups"] = {"filter": "S1_PLANNING", "op": "=="}
        filters["severities"] = {"filter": "fatal", "op": "=="}
        filters["generators"] = {"filter": "ingestion_nppf.py", "op": "=="}
        alerts_planned_imaging = self.query_eboa.get_event_alerts(filters)

        assert len(alerts_planned_imaging) == 8

        assert alerts_planned_imaging[0].message == "The L0 product related to the datatake id 45B92 and corresponding to the planned imaging with mode EXTRA_WIDE_SWATH and timings 2021-03-16T18:10:59.878756_2021-03-16T18:16:12.831484 over orbit 37027 has not been published"

        # Check number of alerts generated
        filters = {}
        filters["gauge_names"] = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC", "op": "=="}
        filters["names"] = {"filter": "ALERT-0002: MISSING L1 SLC DHUS PRODUCT", "op": "=="}
        filters["groups"] = {"filter": "S1_PLANNING", "op": "=="}
        filters["severities"] = {"filter": "fatal", "op": "=="}
        filters["generators"] = {"filter": "ingestion_nppf.py", "op": "=="}
        alerts_planned_imaging = self.query_eboa.get_event_alerts(filters)

        assert len(alerts_planned_imaging) == 8

        assert alerts_planned_imaging[0].message == "The L1 SLC product related to the datatake id 45B94 and corresponding to the planned imaging with mode WAVE and timings 2021-03-16T18:19:42.153551_2021-03-16T18:35:48.853967 over orbit 37027 has not been published"
        
        # Check number of alerts generated
        filters = {}
        filters["gauge_names"] = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD", "op": "=="}
        filters["names"] = {"filter": "ALERT-0003: MISSING L1 GRD DHUS PRODUCT", "op": "=="}
        filters["groups"] = {"filter": "S1_PLANNING", "op": "=="}
        filters["severities"] = {"filter": "fatal", "op": "=="}
        filters["generators"] = {"filter": "ingestion_nppf.py", "op": "=="}
        alerts_planned_imaging = self.query_eboa.get_event_alerts(filters)

        assert len(alerts_planned_imaging) == 8

        assert alerts_planned_imaging[0].message == "The L1 GRD product related to the datatake id 45B92 and corresponding to the planned imaging with mode EXTRA_WIDE_SWATH and timings 2021-03-16T18:10:59.878756_2021-03-16T18:16:12.831484 over orbit 37027 has not been published"

        # Check number of alerts generated
        filters = {}
        filters["gauge_names"] = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L2_OCN", "op": "=="}
        filters["names"] = {"filter": "ALERT-0004: MISSING L2 OCN DHUS PRODUCT", "op": "=="}
        filters["groups"] = {"filter": "S1_PLANNING", "op": "=="}
        filters["severities"] = {"filter": "fatal", "op": "=="}
        filters["generators"] = {"filter": "ingestion_nppf.py", "op": "=="}
        alerts_planned_imaging = self.query_eboa.get_event_alerts(filters)

        assert len(alerts_planned_imaging) == 3

        assert alerts_planned_imaging[0].message == "The L2 OCN product related to the datatake id 45B92 and corresponding to the planned imaging with mode EXTRA_WIDE_SWATH and timings 2021-03-16T18:10:59.878756_2021-03-16T18:16:12.831484 over orbit 37027 has not been published"


        #####
        # Check ECC 8 - IW
        #####
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "ecc", "op": "=="},
             "type": "text",
             "value": {"filter": "8", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-17T04:10:33.066685", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-17T04:17:48.873819", "op": "=="}])

        assert len(events) == 1

        assert events[0].get_structured_values() == [
            {
                "name": "satellite",
                "type": "text",
                "value": "S1A"
            },
            {
                "name": "request_id",
                "type": "text",
                "value": "860033"
            },
            {
                "name": "request",
                "type": "text",
                "value": "MPPASTH1"
            },
            {
                "name": "imaging_operation",
                "type": "text",
                "value": "PASS_THROUGH"
            },
            {
                "name": "start_orbit",
                "type": "double",
                "value": "37033.0"
            },
            {
                "name": "start_angle",
                "type": "double",
                "value": "123.78919"
            },
            {
                "name": "ecc",
                "type": "text",
                "value": "8"
            },
            {
                "name": "imaging_mode",
                "type": "text",
                "value": "IW"
            },
            {
                "name": "imaging_mode_long_name",
                "type": "text",
                "value": "INTERFEROMETRIC_WIDE_SWATH"
            },
            {
                "name": "warmup",
                "type": "text",
                "value": "1"
            },
            {
                "name": "polarisation",
                "type": "text",
                "value": "VHV"
            },
            {
                "name": "datatake_id",
                "type": "text",
                "value": "45BC0"
            },
            {
                "name": "number_of_chops",
                "type": "double",
                "value": "78.0"
            }
        ]

        # Check completeness
        planned_imaging_event_uuid = events[0].event_uuid
        # L0
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-17T04:10:43.066685", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-17T04:17:28.873819", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0

        # L1 SLC
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-17T04:10:43.066685", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-17T04:17:28.873819", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0
        
        # L1 GRD
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-17T04:10:43.066685", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-17T04:17:28.873819", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0
        
        # L2 OCN
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L2_OCN", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-17T04:10:43.066685", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-17T04:17:28.873819", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0
        
        #####
        # Check ECC 9 - WV
        #####
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "ecc", "op": "=="},
             "type": "text",
             "value": {"filter": "9", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-16T18:19:42.153551", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-16T18:35:48.853967", "op": "=="}])

        assert len(events) == 1

        assert events[0].get_structured_values() == [
            {
                "name": "satellite",
                "type": "text",
                "value": "S1A"
            },
            {
                "name": "request_id",
                "type": "text",
                "value": "859956"
            },
            {
                "name": "request",
                "type": "text",
                "value": "MPSARDT2"
            },
            {
                "name": "imaging_operation",
                "type": "text",
                "value": "NOMINAL"
            },
            {
                "name": "start_orbit",
                "type": "double",
                "value": "37027.0"
            },
            {
                "name": "start_angle",
                "type": "double",
                "value": "129.66457"
            },
            {
                "name": "ecc",
                "type": "text",
                "value": "9"
            },
            {
                "name": "imaging_mode",
                "type": "text",
                "value": "WV"
            },
            {
                "name": "imaging_mode_long_name",
                "type": "text",
                "value": "WAVE"
            },
            {
                "name": "warmup",
                "type": "text",
                "value": "1"
            },
            {
                "name": "polarisation",
                "type": "text",
                "value": "VV"
            },
            {
                "name": "datatake_id",
                "type": "text",
                "value": "45B94"
            },
            {
                "name": "number_of_chops",
                "type": "double",
                "value": "32.0"
            },
            {
                "name": "h_packet_store_id",
                "type": "double",
                "value": "0.0"
            },
            {
                "name": "v_packet_store_id",
                "type": "double",
                "value": "20.0"
            }
        ]

        # Check completeness
        planned_imaging_event_uuid = events[0].event_uuid
        # L1 SLC
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-16T18:19:52.153551", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-16T18:35:28.853967", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0
        
        # L2 OCN
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L2_OCN", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-16T18:19:52.153551", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-16T18:35:28.853967", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0

        #####
        # Check ECC 11 - S1_WO_CAL
        #####
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "ecc", "op": "=="},
             "type": "text",
             "value": {"filter": "11", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-17T12:31:23.026189", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-17T12:31:48.030734", "op": "=="}])

        assert len(events) == 1

        assert events[0].get_structured_values() == [
            {
                "name": "satellite",
                "type": "text",
                "value": "S1A"
            },
            {
                "name": "request_id",
                "type": "text",
                "value": "860126"
            },
            {
                "name": "request",
                "type": "text",
                "value": "MPSARDT2"
            },
            {
                "name": "imaging_operation",
                "type": "text",
                "value": "NOMINAL"
            },
            {
                "name": "start_orbit",
                "type": "double",
                "value": "37038.0"
            },
            {
                "name": "start_angle",
                "type": "double",
                "value": "149.78344"
            },
            {
                "name": "ecc",
                "type": "text",
                "value": "11"
            },
            {
                "name": "imaging_mode",
                "type": "text",
                "value": "S1_WO_CAL"
            },
            {
                "name": "imaging_mode_long_name",
                "type": "text",
                "value": "STRIPMAP1_WITHOUT_CALIBRATION"
            },
            {
                "name": "warmup",
                "type": "text",
                "value": "1"
            },
            {
                "name": "polarisation",
                "type": "text",
                "value": "VHV"
            },
            {
                "name": "datatake_id",
                "type": "text",
                "value": "45BED"
            },
            {
                "name": "number_of_chops",
                "type": "double",
                "value": "4.0"
            },
            {
                "name": "h_packet_store_id",
                "type": "double",
                "value": "21.0"
            },
            {
                "name": "v_packet_store_id",
                "type": "double",
                "value": "22.0"
            }
        ]

        # Check completeness
        planned_imaging_event_uuid = events[0].event_uuid
        # L0
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-17T12:31:23.026189", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-17T12:31:23.026189", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0

        # L1 SLC
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-17T12:31:23.026189", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-17T12:31:23.026189", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0
        
        # L1 GRD
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-17T12:31:23.026189", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-17T12:31:23.026189", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0
        
        #####
        # Check ECC 12 - S2_WO_CAL
        #####
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "ecc", "op": "=="},
             "type": "text",
             "value": {"filter": "12", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-19T01:49:07.462107", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-19T01:49:27.464587", "op": "=="}])

        assert len(events) == 1

        assert events[0].get_structured_values() == [
            {
                "name": "satellite",
                "type": "text",
                "value": "S1A"
            },
            {
                "name": "request_id",
                "type": "text",
                "value": "860496"
            },
            {
                "name": "request",
                "type": "text",
                "value": "MPSARDT2"
            },
            {
                "name": "imaging_operation",
                "type": "text",
                "value": "NOMINAL"
            },
            {
                "name": "start_orbit",
                "type": "double",
                "value": "37061.0"
            },
            {
                "name": "start_angle",
                "type": "double",
                "value": "27.9858"
            },
            {
                "name": "ecc",
                "type": "text",
                "value": "12"
            },
            {
                "name": "imaging_mode",
                "type": "text",
                "value": "S2_WO_CAL"
            },
            {
                "name": "imaging_mode_long_name",
                "type": "text",
                "value": "STRIPMAP2_WITHOUT_CALIBRATION"
            },
            {
                "name": "warmup",
                "type": "text",
                "value": "1"
            },
            {
                "name": "polarisation",
                "type": "text",
                "value": "VHV"
            },
            {
                "name": "datatake_id",
                "type": "text",
                "value": "45CB0"
            },
            {
                "name": "number_of_chops",
                "type": "double",
                "value": "3.0"
            },
            {
                "name": "h_packet_store_id",
                "type": "double",
                "value": "33.0"
            },
            {
                "name": "v_packet_store_id",
                "type": "double",
                "value": "32.0"
            }
        ]

        # Check completeness
        planned_imaging_event_uuid = events[0].event_uuid
        # L0
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-19T01:49:07.462107", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-19T01:49:07.462107", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0

        # L1 SLC
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-19T01:49:07.462107", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-19T01:49:07.462107", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0
        
        # L1 GRD
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-19T01:49:07.462107", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-19T01:49:07.462107", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0

        #####
        # Check ECC 13 - S3_WO_CAL
        #####
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "ecc", "op": "=="},
             "type": "text",
             "value": {"filter": "13", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-17T10:58:50.209749", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-17T10:59:05.210061", "op": "=="}])

        assert len(events) == 1

        assert events[0].get_structured_values() == [
            {
                "name": "satellite",
                "type": "text",
                "value": "S1A"
            },
            {
                "name": "request_id",
                "type": "text",
                "value": "860108"
            },
            {
                "name": "request",
                "type": "text",
                "value": "MPSARDT2"
            },
            {
                "name": "imaging_operation",
                "type": "text",
                "value": "NOMINAL"
            },
            {
                "name": "start_orbit",
                "type": "double",
                "value": "37037.0"
            },
            {
                "name": "start_angle",
                "type": "double",
                "value": "172.39317"
            },
            {
                "name": "ecc",
                "type": "text",
                "value": "13"
            },
            {
                "name": "imaging_mode",
                "type": "text",
                "value": "S3_WO_CAL"
            },
            {
                "name": "imaging_mode_long_name",
                "type": "text",
                "value": "STRIPMAP3_WITHOUT_CALIBRATION"
            },
            {
                "name": "warmup",
                "type": "text",
                "value": "1"
            },
            {
                "name": "polarisation",
                "type": "text",
                "value": "VV"
            },
            {
                "name": "datatake_id",
                "type": "text",
                "value": "45BE3"
            },
            {
                "name": "number_of_chops",
                "type": "double",
                "value": "2.0"
            },
            {
                "name": "h_packet_store_id",
                "type": "double",
                "value": "0.0"
            },
            {
                "name": "v_packet_store_id",
                "type": "double",
                "value": "22.0"
            }
        ]

        # Check completeness
        planned_imaging_event_uuid = events[0].event_uuid
        # L0
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-17T10:58:50.209749", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-17T10:58:50.209749", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0

        # L1 SLC
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-17T10:58:50.209749", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-17T10:58:50.209749", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0
        
        # L1 GRD
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-17T10:58:50.209749", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-17T10:58:50.209749", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0
        
        #####
        # Check ECC 14 - S4_WO_CAL
        #####
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "ecc", "op": "=="},
             "type": "text",
             "value": {"filter": "14", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-16T18:36:27.354551", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-16T18:36:37.353521", "op": "=="}])

        assert len(events) == 1

        assert events[0].get_structured_values() == [
            {
                "name": "satellite",
                "type": "text",
                "value": "S1A"
            },
            {
                "name": "request_id",
                "type": "text",
                "value": "859957"
            },
            {
                "name": "request",
                "type": "text",
                "value": "MPSARDT2"
            },
            {
                "name": "imaging_operation",
                "type": "text",
                "value": "NOMINAL"
            },
            {
                "name": "start_orbit",
                "type": "double",
                "value": "37027.0"
            },
            {
                "name": "start_angle",
                "type": "double",
                "value": "190.79834"
            },
            {
                "name": "ecc",
                "type": "text",
                "value": "14"
            },
            {
                "name": "imaging_mode",
                "type": "text",
                "value": "S4_WO_CAL"
            },
            {
                "name": "imaging_mode_long_name",
                "type": "text",
                "value": "STRIPMAP4_WITHOUT_CALIBRATION"
            },
            {
                "name": "warmup",
                "type": "text",
                "value": "1"
            },
            {
                "name": "polarisation",
                "type": "text",
                "value": "VHV"
            },
            {
                "name": "datatake_id",
                "type": "text",
                "value": "45B95"
            },
            {
                "name": "number_of_chops",
                "type": "double",
                "value": "1.0"
            },
            {
                "name": "h_packet_store_id",
                "type": "double",
                "value": "27.0"
            },
            {
                "name": "v_packet_store_id",
                "type": "double",
                "value": "28.0"
            }
        ]

        # Check completeness
        planned_imaging_event_uuid = events[0].event_uuid
        # L0
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-16T18:36:27.354551", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-16T18:36:27.354551", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0

        # L1 SLC
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-16T18:36:27.354551", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-16T18:36:27.354551", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0
        
        # L1 GRD
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-16T18:36:27.354551", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-16T18:36:27.354551", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0

        #####
        # Check ECC 25 - S5N_WO_CAL
        #####
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "ecc", "op": "=="},
             "type": "text",
             "value": {"filter": "25", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-24T06:37:05.984935", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-24T06:37:25.983459", "op": "=="}])

        assert len(events) == 1

        assert events[0].get_structured_values() == [
            {
                "name": "satellite",
                "type": "text",
                "value": "S1A"
            },
            {
                "name": "request_id",
                "type": "text",
                "value": "861778"
            },
            {
                "name": "request",
                "type": "text",
                "value": "MPSARDT2"
            },
            {
                "name": "imaging_operation",
                "type": "text",
                "value": "NOMINAL"
            },
            {
                "name": "start_orbit",
                "type": "double",
                "value": "37136.0"
            },
            {
                "name": "start_angle",
                "type": "double",
                "value": "327.89146"
            },
            {
                "name": "ecc",
                "type": "text",
                "value": "25"
            },
            {
                "name": "imaging_mode",
                "type": "text",
                "value": "S5N_WO_CAL"
            },
            {
                "name": "imaging_mode_long_name",
                "type": "text",
                "value": "STRIPMAP5_NORTHERN_HEMISPHERE_WITHOUT_CALIBRATION"
            },
            {
                "name": "warmup",
                "type": "text",
                "value": "1"
            },
            {
                "name": "polarisation",
                "type": "text",
                "value": "VHV"
            },
            {
                "name": "datatake_id",
                "type": "text",
                "value": "45F52"
            },
            {
                "name": "number_of_chops",
                "type": "double",
                "value": "3.0"
            },
            {
                "name": "h_packet_store_id",
                "type": "double",
                "value": "25.0"
            },
            {
                "name": "v_packet_store_id",
                "type": "double",
                "value": "24.0"
            }
        ]

        # Check completeness
        planned_imaging_event_uuid = events[0].event_uuid
        # L0
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-24T06:37:05.984935", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-24T06:37:05.984935", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0

        # L1 SLC
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-24T06:37:05.984935", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-24T06:37:05.984935", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0
        
        # L1 GRD
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-24T06:37:05.984935", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-24T06:37:05.984935", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0
        
        #####
        # Check ECC 27 - S6_WO_CAL
        #####
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "ecc", "op": "=="},
             "type": "text",
             "value": {"filter": "27", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-19T05:52:44.433795", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-19T05:53:14.425137", "op": "=="}])

        assert len(events) == 1

        assert events[0].get_structured_values() == [
            {
                "name": "satellite",
                "type": "text",
                "value": "S1A"
            },
            {
                "name": "request_id",
                "type": "text",
                "value": "860548"
            },
            {
                "name": "request",
                "type": "text",
                "value": "MPSARDT2"
            },
            {
                "name": "imaging_operation",
                "type": "text",
                "value": "NOMINAL"
            },
            {
                "name": "start_orbit",
                "type": "double",
                "value": "37063.0"
            },
            {
                "name": "start_angle",
                "type": "double",
                "value": "196.41736"
            },
            {
                "name": "ecc",
                "type": "text",
                "value": "27"
            },
            {
                "name": "imaging_mode",
                "type": "text",
                "value": "S6_WO_CAL"
            },
            {
                "name": "imaging_mode_long_name",
                "type": "text",
                "value": "STRIPMAP6_WITHOUT_CALIBRATION"
            },
            {
                "name": "warmup",
                "type": "text",
                "value": "1"
            },
            {
                "name": "polarisation",
                "type": "text",
                "value": "VHV"
            },
            {
                "name": "datatake_id",
                "type": "text",
                "value": "45CCB"
            },
            {
                "name": "number_of_chops",
                "type": "double",
                "value": "5.0"
            },
            {
                "name": "h_packet_store_id",
                "type": "double",
                "value": "25.0"
            },
            {
                "name": "v_packet_store_id",
                "type": "double",
                "value": "24.0"
            }
        ]

        # Check completeness
        planned_imaging_event_uuid = events[0].event_uuid
        # L0
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-19T05:52:44.433795", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-19T05:52:44.433795", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0

        # L1 SLC
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-19T05:52:44.433795", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-19T05:52:44.433795", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0
        
        # L1 GRD
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-19T05:52:44.433795", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-19T05:52:44.433795", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0

        #####
        # Check ECC 32 - EW
        #####
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "ecc", "op": "=="},
             "type": "text",
             "value": {"filter": "32", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-16T18:10:59.878756", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-16T18:16:12.831484", "op": "=="}])

        assert len(events) == 1

        assert events[0].get_structured_values() == [
            {
                "name": "satellite",
                "type": "text",
                "value": "S1A"
            },
            {
                "name": "request_id",
                "type": "text",
                "value": "859954"
            },
            {
                "name": "request",
                "type": "text",
                "value": "MPSARDT2"
            },
            {
                "name": "imaging_operation",
                "type": "text",
                "value": "NOMINAL"
            },
            {
                "name": "start_orbit",
                "type": "double",
                "value": "37027.0"
            },
            {
                "name": "start_angle",
                "type": "double",
                "value": "97.86525"
            },
            {
                "name": "ecc",
                "type": "text",
                "value": "32"
            },
            {
                "name": "imaging_mode",
                "type": "text",
                "value": "EW"
            },
            {
                "name": "imaging_mode_long_name",
                "type": "text",
                "value": "EXTRA_WIDE_SWATH"
            },
            {
                "name": "warmup",
                "type": "text",
                "value": "1"
            },
            {
                "name": "polarisation",
                "type": "text",
                "value": "HHV"
            },
            {
                "name": "datatake_id",
                "type": "text",
                "value": "45B92"
            },
            {
                "name": "number_of_chops",
                "type": "double",
                "value": "102.0"
            },
            {
                "name": "h_packet_store_id",
                "type": "double",
                "value": "25.0"
            },
            {
                "name": "v_packet_store_id",
                "type": "double",
                "value": "26.0"
            }
        ]

        # Check completeness
        planned_imaging_event_uuid = events[0].event_uuid
        # L0
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-16T18:11:09.878756", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-16T18:15:52.831484", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0

        # L1 GRD
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-16T18:11:09.878756", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-16T18:15:52.831484", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0
        
        # L2 OCN
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L2_OCN", "op": "=="},
                                            value_filters = [
            {"name": {"filter": "status", "op": "=="},
             "type": "text",
             "value": {"filter": "MISSING", "op": "=="}}
        ],
                                            start_filters = [{"date": "2021-03-16T18:11:09.878756", "op": "=="}],
                                            stop_filters = [{"date": "2021-03-16T18:15:52.831484", "op": "=="}])

        assert len(events) == 1
        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0
