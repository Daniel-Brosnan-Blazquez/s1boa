"""
Automated tests for the ingestion of the OPDHUS_S1 files

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

class TestOpdhus(unittest.TestCase):
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

    def test_insert_opdhus(self):
        filename = "DEC_OPER_OPDHUS_S1A_AUIP_20210419T135405_V20210316T000000_20210319T000000_2161_2150_SHORTENED.xml"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/inputs/" + filename

        exit_status = ingestion.command_process_file("s1boa.ingestions.ingestion_dhus_products.ingestion_dhus_products", file_path, "2018-01-01T00:00:00")

        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0

        # Check number of sources inserted
        sources = self.query_eboa.get_sources()

        assert len(sources) == 2

        # Check the sources inserted
        sources = self.query_eboa.get_sources(validity_start_filters = [{"date": "2021-03-16T18:10:52.109000", "op": "=="}],
                                              validity_stop_filters = [{"date": "2021-03-17T12:31:42.878000", "op": "=="}],
                                              reported_validity_start_filters = [{"date": "2021-03-16T00:00:00", "op": "=="}],
                                              reported_validity_stop_filters = [{"date": "2021-03-19T00:00:00", "op": "=="}],
                                              generation_time_filters = [{"date": "2021-04-19T13:54:05", "op": "=="}],
                                              reported_generation_time_filters = [{"date": "2021-04-19T13:54:05", "op": "=="}],
                                              processors = {"filter": "ingestion_dhus_products.py", "op": "=="},
                                              dim_signatures = {"filter": "COMPLETENESS_NPPF_S1A", "op": "=="},
                                              names = {"filter": "DEC_OPER_OPDHUS_S1A_AUIP_20210419T135405_V20210316T000000_20210319T000000_2161_2150_SHORTENED.xml", "op": "=="})

        assert len(sources) == 1

        sources = self.query_eboa.get_sources(validity_start_filters = [{"date": "2021-03-16T18:10:52.109000", "op": "=="}],
                                              validity_stop_filters = [{"date": "2021-03-17T12:31:42.878000", "op": "=="}],
                                              reported_validity_start_filters = [{"date": "2021-03-16T00:00:00", "op": "=="}],
                                              reported_validity_stop_filters = [{"date": "2021-03-19T00:00:00", "op": "=="}],
                                              generation_time_filters = [{"date": "2021-04-19T13:54:05", "op": "=="}],
                                              reported_generation_time_filters = [{"date": "2021-04-19T13:54:05", "op": "=="}],
                                              processors = {"filter": "ingestion_dhus_products.py", "op": "=="},
                                              dim_signatures = {"filter": "DHUS_PRODUCTS_S1A", "op": "=="},
                                              names = {"filter": "DEC_OPER_OPDHUS_S1A_AUIP_20210419T135405_V20210316T000000_20210319T000000_2161_2150_SHORTENED.xml", "op": "=="})

        assert len(sources) == 1
        
        # Check number of events generated
        events = self.query_eboa.get_events()

        assert len(events) == 170

        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "DHUS_PRODUCT", "op": "=="})

        assert len(events) == 85

        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "DHUS_PRODUCT", "op": "=="},
                                                start_filters = [{"date": "2021-03-16T18:10:53.109000", "op": "=="}],
                                                stop_filters = [{"date": "2021-03-16T18:11:57.398000", "op": "=="}])

        assert len(events) == 1

        assert events[0].get_structured_values() == [
            {
                "name": "satellite",
                "type": "text",
                "value": "S1A"
            },
            {
                "name": "datatake_id",
                "type": "text",
                "value": "45B92"
            },
            {
                "name": "orbit",
                "type": "double",
                "value": "37027.0"
            },
            {"name": "coordinates_0",
             "type": "geometry",
             "value": "POLYGON ((-155.149475 76.901695, -171.469025 78.285431, -165.186462 81.99588799999999, -143.971863 80.133499, -155.149475 76.901695, -155.149475 76.901695))"}
        ]

        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op": "=="})

        assert len(events) == 25

        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op": "=="},
                                                start_filters = [{"date": "2021-03-16T18:13:52.303000", "op": "=="}],
                                                stop_filters = [{"date": "2021-03-16T18:15:01.503000", "op": "=="}])

        assert len(events) == 1

        assert events[0].get_structured_values() == [
            {
                "name": "satellite",
                "type": "text",
                "value": "S1A"
            },
            {
                "name": "imaging_mode",
                "type": "text",
                "value": "EW"
            },
            {
                "name": "datatake_id",
                "type": "text",
                "value": "45B92"
            },
            {
                "name": "orbit",
                "type": "double",
                "value": "37027.0"
            },
            {
                "name": "status",
                "type": "text",
                "value": "UNEXPECTED"
            },
            {"name": "footprint_details_0",
             "type": "object",
             "values": [{"name": "footprint",
                         "type": "geometry",
                         "value": "POLYGON ((-165.368318 70.850159, -165.604591 70.64258599999999, -165.836534 70.434766, -166.064188 70.22669500000001, -166.287631 70.018377, -166.506989 69.809819, -166.722558 69.601046, -166.934289 69.39204700000001, -167.142282 69.182829, -167.346668 68.973399, -167.547686 68.763777, -167.745274 68.553954, -167.93953 68.343934, -168.130604 68.133729, -168.318645 67.923349, -168.503622 67.712788, -168.685617 67.50205099999999, -168.8648 67.291151, -169.041239 67.08009199999999, -169.214929 66.868869, -178.602958 67.73497999999999, -178.510952 67.951308, -178.417663 68.16759999999999, -178.323171 68.383859, -178.22745 68.600084, -178.13033 68.81627, -178.031767 69.032417, -177.931892 69.248529, -177.830572 69.464602, -177.727672 69.680633, -177.623142 69.89662, -177.517168 70.112571, -177.409495 70.328478, -177.300031 70.544337, -177.188737 70.760149, -177.075794 70.975921, -176.960879 71.191643, -176.843922 71.407312, -176.724929 71.62293099999999, -176.60397 71.83850200000001, -165.368318 70.850159))"}]
             }
        ]


        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD", "op": "=="})

        assert len(events) == 25

        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD", "op": "=="},
                                                start_filters = [{"date": "2021-03-16T18:10:52.109000", "op": "=="}],
                                                stop_filters = [{"date": "2021-03-16T18:11:57.398000", "op": "=="}])

        assert len(events) == 1

        assert events[0].get_structured_values() == [
            {
                "name": "satellite",
                "type": "text",
                "value": "S1A"
            },
            {
                "name": "imaging_mode",
                "type": "text",
                "value": "EW"
            },
            {
                "name": "datatake_id",
                "type": "text",
                "value": "45B92"
            },
            {
                "name": "orbit",
                "type": "double",
                "value": "37027.0"
            },
            {
                "name": "status",
                "type": "text",
                "value": "UNEXPECTED"
            },
            {"name": "footprint_details_0",
             "type": "object",
             "values": [{"name": "footprint",
                         "type": "geometry",
                         "value": "POLYGON ((-142.589811 80.44699300000001, -143.446731 80.279522, -144.275305 80.110067, -145.076656 79.938729, -145.852114 79.76563400000001, -146.602569 79.59084799999999, -147.328953 79.414445, -148.032244 79.236503, -148.71369 79.05713799999999, -149.373888 78.876379, -150.013697 78.694292, -150.634017 78.51094999999999, -151.235809 78.32643, -151.819595 78.140761, -152.386103 77.95399399999999, -152.936167 77.76619599999999, -153.470468 77.577416, -153.989485 77.38768, -154.493824 77.197029, -171.022689 78.598207, -170.755707 78.809532, -170.479461 79.02064799999999, -170.193415 79.231542, -169.897268 79.442213, -169.590378 79.652646, -169.271839 79.86281700000001, -168.940927 80.072709, -168.597291 80.28232199999999, -168.239794 80.491625, -167.867391 80.700593, -167.47909 80.90920199999999, -167.074388 81.117453, -166.651526 81.325294, -166.209204 81.532695, -165.746169 81.739631, -165.261199 81.94607999999999, -164.752116 82.151983, -164.217044 82.357294, -142.589811 80.44699300000001))"}]
                }
        ]


        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC", "op": "=="})

        assert len(events) == 21
        
        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC", "op": "=="},
                                                start_filters = [{"date": "2021-03-17T04:15:53.687000", "op": "=="}],
                                                stop_filters = [{"date": "2021-03-17T04:16:21.784000", "op": "=="}])

        assert len(events) == 1

        assert events[0].get_structured_values() == [
            {
                "name": "satellite",
                "type": "text",
                "value": "S1A"
            },
            {
                "name": "imaging_mode",
                "type": "text",
                "value": "IW"
            },
            {
                "name": "datatake_id",
                "type": "text",
                "value": "45BC0"
            },
            {
                "name": "orbit",
                "type": "double",
                "value": "37033.0"
            },
            {
                "name": "status",
                "type": "text",
                "value": "UNEXPECTED"
            },
            {"name": "footprint_details_0",
             "type": "object",
             "values": [{"name": "footprint",
                         "type": "geometry",
                         "value": "POLYGON ((28.362926 37.131502, 28.305011 36.890013, 28.247291 36.648502, 28.189741 36.406972, 28.132349 36.165422, 28.075143 35.923851, 28.018118 35.68226, 27.961273 35.440649, 25.221232 35.836994, 25.269679 36.078307, 25.318209 36.319606, 25.366823 36.560889, 25.415526 36.802158, 25.464277 37.043413, 25.513093 37.284653, 25.562001 37.525878, 28.362926 37.131502))"}]
             }
        ]
        
        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L2_OCN", "op": "=="})

        assert len(events) == 14

        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L2_OCN", "op": "=="},
                                                start_filters = [{"date": "2021-03-17T04:15:54.500000", "op": "=="}],
                                                stop_filters = [{"date": "2021-03-17T04:16:20.500000", "op": "=="}])

        assert len(events) == 1

        assert events[0].get_structured_values() == [
            {
                "name": "satellite",
                "type": "text",
                "value": "S1A"
            },
            {
                "name": "imaging_mode",
                "type": "text",
                "value": "IW"
            },
            {
                "name": "datatake_id",
                "type": "text",
                "value": "45BC0"
            },
            {
                "name": "orbit",
                "type": "double",
                "value": "37033.0"
            },
            {
                "name": "status",
                "type": "text",
                "value": "UNEXPECTED"
            },
            {"name": "footprint_details_0",
             "type": "object",
             "values": [{"name": "footprint",
                         "type": "geometry",
                         "value": "POLYGON ((28.351183 37.082591, 28.297612 36.859122, 28.244215 36.635634, 28.190966 36.41213, 28.137845 36.188609, 28.084891 35.96507, 28.032101 35.741514, 27.979451 35.51794, 25.236738 35.914189, 25.281591 36.137488, 25.326497 36.360775, 25.371488 36.584049, 25.416563 36.80731, 25.461672 37.030559, 25.506836 37.253796, 25.552091 37.477019, 28.351183 37.082591))"}]
             }
        ]


        # Check number of annotations inserted
        annotations = self.query_eboa.get_annotations()

        assert len(annotations) == 170

        # Check number of annotations generated
        annotations = self.query_eboa.get_annotations(annotation_cnf_names = {"filter": "DHUS_METADATA_INFORMATION", "op": "=="})

        assert len(annotations) == 85

        # Check number of annotations generated
        annotations = self.query_eboa.get_annotations(annotation_cnf_names = {"filter": "DHUS_METADATA_INFORMATION", "op": "=="},
                                                    explicit_refs = {"filter": "S1A_EW_GRDM_1SDH_20210316T181053_20210316T181157_037027_045B92_2677", "op": "=="})

        assert len(annotations) == 1

        assert annotations[0].get_structured_values() == [
            {
                "name": "dhus_ingestion_time",
                "type": "timestamp",
                "value": "2021-03-16T20:39:12.848000"
            },
            {
                "name": "dhus_identifier",
                "type": "text",
                "value": "5d9c9636-460f-4716-9827-6ccf3d88046d"
            },
            {
                "name": "dhus_metadata_url",
                "type": "text",
                "value": "https://scihub.copernicus.eu/dhus/odata/v1/Products('5d9c9636-460f-4716-9827-6ccf3d88046d')"
            },
            {
                "name": "dhus_product_url",
                "type": "text",
                "value": "https://scihub.copernicus.eu/dhus/odata/v1/Products('5d9c9636-460f-4716-9827-6ccf3d88046d')/$value"
            },
            {
                "name": "datatake_id",
                "type": "text",
                "value": "45B92"
            },
            {
                "name": "orbit",
                "type": "double",
                "value": "37027.0"
            },
            {
                "name": "size",
                "type": "double",
                "value": "228598125.0"
            },
            {
                "name": "coordinates_0",
                "type": "geometry",
                "value": "POLYGON ((-155.149475 76.901695, -171.469025 78.285431, -165.186462 81.99588799999999, -143.971863 80.133499, -155.149475 76.901695, -155.149475 76.901695))"
            }           
        ]

        # Check number of annotations generated
        annotations = self.query_eboa.get_annotations(annotation_cnf_names = {"filter": "DHUS_PUBLICATION_TIME", "op": "=="})

        assert len(annotations) == 85

        # Check number of annotations generated
        annotations = self.query_eboa.get_annotations(annotation_cnf_names = {"filter": "DHUS_PUBLICATION_TIME", "op": "=="},
                                                    explicit_refs = {"filter": "S1A_EW_GRDM_1SDH_20210316T181053_20210316T181157_037027_045B92_2677", "op": "=="})

        assert len(annotations) == 1

        assert annotations[0].get_structured_values() == [
            {
                "name": "dhus_publication_time",
                "type": "timestamp",
                "value": "2021-03-16T21:24:18.270000"
            }      
        ]
        
        # Check number of explicit refs inserted
        explicit_refs = self.query_eboa.get_explicit_refs()

        assert len(explicit_refs) == 85
    
        # Check number of alerts generated
        filters = {}
        filters["gauge_names"] = {"filter": "DHUS_PRODUCT", "op": "=="}
        filters["names"] = {"filter": "ALERT-0200: NO PLANNED IMAGING FOR A DHUS PRODUCT", "op": "=="}
        filters["groups"] = {"filter": "S1_DHUS", "op": "=="}
        filters["severities"] = {"filter": "fatal", "op": "=="}
        filters["generators"] = {"filter": "ingestion_dhus_products.py", "op": "=="}
        filters["order_by"] = {"field": "notification_time", "descending": False}
        alerts_planned_imaging = self.query_eboa.get_event_alerts(filters)

        assert len(alerts_planned_imaging) == 85

        assert alerts_planned_imaging[0].message == "The DHUS product S1A_EW_GRDM_1SDH_20210316T181053_20210316T181157_037027_045B92_2677 could not be linked to any planned imaging"

    def test_insert_opdhus_with_plan(self):

        filename = "S1A_OPER_MPL__NPPF__20210316T160000_20210405T180000_0001_SHORTENED.EOF"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/inputs/" + filename

        exit_status = ingestion.command_process_file("s1boa.ingestions.ingestion_nppf.ingestion_nppf", file_path, "2018-01-01T00:00:00")

        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0

        filename = "DEC_OPER_OPDHUS_S1A_AUIP_20210419T135405_V20210316T000000_20210319T000000_2161_2150_SHORTENED.xml"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/inputs/" + filename

        exit_status = ingestion.command_process_file("s1boa.ingestions.ingestion_dhus_products.ingestion_dhus_products", file_path, "2018-01-01T00:00:00")

        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0

        # Check number of sources inserted
        sources = self.query_eboa.get_sources()

        assert len(sources) == 4

        # Check number of events generated
        events = self.query_eboa.get_events()

        assert len(events) == 178

        # Check number of events generated
        planned_imaging_events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING", "op": "=="},
                                                start_filters = [{"date": "2021-03-17T04:10:33.066685", "op": "=="}],
                                                stop_filters = [{"date": "2021-03-17T04:17:48.873819", "op": "=="}])

        assert len(planned_imaging_events) == 1

        planned_imaging_event_uuid = planned_imaging_events[0].event_uuid
        
        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "DHUS_PRODUCT", "op": "=="})

        assert len(events) == 85

        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "DHUS_PRODUCT", "op": "=="},
                                                start_filters = [{"date": "2021-03-17T04:10:26.450000", "op": "=="}],
                                                stop_filters = [{"date": "2021-03-17T04:10:56.292000", "op": "=="}])

        assert len(events) == 1

        dhus_product_event_uuid = events[0].event_uuid

        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0

        assert len([link for link in planned_imaging_events[0].eventLinks if link.event_uuid_link == dhus_product_event_uuid]) > 0

        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op": "=="})

        assert len(events) == 25

        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op": "=="},
                                                start_filters = [{"date": "2021-03-17T04:10:25.800000", "op": "=="}],
                                                stop_filters = [{"date": "2021-03-17T04:10:59.200000", "op": "=="}])

        assert len(events) == 1

        planned_imaging_completeness_l0_event_uuid = events[0].event_uuid

        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0

        assert len([link for link in planned_imaging_events[0].eventLinks if link.event_uuid_link == planned_imaging_completeness_l0_event_uuid]) > 0

        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD", "op": "=="})

        assert len(events) == 25

        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD", "op": "=="},
                                                start_filters = [{"date": "2021-03-17T04:10:25.461000", "op": "=="}],
                                                stop_filters = [{"date": "2021-03-17T04:10:55.500000", "op": "=="}])

        assert len(events) == 1

        planned_imaging_completeness_l1_grd_event_uuid = events[0].event_uuid

        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0

        assert len([link for link in planned_imaging_events[0].eventLinks if link.event_uuid_link == planned_imaging_completeness_l1_grd_event_uuid]) > 0

        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC", "op": "=="})

        assert len(events) == 21
        
        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC", "op": "=="},
                                                start_filters = [{"date": "2021-03-17T04:10:25.450000", "op": "=="}],
                                                stop_filters = [{"date": "2021-03-17T04:10:56.292000", "op": "=="}])

        assert len(events) == 1
        
        planned_imaging_completeness_l1_slc_event_uuid = events[0].event_uuid

        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0

        assert len([link for link in planned_imaging_events[0].eventLinks if link.event_uuid_link == planned_imaging_completeness_l1_slc_event_uuid]) > 0

        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L2_OCN", "op": "=="})

        assert len(events) == 16

        # Check number of events generated
        events = self.query_eboa.get_events(gauge_names = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L2_OCN", "op": "=="},
                                                start_filters = [{"date": "2021-03-17T04:10:43.066685", "op": "=="}],
                                                stop_filters = [{"date": "2021-03-17T04:13:49.500000", "op": "=="}])

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
            {
                "name": "status",
                "type": "text",
                "value": "MISSING"
            },
            {"name": "footprint_details_0",
             "type": "object",
             "values": [{"name": "footprint",
                         "type": "geometry",
                         "value": "POLYGON ((33.787954 55.737887, 33.706848 55.520092, 33.626409 55.302258, 33.546555 55.084388, 33.467295 54.866482, 33.388668 54.648539, 33.310661 54.430557, 33.233175 54.212544, 33.156258 53.994495, 33.079929 53.77641, 33.004177 53.558289, 32.928887 53.340139, 32.854143 53.121954, 32.779947 52.903734, 32.70628 52.68548, 32.633037 52.467199, 32.560312 52.248884, 32.488098 52.030536, 32.41636 51.812156, 32.34503 51.593749, 32.274184 51.37531, 32.203814 51.156839, 32.133871 50.938339, 32.064322 50.719811, 31.995226 50.501253, 31.926575 50.282664, 31.858304 50.064049, 31.790417 49.845406, 31.722952 49.626733, 31.655903 49.408032, 31.589194 49.189305, 31.522856 48.970551, 31.456914 48.751769, 31.391362 48.532959, 31.326109 48.314126, 31.26122 48.095265, 31.196701 47.876378, 31.132547 47.657463, 31.068657 47.438527, 31.005121 47.219564, 30.941934 47.000575, 30.879074 46.78156, 30.816472 46.562524, 30.754204 46.343462, 30.692262 46.124375, 30.630613 45.905264, 30.569218 45.686131, 30.508136 45.466973, 30.447362 45.247791, 30.386847 45.028587, 30.326584 44.809361, 30.266614 44.590111, 27.128041 44.979665, 27.176007 45.198894, 27.224136 45.418108, 27.272374 45.637308, 27.320726 45.856493, 27.369251 46.075663, 27.417951 46.294817, 27.466751 46.513958, 27.515694 46.733084, 27.56482 46.952193, 27.614134 47.171287, 27.663539 47.390368, 27.713118 47.609433, 27.762893 47.828482, 27.812868 48.047514, 27.862926 48.266534, 27.913189 48.485537, 27.963662 48.704523, 28.01433 48.923494, 28.06511 49.142451, 28.11611 49.361391, 28.167335 49.580314, 28.218749 49.799222, 28.270308 50.018115, 28.322103 50.236991, 28.374138 50.45585, 28.426357 50.674693, 28.478755 50.893521, 28.531406 51.112331, 28.584315 51.331125, 28.637403 51.549903, 28.690706 51.768664, 28.744281 51.987408, 28.798132 52.206134, 28.852158 52.424846, 28.906439 52.64354, 28.961011 52.862215, 29.015879 53.080873, 29.070918 53.299516, 29.126255 53.518141, 29.181905 53.736748, 29.23786 53.955336, 29.294009 54.173909, 29.350487 54.392463, 29.407302 54.610998, 29.464424 54.829515, 29.521783 55.048016, 29.579498 55.266498, 29.637575 55.48496, 29.695961 55.703404, 29.754633 55.921831, 29.813688 56.140239, 33.787954 55.737887))"}]
             }
        ]

        planned_imaging_completeness_l2_ocn_event_uuid = events[0].event_uuid

        assert len([link for link in events[0].eventLinks if link.event_uuid_link == planned_imaging_event_uuid]) > 0

        assert len([link for link in planned_imaging_events[0].eventLinks if link.event_uuid_link == planned_imaging_completeness_l2_ocn_event_uuid]) > 0
        
        # Check number of alerts generated
        event_alerts = self.query_eboa.get_event_alerts()

        assert len(event_alerts) == 2

        # Check number of alerts generated
        filters = {}
        filters["gauge_names"] = {"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L2_OCN", "op": "=="}
        filters["notification_time_filters"] = [{"date": "2021-03-18T04:10:33.066685", "op": "=="}]
        filters["names"] = {"filter": "ALERT-0004: MISSING L2 OCN DHUS PRODUCT", "op": "=="}
        filters["groups"] = {"filter": "S1_PLANNING", "op": "=="}
        filters["severities"] = {"filter": "fatal", "op": "=="}
        filters["generators"] = {"filter": "ingestion_nppf.py", "op": "=="}
        alerts_planned_imaging = self.query_eboa.get_event_alerts(filters)

        assert len(alerts_planned_imaging) == 2

        assert alerts_planned_imaging[0].message == "The L2 OCN product related to the datatake id 45BC0 and corresponding to the planned imaging with mode INTERFEROMETRIC_WIDE_SWATH and timings 2021-03-17T04:10:33.066685_2021-03-17T04:17:48.873819 over orbit 37033 has not been published"

        assert alerts_planned_imaging[1].message == "The L2 OCN product related to the datatake id 45BC0 and corresponding to the planned imaging with mode INTERFEROMETRIC_WIDE_SWATH and timings 2021-03-17T04:10:33.066685_2021-03-17T04:17:48.873819 over orbit 37033 has not been published"
