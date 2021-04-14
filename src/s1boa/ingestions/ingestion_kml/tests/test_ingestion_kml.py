"""
Automated tests for the ingestion of the KML files

Written by DEIMOS Space S.L. (dibb)

module s1boa
"""
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

class TestKml(unittest.TestCase):
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

    def test_insert_kml(self):
        filename = "Sentinel-1A_MP_20210312T160000_20210313T000000.kml"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/inputs/" + filename

        exit_status = ingestion.command_process_file("s1boa.ingestions.ingestion_kml.ingestion_kml", file_path, "2018-01-01T00:00:00")

        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0

        # Check number of sources inserted
        sources = self.query_eboa.get_sources()

        assert len(sources) == 1

        # Check number of events inserted
        events = self.query_eboa.get_events()

        assert len(events) == 27

        # Check an event crossing the antimeridian
        event_crossing_antimeridian = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_KML", "op": "=="},
                                                                 start_filters = [{"date": "2021-03-12T20:22:42", "op": "=="}],
                                                                 stop_filters = [{"date": "2021-03-12T20:25:39", "op": "=="}])

        assert len(event_crossing_antimeridian) == 1

        # Check values
        assert event_crossing_antimeridian[0].get_structured_values() == [
            {
                "name": "satellite",
                "type": "text",
                "value": "S1A"
            },
            {
                "name": "datatake_id",
                "type": "text",
                "value": "45989"
            },
            {
                "name": "mode",
                "type": "text",
                "value": "EW"
            },
            {
                "name": "swath",
                "type": "text",
                "value": "NA"
            },
            {
                "name": "polarisation",
                "type": "text",
                "value": "DH"
            },
            {
                "name": "orbit",
                "type": "double",
                "value": "36970.0"
            },
            {
                "name": "coordinates_0",
                "type": "geometry",
                "value": "POLYGON ((-178.0854 79.91791000000001, -180 79.03911960988972, -180 80.08467215204669, -178.0854 79.91791000000001, -178.0854 79.91791000000001))"
            },
            {
                "name": "coordinates_1",
                "type": "geometry",
                "value": "POLYGON ((180 79.03911960988972, 161.24506 70.43071, 150.24231 71.40302, 161.28791 81.7145, 180 80.08467215204669, 180 79.03911960988972))"
            }
        ]
