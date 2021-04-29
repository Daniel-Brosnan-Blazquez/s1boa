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
        sources = self.query_eboa.get_sources(validity_start_filters = [{"date": "2021-03-16T00:00:00", "op": "=="}],
                                              validity_stop_filters = [{"date": "2021-03-19T00:00:00", "op": "=="}],
                                              reported_validity_start_filters = [{"date": "2021-03-16T00:00:00", "op": "=="}],
                                              reported_validity_stop_filters = [{"date": "2021-03-19T00:00:00", "op": "=="}],
                                              generation_time_filters = [{"date": "2021-04-19T13:54:05", "op": "=="}],
                                              reported_generation_time_filters = [{"date": "2021-04-19T13:54:05", "op": "=="}],
                                              processors = {"filter": "ingestion_dhus_products.py", "op": "=="},
                                              dim_signatures = {"filter": "COMPLETENESS_NPPF_S1A", "op": "=="},
                                              names = {"filter": "DEC_OPER_OPDHUS_S1A_AUIP_20210419T135405_V20210316T000000_20210319T000000_2161_2150_SHORTENED.xml", "op": "=="})

        assert len(sources) == 1

        sources = self.query_eboa.get_sources(validity_start_filters = [{"date": "2021-03-16T00:00:00", "op": "=="}],
                                              validity_stop_filters = [{"date": "2021-03-19T00:00:00", "op": "=="}],
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
            }
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
        filters["groups"] = {"filter": "DHUS", "op": "=="}
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