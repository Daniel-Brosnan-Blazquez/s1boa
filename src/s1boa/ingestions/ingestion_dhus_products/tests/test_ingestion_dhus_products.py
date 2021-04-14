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
        filename = "DEC_OPER_OPDHUS_S1A_AUIP_20210414T091220_V20210317T000000_20210318T000000_2131_0000.xml"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/inputs/" + filename

        exit_status = ingestion.command_process_file("s1boa.ingestions.ingestion_dhus_products.ingestion_dhus_products", file_path, "2018-01-01T00:00:00")

        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0
