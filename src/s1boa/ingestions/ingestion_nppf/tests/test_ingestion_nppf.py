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

        assert len(sources) == 1

        # Check the source inserted
        sources = self.query_eboa.get_sources(validity_start_filters = [{"date": "2021-03-16T18:07:38.057000", "op": "=="}],
                                              validity_stop_filters = [{"date": "2021-04-05T18:00:00", "op": "=="}],
                                              reported_validity_start_filters = [{"date": "2021-03-16T16:00:00", "op": "=="}],
                                              reported_validity_stop_filters = [{"date": "2021-04-05T18:00:00", "op": "=="}],
                                              generation_time_filters = [{"date": "2021-03-16T13:05:04", "op": "=="}],
                                              reported_generation_time_filters = [{"date": "2021-03-16T13:05:04", "op": "=="}],
                                              processors = {"filter": "ingestion_nppf.py", "op": "=="},
                                              names = {"filter": "S1A_OPER_MPL__NPPF__20210316T160000_20210405T180000_0001_SHORTENED.EOF", "op": "=="})

        assert len(sources) == 1

        # Check number of events inserted
        events = self.query_eboa.get_events()

        assert len(events) == 9

        # Check ECC 8 - IW
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
                "value": "PASS_THOUGH"
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
