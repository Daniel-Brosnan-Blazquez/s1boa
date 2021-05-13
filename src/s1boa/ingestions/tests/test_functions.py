"""
Automated tests for the functions of the ingestion of the S1BOA submodule

Written by DEIMOS Space S.L. (dibb)

module s1boa
"""
# Import python utilities
import os
import sys
import unittest
import datetime
from dateutil import parser
import traceback
import pdb
import re

# Import engine of the DDBB
import eboa.engine.engine as eboa_engine
from eboa.engine.engine import Engine
from eboa.engine.query import Query

# Import ingestion
import eboa.ingestion.eboa_ingestion as ingestion

# Import functions
import s1boa.ingestions.functions as s1boa_functions

# Import errors
from s1boa.ingestions.errors import WrongDate, WrongSatellite

# Import logging
from eboa.logging import Log

class TestS2boaFunctions(unittest.TestCase):
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

    def test_build_orbpre_from_reference_wrong_start(self):

        test_success = False
        try:
            s1boa_functions.build_orbpre_file_from_reference("not_a_correct_date", "", "")
        except WrongDate:
            traceback.print_exc(file=sys.stdout)
            test_success = True
        # end try

        assert test_success

    def test_build_orbpre_from_reference_wrong_stop(self):

        test_success = False
        try:
            s1boa_functions.build_orbpre_file_from_reference("2020-01-01T00:00:00", "not_a_correct_date", "")
        except WrongDate:
            traceback.print_exc(file=sys.stdout)
            test_success = True
        # end try

        assert test_success

    def test_build_orbpre_from_reference_wrong_satellite(self):

        test_success = False
        try:
            s1boa_functions.build_orbpre_file_from_reference("2020-01-01T00:00:00", "2020-01-01T00:00:00", "not_a_registered_satellite")
        except WrongSatellite:
            traceback.print_exc(file=sys.stdout)
            test_success = True
        # end try

        assert test_success

    def test_build_orbpre_from_reference_s1a(self):

        # Minimum window is [date - 200 minutes, date + 200 minutes]
        orbpre_file_path = s1boa_functions.build_orbpre_file_from_reference("2020-01-01T00:00:00", "2020-01-01T00:00:00", "S1A")

        f = open(orbpre_file_path,"r")
        orbpre_file_content = f.read()
        orbpre_file_content = re.sub(".*Creation_Date.*", "", orbpre_file_content)
        orbpre_file_content = re.sub(".*File_Name.*", "", orbpre_file_content)
        assert orbpre_file_content == '''<?xml version="1.0"?>
<Earth_Explorer_File xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://eop-cfi.esa.int/CFI http://eop-cfi.esa.int/CFI/EE_CFI_SCHEMAS/EO_OPER_MPL_ORBPRE_0203.XSD" schemaVersion="2.3" xmlns="http://eop-cfi.esa.int/CFI">
  <Earth_Explorer_Header>
    <Fixed_Header>

      <File_Description>FOS Predicted Orbit File</File_Description>
      <Notes/>
      <Mission>Sentinel1A</Mission>
      <File_Class/>
      <File_Type>MPL_ORBPRE</File_Type>
      <Validity_Period>
        <Validity_Start>UTC=2019-12-31T19:47:25</Validity_Start>
        <Validity_Stop>UTC=2020-01-01T02:22:23</Validity_Stop>
      </Validity_Period>
      <File_Version>0001</File_Version>
      <Source>
        <System/>
        <Creator>EO_ORBIT:xo_gen_pof</Creator>
        <Creator_Version>4.17</Creator_Version>

      </Source>
    </Fixed_Header>
    <Variable_Header>
      <Ref_Frame>EARTH_FIXED</Ref_Frame>
      <Time_Reference>TAI</Time_Reference>
    </Variable_Header>
  </Earth_Explorer_Header>
  <Data_Block type="xml">
    <List_of_OSVs count="5">
      <OSV>
        <TAI>TAI=2019-12-31T19:48:01.518125</TAI>
        <UTC>UTC=2019-12-31T19:47:24.518125</UTC>
        <UT1>UT1=2019-12-31T19:47:24.518125</UT1>
        <Absolute_Orbit>+30597</Absolute_Orbit>
        <X unit="m">+6327996.651</X>
        <Y unit="m">-3168390.533</Y>
        <Z unit="m">+0000000.000</Z>
        <VX unit="m/s">-0717.044753</VX>
        <VY unit="m/s">-1412.302336</VY>
        <VZ unit="m/s">+7430.334805</VZ>
        <Quality>0000000000000</Quality>
      </OSV>
      <OSV>
        <TAI>TAI=2019-12-31T21:26:46.089553</TAI>
        <UTC>UTC=2019-12-31T21:26:09.089553</UTC>
        <UT1>UT1=2019-12-31T21:26:09.089553</UT1>
        <Absolute_Orbit>+30598</Absolute_Orbit>
        <X unit="m">+4426447.494</X>
        <Y unit="m">-5521666.666</Y>
        <Z unit="m">+0000000.000</Z>
        <VX unit="m/s">-1241.350420</VX>
        <VY unit="m/s">-0983.768369</VY>
        <VZ unit="m/s">+7430.334805</VZ>
        <Quality>0000000000000</Quality>
      </OSV>
      <OSV>
        <TAI>TAI=2019-12-31T23:05:30.660982</TAI>
        <UTC>UTC=2019-12-31T23:04:53.660982</UTC>
        <UT1>UT1=2019-12-31T23:04:53.660982</UT1>
        <Absolute_Orbit>+30599</Absolute_Orbit>
        <X unit="m">+1715852.956</X>
        <Y unit="m">-6865718.376</Y>
        <Z unit="m">+0000000.000</Z>
        <VX unit="m/s">-1538.767859</VX>
        <VY unit="m/s">-0375.425817</VY>
        <VZ unit="m/s">+7430.334805</VZ>
        <Quality>0000000000000</Quality>
      </OSV>
      <OSV>
        <TAI>TAI=2020-01-01T00:44:15.232410</TAI>
        <UTC>UTC=2020-01-01T00:43:38.232410</UTC>
        <UT1>UT1=2020-01-01T00:43:38.232410</UT1>
        <Absolute_Orbit>+30600</Absolute_Orbit>
        <X unit="m">-1308357.165</X>
        <Y unit="m">-6954886.176</Y>
        <Z unit="m">+0000000.000</Z>
        <VX unit="m/s">-1554.936502</VX>
        <VY unit="m/s">+0301.535310</VY>
        <VZ unit="m/s">+7430.334805</VZ>
        <Quality>0000000000000</Quality>
      </OSV>
      <OSV>
        <TAI>TAI=2020-01-01T02:22:59.803839</TAI>
        <UTC>UTC=2020-01-01T02:22:22.803839</UTC>
        <UT1>UT1=2020-01-01T02:22:22.803839</UT1>
        <Absolute_Orbit>+30601</Absolute_Orbit>
        <X unit="m">-4093431.880</X>
        <Y unit="m">-5772872.390</Y>
        <Z unit="m">+0000000.000</Z>
        <VX unit="m/s">-1286.901119</VX>
        <VY unit="m/s">+0923.383223</VY>
        <VZ unit="m/s">+7430.334805</VZ>
        <Quality>0000000000000</Quality>
      </OSV>
    </List_of_OSVs>
  </Data_Block>
</Earth_Explorer_File>
'''

    def test_build_orbpre_from_reference_s1b(self):

        # Minimum window is [date - 200 minutes, date + 200 minutes]
        orbpre_file_path = s1boa_functions.build_orbpre_file_from_reference("2020-01-01T00:00:00", "2020-01-01T00:00:00", "S1B")

        f = open(orbpre_file_path,"r")
        orbpre_file_content = f.read()
        orbpre_file_content = re.sub(".*Creation_Date.*", "", orbpre_file_content)
        orbpre_file_content = re.sub(".*File_Name.*", "", orbpre_file_content)
        assert orbpre_file_content == '''<?xml version="1.0"?>
<Earth_Explorer_File xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://eop-cfi.esa.int/CFI http://eop-cfi.esa.int/CFI/EE_CFI_SCHEMAS/EO_OPER_MPL_ORBPRE_0203.XSD" schemaVersion="2.3" xmlns="http://eop-cfi.esa.int/CFI">
  <Earth_Explorer_Header>
    <Fixed_Header>

      <File_Description>FOS Predicted Orbit File</File_Description>
      <Notes/>
      <Mission>Sentinel1B</Mission>
      <File_Class/>
      <File_Type>MPL_ORBPRE</File_Type>
      <Validity_Period>
        <Validity_Start>UTC=2019-12-31T20:36:05</Validity_Start>
        <Validity_Stop>UTC=2020-01-01T03:11:03</Validity_Stop>
      </Validity_Period>
      <File_Version>0001</File_Version>
      <Source>
        <System/>
        <Creator>EO_ORBIT:xo_gen_pof</Creator>
        <Creator_Version>4.17</Creator_Version>

      </Source>
    </Fixed_Header>
    <Variable_Header>
      <Ref_Frame>EARTH_FIXED</Ref_Frame>
      <Time_Reference>TAI</Time_Reference>
    </Variable_Header>
  </Earth_Explorer_Header>
  <Data_Block type="xml">
    <List_of_OSVs count="5">
      <OSV>
        <TAI>TAI=2019-12-31T20:36:41.803827</TAI>
        <UTC>UTC=2019-12-31T20:36:04.803827</UTC>
        <UT1>UT1=2019-12-31T20:36:04.803827</UT1>
        <Absolute_Orbit>+19614</Absolute_Orbit>
        <X unit="m">+5504452.231</X>
        <Y unit="m">-4447836.084</Y>
        <Z unit="m">+0000000.000</Z>
        <VX unit="m/s">-1002.366327</VX>
        <VY unit="m/s">-1226.382002</VY>
        <VZ unit="m/s">+7430.334805</VZ>
        <Quality>0000000000000</Quality>
      </OSV>
      <OSV>
        <TAI>TAI=2019-12-31T22:15:26.375256</TAI>
        <UTC>UTC=2019-12-31T22:14:49.375256</UTC>
        <UT1>UT1=2019-12-31T22:14:49.375256</UT1>
        <Absolute_Orbit>+19615</Absolute_Orbit>
        <X unit="m">+3143816.543</X>
        <Y unit="m">-6340241.142</Y>
        <Z unit="m">+0000000.000</Z>
        <VX unit="m/s">-1422.949253</VX>
        <VY unit="m/s">-0695.677003</VY>
        <VZ unit="m/s">+7430.334805</VZ>
        <Quality>0000000000000</Quality>
      </OSV>
      <OSV>
        <TAI>TAI=2019-12-31T23:54:10.946684</TAI>
        <UTC>UTC=2019-12-31T23:53:33.946684</UTC>
        <UT1>UT1=2019-12-31T23:53:33.946684</UT1>
        <Absolute_Orbit>+19616</Absolute_Orbit>
        <X unit="m">+0208568.763</X>
        <Y unit="m">-7073806.561</Y>
        <Z unit="m">+0000000.000</Z>
        <VX unit="m/s">-1583.452165</VX>
        <VY unit="m/s">-0037.819413</VY>
        <VZ unit="m/s">+7430.334805</VZ>
        <Quality>0000000000000</Quality>
      </OSV>
      <OSV>
        <TAI>TAI=2020-01-01T01:32:55.518113</TAI>
        <UTC>UTC=2020-01-01T01:32:18.518113</UTC>
        <UT1>UT1=2020-01-01T01:32:18.518113</UT1>
        <Absolute_Orbit>+19617</Absolute_Orbit>
        <X unit="m">-2764800.240</X>
        <Y unit="m">-6514454.683</Y>
        <Z unit="m">+0000000.000</Z>
        <VX unit="m/s">-1454.539093</VX>
        <VY unit="m/s">+0626.950632</VY>
        <VZ unit="m/s">+7430.334805</VZ>
        <Quality>0000000000000</Quality>
      </OSV>
      <OSV>
        <TAI>TAI=2020-01-01T03:11:40.089541</TAI>
        <UTC>UTC=2020-01-01T03:11:03.089541</UTC>
        <UT1>UT1=2020-01-01T03:11:03.089541</UT1>
        <Absolute_Orbit>+19618</Absolute_Orbit>
        <X unit="m">-5232831.980</X>
        <Y unit="m">-4764421.230</Y>
        <Z unit="m">+0000000.000</Z>
        <VX unit="m/s">-1059.772164</VX>
        <VY unit="m/s">+1177.129571</VY>
        <VZ unit="m/s">+7430.334805</VZ>
        <Quality>0000000000000</Quality>
      </OSV>
    </List_of_OSVs>
  </Data_Block>
</Earth_Explorer_File>
'''

    def test_associate_footprints_iw_s1a(self):

        logging_module = Log(name = __name__)
        previous_logging_level = None
        if "EBOA_LOG_LEVEL" in os.environ:
            previous_logging_level = os.environ["EBOA_LOG_LEVEL"]
        # end if

        os.environ["EBOA_LOG_LEVEL"] = "DEBUG"

        logging_module.define_logging_configuration()
        
        # Minimum window is [date - 200 minutes, date + 200 minutes]
        events_per_imaging_mode = {
            "IW": [{"start": "2021-03-17T04:12:10.501000",
                    "stop": "2021-03-17T04:12:35.499000",
                    }]
        }

        events_with_footprint = s1boa_functions.associate_footprints(events_per_imaging_mode, "S1A")

        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {"name": "dim_signature",
                              "exec": "exec",
                              "version": "1.0"},
            "source": {"name": "source.xml",
                       "reception_time": "2018-06-06T13:33:29",
                       "generation_time": "2018-07-05T02:07:03",
                       "validity_start": "2018-06-05T02:07:03",
                       "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T02:07:03",
                "stop": "2018-06-05T08:07:36",
                "values": events_with_footprint[0]["values"]
            }]
        }]
        }
        exit_status = self.engine_eboa.treat_data(data)

        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0


        assert len(events_with_footprint) == 1
        
        assert events_with_footprint[0]["values"] == [
            {"name": "footprint_details",
             "type": "object",
             "values": [{"name": "footprint",
                         "type": "geometry",
                         "value": "32.000866 50.519131 31.922603 50.270001 31.844881 50.020833 31.767632 49.771631 31.690902 49.522393 31.614684 49.273118 31.538968 49.023807 28.128559 49.414686 28.18698 49.664194 28.245669 49.913681 28.304632 50.163147 28.36387 50.412591 28.423319 50.662016 28.483058 50.911419 32.000866 50.519131"}]}]

        if previous_logging_level:
            os.environ["EBOA_LOG_LEVEL"] = previous_logging_level
        else:
            del os.environ["EBOA_LOG_LEVEL"]
        # end if
        logging_module.define_logging_configuration()

    def test_associate_footprints_ew_s1a(self):

        logging_module = Log(name = __name__)
        previous_logging_level = None
        if "EBOA_LOG_LEVEL" in os.environ:
            previous_logging_level = os.environ["EBOA_LOG_LEVEL"]
        # end if

        os.environ["EBOA_LOG_LEVEL"] = "DEBUG"

        logging_module.define_logging_configuration()
        
        # Minimum window is [date - 200 minutes, date + 200 minutes]
        events_per_imaging_mode = {
            "EW": [{"start": "2021-03-16T18:10:52.302000",
                    "stop": "2021-03-16T18:12:01.502000",
                    }]
        }

        events_with_footprint = s1boa_functions.associate_footprints(events_per_imaging_mode, "S1A")

        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {"name": "dim_signature",
                              "exec": "exec",
                              "version": "1.0"},
            "source": {"name": "source.xml",
                       "reception_time": "2018-06-06T13:33:29",
                       "generation_time": "2018-07-05T02:07:03",
                       "validity_start": "2018-06-05T02:07:03",
                       "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T02:07:03",
                "stop": "2018-06-05T08:07:36",
                "values": events_with_footprint[0]["values"]
            }]
        }]
        }
        exit_status = self.engine_eboa.treat_data(data)

        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0


        assert len(events_with_footprint) == 1
        
        assert events_with_footprint[0]["values"] == [
            {"name": "footprint_details",
             "type": "object",
             "values": [{"name": "footprint",
                         "type": "geometry",
                         "value": "32.000866 50.519131 31.922603 50.270001 31.844881 50.020833 31.767632 49.771631 31.690902 49.522393 31.614684 49.273118 31.538968 49.023807 28.128559 49.414686 28.18698 49.664194 28.245669 49.913681 28.304632 50.163147 28.36387 50.412591 28.423319 50.662016 28.483058 50.911419 32.000866 50.519131"}]}]

        if previous_logging_level:
            os.environ["EBOA_LOG_LEVEL"] = previous_logging_level
        else:
            del os.environ["EBOA_LOG_LEVEL"]
        # end if
        logging_module.define_logging_configuration()
