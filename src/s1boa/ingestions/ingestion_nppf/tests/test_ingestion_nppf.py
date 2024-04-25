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
        filters["order_by"] = {"field": "notification_time", "descending": False}
        alerts_planned_imaging = self.query_eboa.get_event_alerts(**filters)

        assert len(alerts_planned_imaging) == 8

        assert alerts_planned_imaging[0].message == "The L0 product related to the datatake id 45B92 and corresponding to the planned imaging with mode EXTRA_WIDE_SWATH and timings 2021-03-16T18:10:59.878756_2021-03-16T18:16:12.831484 over orbit 37027 has not been published"

        # Check number of alerts generated
        filters = {}
        filters["gauge_names"] = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC", "op": "=="}
        filters["names"] = {"filter": "ALERT-0002: MISSING L1 SLC DHUS PRODUCT", "op": "=="}
        filters["groups"] = {"filter": "S1_PLANNING", "op": "=="}
        filters["severities"] = {"filter": "fatal", "op": "=="}
        filters["generators"] = {"filter": "ingestion_nppf.py", "op": "=="}
        filters["order_by"] = {"field": "notification_time", "descending": False}
        alerts_planned_imaging = self.query_eboa.get_event_alerts(**filters)

        assert len(alerts_planned_imaging) == 8

        assert alerts_planned_imaging[0].message == "The L1 SLC product related to the datatake id 45B94 and corresponding to the planned imaging with mode WAVE and timings 2021-03-16T18:19:42.153551_2021-03-16T18:35:48.853967 over orbit 37027 has not been published"
        
        # Check number of alerts generated
        filters = {}
        filters["gauge_names"] = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD", "op": "=="}
        filters["names"] = {"filter": "ALERT-0003: MISSING L1 GRD DHUS PRODUCT", "op": "=="}
        filters["groups"] = {"filter": "S1_PLANNING", "op": "=="}
        filters["severities"] = {"filter": "fatal", "op": "=="}
        filters["generators"] = {"filter": "ingestion_nppf.py", "op": "=="}
        filters["order_by"] = {"field": "notification_time", "descending": False}
        alerts_planned_imaging = self.query_eboa.get_event_alerts(**filters)

        assert len(alerts_planned_imaging) == 8

        assert alerts_planned_imaging[0].message == "The L1 GRD product related to the datatake id 45B92 and corresponding to the planned imaging with mode EXTRA_WIDE_SWATH and timings 2021-03-16T18:10:59.878756_2021-03-16T18:16:12.831484 over orbit 37027 has not been published"

        # Check number of alerts generated
        filters = {}
        filters["gauge_names"] = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L2_OCN", "op": "=="}
        filters["names"] = {"filter": "ALERT-0004: MISSING L2 OCN DHUS PRODUCT", "op": "=="}
        filters["groups"] = {"filter": "S1_PLANNING", "op": "=="}
        filters["severities"] = {"filter": "fatal", "op": "=="}
        filters["generators"] = {"filter": "ingestion_nppf.py", "op": "=="}
        filters["order_by"] = {"field": "notification_time", "descending": False}
        alerts_planned_imaging = self.query_eboa.get_event_alerts(**filters)

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
            },
            {"name": "footprint_details_0",
             "type": "object",
             "values": [{"name": "footprint",
                         "type": "geometry",
                         "value": "POLYGON ((34.015349 56.33485, 33.932967 56.118583, 33.851283 55.902274, 33.77019 55.685931, 33.689734 55.46955, 33.609938 55.253131, 33.530787 55.036672, 33.452154 54.820182, 33.374139 54.603654, 33.296735 54.38709, 33.219911 54.17049, 33.143578 53.953859, 33.067826 53.737192, 32.992643 53.52049, 32.917971 53.303755, 32.84378 53.08699, 32.770129 52.87019, 32.697009 52.653357, 32.624337 52.436494, 32.552136 52.2196, 32.480439 52.002674, 32.409237 51.785715, 32.338426 51.568729, 32.268078 51.351713, 32.1982 51.134665, 32.128775 50.917587, 32.059707 50.700484, 31.991085 50.48335, 31.922904 50.266186, 31.855121 50.048994, 31.787692 49.831776, 31.720682 49.61453, 31.654083 49.397254, 31.587833 49.179953, 31.521934 48.962626, 31.456428 48.745271, 31.391308 48.527888, 31.32649 48.310482, 31.262023 48.09305, 31.197923 47.875591, 31.134185 47.658105, 31.070706 47.440597, 31.007577 47.223063, 30.944793 47.005504, 30.882328 46.787919, 30.820123 46.570313, 30.758247 46.352681, 30.696696 46.135024, 30.635422 45.917345, 30.574411 45.699643, 30.51371 45.481917, 30.453313 45.264167, 30.393155 45.046395, 30.333264 44.828602, 30.273664 44.610784, 30.21435 44.392943, 30.155239 44.175083, 30.096397 43.9572, 30.03783 43.739294, 29.979521 43.521366, 29.921403 43.30342, 29.863547 43.08545, 29.80595 42.867459, 29.748576 42.649447, 29.691398 42.431416, 29.634468 42.213363, 29.577781 41.995289, 29.521285 41.777196, 29.464991 41.559083, 29.40893 41.34095, 29.353098 41.122796, 29.297427 40.904624, 29.241963 40.686432, 29.186719 40.46822, 29.131689 40.249988, 29.076795 40.031739, 29.022111 39.813471, 28.967635 39.595183, 28.913342 39.376876, 28.859194 39.158552, 28.805243 38.94021, 28.751489 38.721848, 28.69789 38.503469, 28.644442 38.285072, 28.591181 38.066657, 28.538105 37.848224, 28.485158 37.629775, 28.432369 37.411308, 28.379756 37.192823, 28.327318 36.97432, 28.274983 36.755803, 28.222813 36.537268, 28.17081 36.318715, 28.118959 36.100146, 28.067211 35.881561, 28.015623 35.66296, 27.964192 35.444342, 27.912889 35.225708, 27.861697 35.007059, 27.810655 34.788393, 27.759762 34.569711, 27.708973 34.351014, 27.658303 34.132303, 27.607775 33.913575, 27.557387 33.694831, 27.507081 33.476074, 27.4569 33.257302, 27.406854 33.038513, 27.356935 32.81971, 27.307086 32.600894, 27.257365 32.382063, 27.207771 32.163216, 27.158282 31.944356, 27.108871 31.725482, 27.059581 31.506594, 27.01041 31.287691, 26.961323 31.068776, 26.912323 30.849847, 26.863437 30.630903, 26.814662 30.411946, 26.765952 30.192977, 24.186829 30.596868, 24.229661 30.815479, 24.272485 31.03408, 24.315361 31.252671, 24.358291 31.471251, 24.401239 31.689821, 24.444199 31.908382, 24.487217 32.126931, 24.530294 32.34547, 24.573373 32.563998, 24.616488 32.782516, 24.659665 33.001023, 24.702906 33.219519, 24.746134 33.438005, 24.78942 33.656479, 24.832775 33.874942, 24.876185 34.093394, 24.919591 34.311836, 24.963068 34.530265, 25.006618 34.748683, 25.050209 34.96709, 25.093819 35.185486, 25.137507 35.40387, 25.181272 35.622242, 25.225062 35.840603, 25.268897 36.058952, 25.312815 36.277289, 25.356816 36.495614, 25.400826 36.713927, 25.444907 36.932229, 25.489076 37.150518, 25.533329 37.368794, 25.577585 37.58706, 25.621933 37.805312, 25.666376 38.023552, 25.710887 38.241779, 25.755428 38.459995, 25.800067 38.678198, 25.844807 38.896388, 25.8896 39.114565, 25.93445 39.33273, 25.979405 39.550882, 26.024467 39.76902, 26.069566 39.987146, 26.11475 40.20526, 26.160046 40.42336, 26.205458 40.641446, 26.250888 40.85952, 26.296433 41.077581, 26.342099 41.295628, 26.387868 41.513661, 26.433677 41.731682, 26.479613 41.949689, 26.525677 42.167682, 26.571828 42.385661, 26.618049 42.603628, 26.664406 42.82158, 26.7109 43.039518, 26.757464 43.257443, 26.80413 43.475355, 26.850941 43.693251, 26.897897 43.911133, 26.944907 44.129003, 26.992052 44.346857, 27.039351 44.564697, 27.086795 44.782523, 27.134296 45.000336, 27.181958 45.218133, 27.229783 45.435916, 27.277737 45.653684, 27.325782 45.871438, 27.373998 46.089177, 27.422389 46.306901, 27.470893 46.524611, 27.519524 46.742307, 27.568338 46.959987, 27.617338 47.177651, 27.666434 47.395301, 27.715695 47.612937, 27.765151 47.830556, 27.814806 48.04816, 27.864541 48.26575, 27.91448 48.483325, 27.964628 48.700883, 28.01496 48.918425, 28.06541 49.135954, 28.11608 49.353466, 28.166973 49.570961, 28.218034 49.788442, 28.269255 50.005907, 28.320711 50.223356, 28.372406 50.440788, 28.424253 50.658205, 28.476305 50.875606, 28.528608 51.09299, 28.581167 51.310357, 28.633863 51.52771, 28.68681 51.745045, 28.740026 51.962364, 28.793498 52.179665, 28.847128 52.396951, 28.901042 52.61422, 28.955243 52.831471, 29.009687 53.048705, 29.06434 53.265924, 29.119296 53.483125, 29.174562 53.700307, 29.230057 53.917473, 29.285814 54.134622, 29.341897 54.351753, 29.398314 54.568865, 29.454947 54.785961, 29.511898 55.003039, 29.569201 55.220098, 29.626855 55.437138, 29.684728 55.654163, 29.742973 55.871168, 29.801596 56.088153, 29.860563 56.30512, 29.91981 56.522071, 29.979457 56.739001, 34.015349 56.33485))"}]}]

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
            },
            {"name": "footprint_details_0",
             "type": "object",
             "values": [{"name": "footprint",
                         "type": "geometry",
                         "value": "POLYGON ((-178.493434 50.391761, -178.592984 50.101709, -178.691681 49.811595, -178.789544 49.521419, -178.886592 49.231182, -178.982842 48.940886, -179.078313 48.650531, -179.173021 48.360118, -179.266983 48.069648, -179.360221 47.779121, -179.452745 47.48854, -179.544569 47.197903, -179.635709 46.907212, -179.72618 46.616468, -179.815996 46.325671, -179.90517 46.034822, -179.993716 45.743922, -180 45.72312922157148, -180 46.64445054870983, -179.996566 46.655755, -179.907573 46.946579, -179.817932 47.237351, -179.72763 47.528071, -179.636653 47.818739, -179.544984 48.109354, -179.452615 48.399915, -179.359525 48.690421, -179.265697 48.980871, -179.171114 49.271266, -179.07576 49.561603, -178.979617 49.851882, -178.882668 50.142102, -178.784892 50.432262, -178.493434 50.391761))"}]}, {"name": "footprint_details_1", "type": "object", "values": [{"name": "footprint", "type": "geometry", "value": "POLYGON ((180 45.72312922157148, 179.918353 45.452972, 179.831025 45.161971, 179.744286 44.870922, 179.658124 44.579823, 179.572528 44.288677, 179.487486 43.997483, 179.402987 43.706242, 179.319019 43.414955, 179.235572 43.123622, 179.152636 42.832244, 179.070199 42.540822, 178.988252 42.249355, 178.906786 41.957845, 178.82579 41.666292, 178.745255 41.374696, 178.665172 41.083058, 178.585532 40.791379, 178.506326 40.499659, 178.427546 40.207898, 178.349183 39.916097, 178.271228 39.624256, 178.193675 39.332376, 178.116515 39.040458, 178.03974 38.748501, 177.963343 38.456506, 177.887317 38.164474, 177.811653 37.872404, 177.736346 37.580299, 177.661388 37.288156, 177.586772 36.995979, 177.512492 36.703765, 177.438541 36.411517, 177.364913 36.119234, 177.291601 35.826917, 177.2186 35.534567, 177.145903 35.242182, 177.073504 34.949765, 177.001397 34.657315, 176.929578 34.364833, 176.85804 34.072319, 176.786777 33.779773, 176.715785 33.487196, 176.645057 33.194589, 176.57459 32.901951, 176.504377 32.609282, 176.434413 32.316584, 176.364695 32.023857, 176.295216 31.7311, 176.225973 31.438315, 176.156959 31.145501, 176.088172 30.85266, 176.019603 30.55979, 175.951251 30.266894, 175.883111 29.97397, 175.815179 29.68102, 175.747451 29.388043, 175.679922 29.09504, 175.61259 28.802012, 175.545449 28.508958, 175.478496 28.21588, 175.411726 27.922776, 175.345136 27.629648, 175.278722 27.336497, 175.212481 27.043321, 175.146408 26.750122, 175.0805 26.4569, 175.014753 26.163655, 174.949165 25.870388, 174.88373 25.577099, 174.818447 25.283788, 174.75331 24.990455, 174.688318 24.697101, 174.623467 24.403727, 174.558753 24.110332, 174.494174 23.816917, 174.429726 23.523482, 174.365406 23.230028, 174.30121 22.936554, 174.237137 22.643061, 174.173182 22.34955, 174.109343 22.056021, 174.045617 21.762473, 173.982001 21.468908, 173.918492 21.175326, 173.855087 20.881727, 173.791784 20.588111, 173.728579 20.294479, 173.66547 20.000831, 173.602454 19.707167, 173.539528 19.413488, 173.47669 19.119794, 173.413936 18.826085, 173.351266 18.532362, 173.288674 18.238624, 173.226161 17.944873, 173.163721 17.651109, 173.101354 17.357331, 173.039056 17.063541, 172.976825 16.769738, 172.914659 16.475923, 172.852555 16.182097, 172.790511 15.888259, 172.728524 15.59441, 172.666592 15.30055, 172.604712 15.006679, 172.542882 14.712799, 172.481101 14.418908, 172.419364 14.125008, 172.357671 13.8311, 172.296019 13.537182, 172.234403 13.243256, 172.172824 12.949322, 172.111278 12.655379, 172.049764 12.36143, 171.98828 12.067473, 171.926823 11.77351, 171.865391 11.47954, 171.803982 11.185564, 171.742594 10.891583, 171.681224 10.597596, 171.61987 10.303604, 171.558531 10.009607, 171.497203 9.715605999999999, 171.435886 9.4216, 171.374576 9.127591000000001, 171.313271 8.833579, 171.25197 8.539564, 171.19067 8.245545999999999, 171.12937 7.951526, 171.068066 7.657503, 171.006757 7.36348, 170.945441 7.069455, 170.884116 6.775429, 170.822779 6.481402, 170.761428 6.187376, 170.700062 5.893349, 170.638678 5.599324, 170.577275 5.305299, 170.515849 5.011275, 170.454399 4.717253, 170.392923 4.423233, 170.331418 4.129215, 170.269884 3.8352, 170.208316 3.541188, 170.146715 3.24718, 170.085076 2.953175, 170.023398 2.659174, 169.96168 2.365178, 169.899918 2.071187, 169.838112 1.777201, 169.776257 1.483221, 169.714354 1.189247, 169.652399 0.89528, 169.590389 0.601319, 169.528325 0.307365, 169.466201 0.013419, 169.404018 -0.280519, 169.341772 -0.574449, 169.279462 -0.868371, 169.217085 -1.162283, 169.154638 -1.456186, 169.092121 -1.750078, 169.02953 -2.043961, 168.966863 -2.337833, 168.904119 -2.631694, 168.841294 -2.925544, 168.778387 -3.219382, 168.715395 -3.513207, 168.652315 -3.80702, 168.589147 -4.100821, 168.525886 -4.394607, 168.462531 -4.68838, 168.39908 -4.982139, 168.33553 -5.275883, 168.271879 -5.569612, 168.208125 -5.863326, 168.144265 -6.157024, 168.080297 -6.450705, 168.016217 -6.74437, 167.952025 -7.038019, 167.887717 -7.331649, 167.82329 -7.625262, 167.758743 -7.918857, 167.572181 -7.877861, 167.636877 -7.584325, 167.701446 -7.290769, 167.765892 -6.997196, 167.830216 -6.703604, 167.894423 -6.409995, 167.958513 -6.116369, 168.022489 -5.822727, 168.086355 -5.529067, 168.150112 -5.235393, 168.213762 -4.941702, 168.277309 -4.647997, 168.340754 -4.354276, 168.4041 -4.060542, 168.467349 -3.766794, 168.530502 -3.473032, 168.593564 -3.179257, 168.656535 -2.885469, 168.719419 -2.591669, 168.782217 -2.297858, 168.844933 -2.004035, 168.907567 -1.7102, 168.970123 -1.416356, 169.032603 -1.1225, 169.095008 -0.828635, 169.157341 -0.534761, 169.219605 -0.240877, 169.281801 0.053015, 169.343932 0.346916, 169.405999 0.640825, 169.468005 0.934741, 169.529952 1.228665, 169.591843 1.522595, 169.653679 1.816532, 169.715462 2.110475, 169.777195 2.404424, 169.838879 2.698378, 169.900518 2.992337, 169.962112 3.286301, 170.023665 3.580269, 170.085177 3.87424, 170.146652 4.168215, 170.208092 4.462194, 170.269498 4.756175, 170.330872 5.050158, 170.392217 5.344144, 170.453535 5.638131, 170.514827 5.932119, 170.576097 6.226109, 170.637345 6.520099, 170.698575 6.814089, 170.759788 7.108079, 170.820986 7.402069, 170.882172 7.696058, 170.943347 7.990046, 171.004513 8.284032, 171.065674 8.578016, 171.12683 8.871998, 171.187984 9.165977, 171.249138 9.459954, 171.310295 9.753926999999999, 171.371455 10.047897, 171.432622 10.341862, 171.493798 10.635824, 171.554984 10.92978, 171.616184 11.223732, 171.677398 11.517678, 171.738629 11.811619, 171.79988 12.105554, 171.861153 12.399482, 171.922449 12.693404, 171.983771 12.987318, 172.045122 13.281226, 172.106502 13.575125, 172.167914 13.869017, 172.22936 14.1629, 172.290844 14.456775, 172.352367 14.75064, 172.413932 15.044496, 172.475541 15.338343, 172.537196 15.632179, 172.5989 15.926006, 172.660655 16.219821, 172.722464 16.513626, 172.784329 16.807419, 172.846252 17.1012, 172.908235 17.39497, 172.970282 17.688727, 173.032395 17.982472, 173.094575 18.276204, 173.156827 18.569922, 173.219151 18.863627, 173.281551 19.157318, 173.34403 19.450995, 173.40659 19.744657, 173.469233 20.038305, 173.531962 20.331937, 173.594781 20.625554, 173.657691 20.919155, 173.720695 21.21274, 173.783796 21.506308, 173.846998 21.79986, 173.910302 22.093395, 173.973712 22.386912, 174.037231 22.680412, 174.100861 22.973893, 174.164605 23.267356, 174.228467 23.560801, 174.292449 23.854227, 174.356555 24.147633, 174.420787 24.44102, 174.48515 24.734387, 174.549645 25.027733, 174.614277 25.32106, 174.679048 25.614365, 174.743961 25.907649, 174.809021 26.200912, 174.874231 26.494153, 174.939594 26.787372, 175.005113 27.080568, 175.070792 27.373742, 175.136635 27.666893, 175.202645 27.96002, 175.268827 28.253124, 175.335183 28.546203, 175.401718 28.839259, 175.468436 29.132289, 175.53534 29.425295, 175.602434 29.718276, 175.669724 30.011231, 175.737212 30.30416, 175.804902 30.597062, 175.8728 30.889939, 175.940906 31.182788, 176.009228 31.47561, 176.07777 31.768405, 176.146537 32.061172, 176.215534 32.35391, 176.284765 32.64662, 176.354235 32.939301, 176.423949 33.231953, 176.493912 33.524576, 176.564129 33.817168, 176.634606 34.10973, 176.705347 34.402262, 176.776357 34.694762, 176.847643 34.987232, 176.91921 35.279669, 176.991063 35.572075, 177.063208 35.864448, 177.135652 36.156789, 177.208399 36.449096, 177.281457 36.74137, 177.354832 37.03361, 177.428529 37.325816, 177.502555 37.617987, 177.576917 37.910123, 177.651622 38.202223, 177.726677 38.494288, 177.802088 38.786317, 177.877862 39.078309, 177.954008 39.370264, 178.030533 39.662181, 178.107443 39.954061, 178.184748 40.245902, 178.262455 40.537705, 178.340572 40.829468, 178.419107 41.121192, 178.49807 41.412875, 178.577469 41.704519, 178.657312 41.996121, 178.737609 42.287681, 178.818369 42.5792, 178.899602 42.870676, 178.981317 43.162109, 179.063525 43.453498, 179.146236 43.744844, 179.22946 44.036145, 179.313208 44.327401, 179.397491 44.618611, 179.48232 44.909775, 179.567707 45.200892, 179.653663 45.491962, 179.740202 45.782984, 179.827335 46.073957, 179.915074 46.364881, 180 46.64445054870983, 180 45.72312922157148))"}]}]

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
            },
            {"name": "footprint_details_0",
             "type": "object",
             "values": [{"name": "footprint",
                         "type": "geometry",
                         "value": "POLYGON ((-95.087502 30.466808, -95.147306 30.21556, -95.206942 29.96429, -95.266406 29.712999, -95.325699 29.461687, -95.38482500000001 29.210355, -95.443787 28.959002, -96.261939 29.104035, -96.205044 29.355406, -96.14801 29.60676, -96.090835 29.858095, -96.033517 30.109411, -95.97605299999999 30.360709, -95.918447 30.611987, -95.087502 30.466808))"}]}]

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
            },
            {"name": "footprint_details_0",
             "type": "object",
             "values": [{"name": "footprint",
                         "type": "geometry",
                         "value": "POLYGON ((-118.620653 28.331847, -118.675863 28.573186, -118.731181 28.814509, -118.786637 29.055815, -118.842232 29.297102, -118.897969 29.538372, -118.076268 29.680425, -118.02254 29.439163, -117.96893 29.197885, -117.915437 28.956591, -117.862058 28.715282, -117.808761 28.473958, -118.620653 28.331847))"}]}]

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
            },
            {"name": "footprint_details_0",
             "type": "object",
             "values": [{"name": "footprint",
                         "type": "geometry",
                         "value": "POLYGON ((-76.395349 8.217855999999999, -76.44225400000001 7.990985, -76.48918999999999 7.764115, -76.536137 7.537244, -76.58309199999999 7.310373, -77.300253 7.457843, -77.25368 7.684563, -77.207126 7.911284, -77.160595 8.138005, -77.11411 8.364727999999999, -76.395349 8.217855999999999))"}]}]

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
            },
            {"name": "footprint_details_0",
             "type": "object",
             "values": [{"name": "footprint",
                         "type": "geometry",
                         "value": "POLYGON ((165.85393 -9.935810999999999, 165.785068 -10.237282, 165.716011 -10.538725, 164.993293 -10.374898, 165.06304 -10.073805, 165.13257 -9.772682, 165.85393 -9.935810999999999))"}]}]

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
            },
            {"name": "footprint_details_0",
             "type": "object",
             "values": [{"name": "footprint",
                         "type": "geometry",
                         "value": "POLYGON ((-178.760026 -30.810096, -178.836131 -30.572116, -178.911858 -30.334083, -178.987211 -30.095998, -179.062194 -29.857862, -179.136813 -29.619675, -178.324896 -29.422176, -178.248432 -29.659836, -178.171583 -29.89744, -178.094345 -30.13499, -178.016713 -30.372483, -177.938681 -30.609919, -178.760026 -30.810096))"}]}]

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
            },
            {"name": "footprint_details_0",
             "type": "object",
             "values": [{"name": "footprint",
                         "type": "geometry",
                         "value": "POLYGON ((-5.311756 -15.237815, -5.367625 -15.462971, -5.42367 -15.6881, -5.479882 -15.913206, -5.536259 -16.138288, -5.592803 -16.363347, -5.649527 -16.588379, -5.706428 -16.813385, -5.763501 -17.038367, -6.502723 -16.862306, -6.444809 -16.637688, -6.38708 -16.413044, -6.32954 -16.188373, -6.272196 -15.963672, -6.21503 -15.738947, -6.15804 -15.514196, -6.101229 -15.28942, -6.04461 -15.064616, -5.311756 -15.237815))"}]}]

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
            },
            {"name": "footprint_details_0",
             "type": "object",
             "values": [{"name": "footprint",
                         "type": "geometry",
                         "value": "POLYGON ((-144.383655 80.086102, -145.183974 79.913961, -145.95825 79.740047, -146.707643 79.56446, -147.432957 79.387258, -148.135174 79.208518, -148.815406 79.028339, -149.474529 78.846784, -150.113269 78.663904, -150.732459 78.479761, -151.333121 78.294442, -151.915862 78.107984, -152.481339 77.92043, -153.030248 77.73183, -153.563529 77.542264, -154.081554 77.35174499999999, -154.584917 77.160313, -155.074243 76.968014, -155.550274 76.774907, -156.013301 76.581, -156.46383 76.38632699999999, -156.902443 76.19093100000001, -157.329666 75.994851, -157.745769 75.798095, -158.151172 75.600692, -158.546423 75.402683, -158.931863 75.204088, -159.307749 75.004919, -159.67443 74.805198, -160.032431 74.604967, -160.381931 74.404231, -160.723182 74.203003, -161.056476 74.001301, -161.382321 73.79916799999999, -161.700756 73.59659499999999, -162.012033 73.393597, -162.31644 73.190195, -162.61435 72.986417, -162.905802 72.782257, -163.191014 72.57772900000001, -163.470276 72.372854, -163.74383 72.167648, -164.011733 71.96211, -164.274169 71.756249, -164.531437 71.55009, -164.78366 71.343638, -165.030917 71.136894, -165.273362 70.929867, -165.511304 70.722583, -165.744762 70.51503599999999, -165.973835 70.307232, -166.198657 70.09917799999999, -166.419542 69.890901, -166.63642 69.682388, -166.84941 69.473646, -167.058666 69.264686, -167.264399 69.055525, -167.466569 68.846154, -167.665277 68.63658, -167.860698 68.42681399999999, -168.052949 68.216866, -168.242019 68.00672900000001, -168.427996 67.79641100000001, -168.611072 67.58592400000001, -168.791283 67.375271, -168.968643 67.164449, -169.143229 66.953462, -169.315253 66.742329, -169.484671 66.531041, -169.651527 66.319602, -169.815892 66.108014, -169.977979 65.89629600000001, -170.137692 65.68443600000001, -170.295093 65.472438, -170.450279 65.26030900000001, -170.603382 65.048058, -170.75434 64.835679, -170.903205 64.62317400000001, -171.050096 64.410552, -171.195077 64.197818, -171.338111 63.984966, -171.479247 63.771999, -171.618623 63.558928, -171.756237 63.345751, -171.892082 63.132467, -172.026198 62.919077, -172.158746 62.705595, -180 63.47320869176875, -180 64.06790151542354, -179.974029 64.14261999999999, -179.897916 64.359251, -179.82105 64.575857, -179.743476 64.79244, -179.665036 65.008994, -179.585705 65.22552, -179.50558 65.442021, -179.42462 65.658495, -179.342698 65.87494, -179.25979 66.091353, -179.176039 66.30774099999999, -179.091306 66.5241, -179.005505 66.740426, -178.918606 66.95671900000001, -178.830806 67.17298700000001, -178.741857 67.38922100000001, -178.651716 67.60542100000001, -178.560389 67.821586, -178.468007 68.037722, -178.374327 68.253822, -178.279313 68.46988399999999, -178.183017 68.68591000000001, -178.085466 68.901903, -177.986458 69.117856, -177.885946 69.33376800000001, -177.784036 69.549644, -177.680642 69.76548, -177.575601 69.981272, -177.468859 70.197019, -177.360577 70.412728, -177.250545 70.62839099999999, -177.138642 70.84400599999999, -177.024804 71.05957100000001, -176.909251 71.27509499999999, -176.791637 71.490566, -176.671885 71.70598200000001, -176.549977 71.921346, -176.426022 72.13666000000001, -176.299697 72.351916, -176.170914 72.56711, -176.039707 72.782246, -175.906049 72.997325, -175.769652 73.21233599999999, -175.630409 73.427278, -175.488411 73.642157, -175.343476 73.856966, -175.195351 74.071698, -175.043907 74.286351, -174.889292 74.500933, -174.73115 74.71543200000001, -174.569265 74.92984199999999, -174.403481 75.144161, -174.233988 75.35839799999999, -174.060251 75.572536, -173.88208 75.786571, -173.69936 76.0005, -173.5121 76.21433, -173.319775 76.428042, -173.122146 76.641633, -172.919133 76.855101, -172.710534 77.06844599999999, -172.495825 77.281651, -172.2747 77.494709, -172.047107 77.70762499999999, -171.812589 77.920385, -171.570611 78.132976, -171.320772 78.345388, -171.063037 78.55762900000001, -170.796638 78.76967399999999, -170.521005 78.981511, -170.235627 79.193127, -169.940393 79.40452999999999, -169.634217 79.615686, -169.316431 79.82658000000001, -168.986448 80.03720199999999, -168.643769 80.247545, -168.287152 80.45757399999999, -167.915679 80.66726800000001, -167.528619 80.876615, -167.124954 81.085594, -166.703186 81.29416399999999, -166.262024 81.502296, -165.800474 81.709974, -165.316803 81.91715600000001, -144.383655 80.086102))"}]},
            {"name": "footprint_details_1",
             "type": "object",
             "values": [{"name": "footprint",
                         "type": "geometry",
                         "value": "POLYGON ((180 63.47320869176875, 179.802212 63.492571, 179.876143 63.709277, 179.950664 63.925962, 180 64.06790151542354, 180 63.47320869176875))"}]}]

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
