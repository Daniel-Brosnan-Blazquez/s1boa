"""
Automated tests for the DHUS availability view

Written by DEIMOS Space S.L. (dibb)

module s1boa
"""
import os
import sys
import unittest
import time
import subprocess
import datetime
import s1vboa.tests.dhus_availability.aux_functions as functions
import vboa.tests.functions as functions_vboa
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains,TouchActions
from selenium.webdriver.common.keys import Keys

# Import engine of the DDBB
import eboa.engine.engine as eboa_engine
import eboa.ingestion.eboa_ingestion as ingestion
import eboa.triggering.eboa_triggering as triggering
from eboa.engine.engine import Engine
from eboa.engine.query import Query

class TestDhusAvailabilityView(unittest.TestCase):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('window-size=1920,1080')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

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

    @classmethod
    def tearDownClass(self):
        self.driver.quit()

    def test_dhus_availability_no_data(self):

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/views/dhus-availability")

        functions.query(self.driver, wait, mission = "S1A", start = "2018-07-01T00:00:00", stop = "2018-07-31T23:59:59", start_orbit = "17600", stop_orbit = "17800", table_details = True, map = True, station_reports = True)

        # Check header generated
        header_no_data = wait.until(EC.visibility_of_element_located((By.ID,"header-no-data")))

        assert header_no_data

        table_details_no_data = wait.until(EC.visibility_of_element_located((By.ID,"dhus-availability-no-planned-imaging")))

        assert table_details_no_data

    def test_dhus_availability_only_plan(self):

        filename = "S1A_OPER_MPL__NPPF__20210316T160000_20210405T180000_0001_SHORTENED.EOF"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/inputs/" + filename

        exit_status = ingestion.command_process_file("s1boa.ingestions.ingestion_nppf.ingestion_nppf", file_path, "2018-01-01T00:00:00")

        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/views/dhus-availability")

        functions.query(self.driver, wait, "S1_", start = "2021-03-16T00:00:00	", stop = "2021-03-17T23:59:59")

        # Check summary ununexpected duration L0
        summary_unexpected_l0 = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-available-duration-L0")))

        assert summary_unexpected_l0

        assert summary_unexpected_l0.text == "0.0"

        # Check summary ununexpected duration L1_SLC
        summary_unexpected_l1_slc = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-available-duration-L1_SLC")))

        assert summary_unexpected_l1_slc

        assert summary_unexpected_l1_slc.text == "0.0"

        # Check summary unexpected duration L1_GRD
        summary_unexpected_l1_grd = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-available-duration-L1_GRD")))

        assert summary_unexpected_l1_grd

        assert summary_unexpected_l1_grd.text == "0.0"

        # Check summary unexpected duration L2_OCN
        summary_unexpected_l2_ocn = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-available-duration-L2_OCN")))

        assert summary_unexpected_l2_ocn

        assert summary_unexpected_l2_ocn.text == "0.0"

        # Check summary missing duration L0
        summary_missing_l0 = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-missing-duration-L0")))

        assert summary_missing_l0

        assert summary_missing_l0.text == "11.479"

        # Check summary missing duration L1_SLC
        summary_missing_l1_slc = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-missing-duration-L1_SLC")))

        assert summary_missing_l1_slc

        assert summary_missing_l1_slc.text == "22.375"

        # Check summary missing duration L1_GRD
        summary_missing_l1_grd = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-missing-duration-L1_GRD")))

        assert summary_missing_l1_grd

        assert summary_missing_l1_grd.text == "11.479"

       # Check summary missing duration L2_OCN
        summary_missing_l2_ocn = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-missing-duration-L2_OCN")))

        assert summary_missing_l2_ocn

        assert summary_missing_l2_ocn.text == "27.091"

        # Check whether the map is displayed
        map_section = self.driver.find_element_by_id("dhus-availability-maps-section")

        condition = map_section.is_displayed()

        assert condition is True

        l0_map_section = self.driver.find_element_by_id("dhus-availability-map-L0-section")

        condition = l0_map_section.is_displayed()

        assert condition is True

        l1_slc_map_section = self.driver.find_element_by_id("dhus-availability-map-L1_SLC-section")

        condition = l1_slc_map_section.is_displayed()

        assert condition is True

        l1_grd_map_section = self.driver.find_element_by_id("dhus-availability-map-L1_GRD-section")

        condition = l1_grd_map_section.is_displayed()

        assert condition is True

        l2_ocn_map_section = self.driver.find_element_by_id("dhus-availability-map-L2_OCN-section")

        condition = l2_ocn_map_section.is_displayed()

        assert condition is True

        planned_imaging = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-16T18:10:59.878756", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-16T18:16:12.831484", "op": "=="}])

        dhus_product_completeness_l0 = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-16T18:11:09.878756", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-16T18:15:52.831484", "op": "=="}])
        
        map_l0_tooltip_info = [
            {
                "id": str(dhus_product_completeness_l0[0].event_uuid),
                "geometries": [{
                    "name": "footprint",
                    "type": "geometry",
                    "value": "POLYGON ((-146.527938 79.608563, -147.25676 79.432294, -147.96247 79.25449, -148.646159 79.075244, -149.3085 78.89459600000001, -149.950364 78.712614, -150.572737 78.529381, -151.176415 78.344954, -151.762008 78.15937099999999, -152.33025 77.972686, -152.882055 77.78497400000001, -153.417949 77.596266, -153.938493 77.406597, -154.444297 77.21601, -154.93622 77.024576, -155.414543 76.832303, -155.879793 76.639224, -156.332535 76.445382, -156.773407 76.25082399999999, -157.202654 76.055559, -157.620719 75.85961399999999, -158.028143 75.66303000000001, -158.425348 75.465836, -158.812576 75.26804, -159.190196 75.069667, -159.558732 74.870757, -159.91842 74.671322, -160.269503 74.471371, -160.61229 74.270926, -160.947296 74.07002799999999, -161.274592 73.868673, -161.594431 73.66687400000001, -161.90711 73.464653, -162.213025 73.26204, -162.51222 73.05903000000001, -162.80492 72.855636, -163.091434 72.65188000000001, -163.372006 72.44777999999999, -163.646705 72.243334, -163.91572 72.03855299999999, -164.179374 71.833462, -164.437777 71.628066, -164.691021 71.422366, -164.939271 71.216373, -165.182861 71.010113, -165.421781 70.80358, -165.656153 70.59678, -165.886139 70.389723, -166.112018 70.18243200000001, -166.333744 69.974897, -166.551441 69.76712499999999, -166.765297 69.55913, -166.975475 69.35092400000001, -167.181963 69.1425, -167.384868 68.93386599999999, -167.584402 68.725038, -167.780623 68.51601700000001, -167.973553 68.306802, -168.163284 68.097399, -168.350052 67.887826, -168.53382 67.678077, -168.714642 67.468154, -168.892611 67.258062, -169.067946 67.047821, -169.240563 66.837418, -169.410532 66.626858, -169.577977 66.41615, -169.743022 66.205303, -169.905618 65.99431, -170.065829 65.783175, -170.223803 65.57190900000001, -170.379579 65.36051399999999, -170.533143 65.14898700000001, -170.68455 64.93733, -170.833975 64.725559, -170.981377 64.513666, -171.126774 64.301652, -171.270219 64.089521, -171.411898 63.877288, -179.788062 64.682958, -179.710233 64.89884000000001, -179.631741 65.114701, -179.55236 65.330533, -179.47206 65.54633699999999, -179.390862 65.762112, -179.308876 65.977863, -179.225898 66.193584, -179.141899 66.409273, -179.056956 66.624934, -178.971068 66.84056699999999, -178.884076 67.056167, -178.795947 67.271734, -178.706816 67.487273, -178.616563 67.70277900000001, -178.525076 67.91825, -178.432318 68.133684, -178.338485 68.34909, -178.243329 68.564459, -178.146788 68.77978899999999, -178.048862 68.995081, -177.949687 69.210341, -177.848999 69.42556, -177.746751 69.640736, -177.643 69.855873, -177.537755 70.070972, -177.430799 70.28602600000001, -177.322074 70.50103300000001, -177.211703 70.715999, -177.099551 70.93092, -176.985453 71.145791, -176.869339 71.36060999999999, -176.751402 71.57538599999999, -176.63135 71.790108, -176.50907 72.004775, -176.384516 72.219385, -176.257846 72.43394600000001, -176.128702 72.648445, -175.996991 72.862881, -175.86273 73.077257, -175.725919 73.291573, -175.586243 73.505819, -175.443589 73.719993, -175.298041 73.934101, -175.149419 74.14813599999999, -174.997454 74.362092, -174.842008 74.575965, -174.683234 74.78976400000001, -174.520751 75.00347600000001, -174.354333 75.217096, -174.183837 75.43062, -174.009411 75.644058, -173.830517 75.857393, -173.646953 76.070618, -173.458624 76.28373499999999, -173.265464 76.496746, -173.066959 76.709633, -172.862848 76.922391, -172.653091 77.135024, -172.437365 77.347523, -172.215169 77.55987500000001, -171.98617 77.772071, -171.75037 77.98412, -171.507143 78.196001, -171.255987 78.407702, -170.996477 78.619214, -170.728613 78.830546, -170.451431 79.041667, -170.164394 79.252565, -169.867054 79.463234, -169.559045 79.673669, -169.239317 79.88383899999999, -168.90714 80.09372999999999, -168.562002 80.30333299999999, -168.203064 80.512631, -167.829123 80.721591, -167.439168 80.93019, -167.032546 81.13842099999999, -166.607792 81.34624700000001, -146.527938 79.608563))"
                }],
                "style": {"stroke_color": "red", "fill_color": "rgba(255,0,0,0.3)"},
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L0</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37027.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l0[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l0[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>4.716</td></tr>" +
                "<tr><td>Imaging mode</td><td>EXTRA_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-red' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>MISSING</a></td></tr>" +
                "<tr><td>Product</td><td><a class='bold-red'>N/A</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td><a class='bold-red'>N/A</a></td></tr>" +
                "<tr><td>Size (GB)</td><td><a class='bold-red'>N/A</a></td></tr>" + 
                "<tr><td>Datatake id</td><td>45B92</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-16T18:10:59.878756</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-16T18:16:12.831484</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>5.216</td></tr>"
                "</table>"
            } 
        ]

        dhus_availability_data_maps_l0 = self.driver.execute_script('return dhus_availability_data_maps["L0"].find(element => element.id === "' + str(dhus_product_completeness_l0[0].event_uuid) + '");')
        assert dhus_availability_data_maps_l0 == map_l0_tooltip_info[0]
        
        planned_imaging = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-16T18:36:27.354551", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-16T18:36:37.353521", "op": "=="}])
        
        dhus_product_completeness_l1_slc = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-16T18:36:27.354551", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-16T18:36:27.354551", "op": "=="}])

        map_l1_slc_tooltip_info = [
            {
                "id": str(dhus_product_completeness_l1_slc[0].event_uuid),
                "geometries": [{
                    "name": "footprint",
                    "type": "geometry",
                    "value": "POLYGON ((165.852559 -9.933427, 165.131247 -9.770303999999999, 165.131247 -9.770303999999999, 165.852559 -9.933427))"
                }],
                "style": {"stroke_color": "red", "fill_color": "rgba(255,0,0,0.3)"},
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_SLC</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37027.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_slc[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_slc[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.0</td></tr>" +
                "<tr><td>Imaging mode</td><td>STRIPMAP4_WITHOUT_CALIBRATION</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-red' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>MISSING</a></td></tr>" +
                "<tr><td>Product</td><td><a class='bold-red'>N/A</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td><a class='bold-red'>N/A</a></td></tr>" +
                "<tr><td>Size (GB)</td><td><a class='bold-red'>N/A</a></td></tr>" +  
                "<tr><td>Datatake id</td><td>45B95</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-16T18:36:27.354551</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-16T18:36:37.353521</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>0.167</td></tr>"
                "</table>"
            } 
        ]

        dhus_availability_data_maps_l1_slc = self.driver.execute_script('return dhus_availability_data_maps["L1_SLC"].find(element => element.id === "' + str(dhus_product_completeness_l1_slc[0].event_uuid) + '");')
        assert dhus_availability_data_maps_l1_slc == map_l1_slc_tooltip_info[0]

        planned_imaging = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:10:33.066685", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:17:48.873819", "op": "=="}])
        
        dhus_product_completeness_l1_grd = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:10:43.066685", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:17:28.873819", "op": "=="}])

        map_l1_grd_tooltip_info = [
            {
                "id": str(dhus_product_completeness_l1_grd[0].event_uuid),
                "geometries": [{
                    "name": "footprint",
                    "type": "geometry",
                    "value": "POLYGON ((33.787361 55.739162, 33.706972 55.523299, 33.627243 55.307396, 33.548079 55.09146, 33.469507 54.875489, 33.391559 54.659479, 33.314223 54.443432, 33.237379 54.227355, 33.161114 54.011243, 33.085429 53.795094, 33.010296 53.578911, 32.935622 53.362699, 32.861498 53.146452, 32.787915 52.930171, 32.714816 52.713859, 32.64217 52.497517, 32.570037 52.281143, 32.498408 52.064735, 32.427201 51.8483, 32.356443 51.631834, 32.286163 51.415337, 32.216354 51.198809, 32.146909 50.982255, 32.077908 50.765671, 32.009356 50.549056, 31.941227 50.332413, 31.873441 50.115745, 31.806081 49.899047, 31.73914 49.68232, 31.672568 49.465567, 31.606341 49.248789, 31.540513 49.031982, 31.475077 48.815147, 31.40996 48.598288, 31.34519 48.381403, 31.280793 48.164492, 31.216765 47.947553, 31.153008 47.730592, 31.0896 47.513605, 31.026542 47.296592, 30.963815 47.079554, 30.901347 46.862494, 30.839214 46.645409, 30.777411 46.428298, 30.715894 46.211164, 30.654641 45.994009, 30.593703 45.776828, 30.533075 45.559623, 30.472691 45.342397, 30.412577 45.125149, 30.35276 44.907876, 30.293234 44.69058, 30.233913 44.473265, 30.174867 44.255927, 30.116101 44.038566, 30.057595 43.821182, 29.999285 43.60378, 29.941243 43.386355, 29.883463 43.168908, 29.825906 42.95144, 29.768553 42.733953, 29.711453 42.516444, 29.654599 42.298914, 29.597934 42.081365, 29.54148 41.863795, 29.485264 41.646205, 29.429281 41.428594, 29.373453 41.210965, 29.317845 40.993317, 29.26246 40.775648, 29.207281 40.557959, 29.152253 40.340253, 29.097438 40.122527, 29.042835 39.904782, 28.988406 39.687018, 28.934136 39.469236, 28.880068 39.251436, 28.826199 39.033616, 28.772475 38.81578, 28.718918 38.597925, 28.665552 38.380052, 28.612374 38.162161, 28.559311 37.944253, 28.506425 37.726328, 28.453719 37.508385, 28.401177 37.290424, 28.348749 37.072448, 28.296494 36.854454, 28.244408 36.636442, 28.192459 36.418414, 28.140633 36.200371, 28.088971 35.98231, 28.037468 35.764232, 27.986076 35.54614, 27.934816 35.328031, 27.88371 35.109906, 27.832755 34.891764, 27.781886 34.673608, 27.731158 34.455437, 27.680575 34.237249, 27.630123 34.019045, 27.579756 33.800828, 27.529528 33.582595, 27.479436 33.364347, 27.429451 33.146084, 27.379561 32.927807, 27.329801 32.709515, 27.28017 32.491208, 27.230623 32.272887, 27.181179 32.054552, 27.131859 31.836203, 27.082661 31.617839, 27.033523 31.399463, 24.420185 31.80151, 24.463103 32.019546, 24.506002 32.237573, 24.54896 32.455589, 24.591978 32.673594, 24.635032 32.891588, 24.678091 33.109573, 24.721214 33.327546, 24.764403 33.545508, 24.807609 33.763459, 24.850846 33.9814, 24.894153 34.199329, 24.93753 34.417246, 24.980907 34.635153, 25.024341 34.853049, 25.06785 35.070933, 25.111428 35.288805, 25.155 35.506666, 25.19865 35.724516, 25.242381 35.942354, 25.286164 36.16018, 25.329967 36.377995, 25.373855 36.595797, 25.417828 36.813587, 25.461835 37.031366, 25.505891 37.249133, 25.550037 37.466887, 25.594275 37.684629, 25.638528 37.902359, 25.682859 38.120078, 25.727287 38.337783, 25.771805 38.555475, 25.816333 38.773156, 25.860963 38.990824, 25.905695 39.208479, 25.9505 39.426121, 25.995345 39.643751, 26.040298 39.861368, 26.085361 40.078972, 26.130478 40.296563, 26.175665 40.514142, 26.220968 40.731706, 26.266389 40.949258, 26.311843 41.166797, 26.357401 41.384323, 26.403081 41.601835, 26.448879 41.819333, 26.494707 42.036819, 26.540664 42.254291, 26.586752 42.471749, 26.632939 42.689193, 26.679189 42.906625, 26.725576 43.124043, 26.772104 43.341446, 26.81871 43.558835, 26.865415 43.776212, 26.912266 43.993574, 26.959267 44.210921, 27.006326 44.428255, 27.05352 44.645575, 27.100871 44.86288, 27.148371 45.08017, 27.195928 45.297448, 27.243649 45.514711, 27.291537 45.731958, 27.339555 45.949191, 27.387668 46.166411, 27.435956 46.383616, 27.484422 46.600804, 27.532999 46.817979, 27.58171 47.03514, 27.630608 47.252285, 27.679695 47.469414, 27.728874 47.68653, 27.778228 47.903631, 27.827782 48.120716, 27.877527 48.337784, 27.927365 48.55484, 27.977412 48.771879, 28.027671 48.988903, 28.078104 49.205911, 28.128673 49.422904, 28.179465 49.639881, 28.230484 49.856842, 28.281658 50.073788, 28.333014 50.290719, 28.384608 50.507633, 28.436446 50.724529, 28.488419 50.941412, 28.540622 51.158279, 28.593081 51.375128, 28.645788 51.59196, 28.698636 51.808778, 28.751753 52.025579, 28.805144 52.242362, 28.858766 52.459129, 28.91258 52.675881, 28.966683 52.892615, 29.02108 53.109331, 29.075691 53.326031, 29.130548 53.542715, 29.185715 53.75938, 29.241198 53.976028, 29.296879 54.19266, 29.352863 54.409274, 29.40918 54.62587, 29.465823 54.842447, 29.522675 55.059009, 29.579879 55.275552, 29.637442 55.492075, 29.695316 55.708581, 29.753462 55.925071, 29.811987 56.141541, 33.787361 55.739162))"
                }],
                "style": {"stroke_color": "red", "fill_color": "rgba(255,0,0,0.3)"},
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_GRD</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_grd[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_grd[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>6.763</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-red' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>MISSING</a></td></tr>" +
                "<tr><td>Product</td><td><a class='bold-red'>N/A</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td><a class='bold-red'>N/A</a></td></tr>" +
                "<tr><td>Size (GB)</td><td><a class='bold-red'>N/A</a></td></tr>" +
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>"
            } 
        ]

        dhus_availability_data_maps_l1_grd = self.driver.execute_script('return dhus_availability_data_maps["L1_GRD"].find(element => element.id === "' + str(dhus_product_completeness_l1_grd[0].event_uuid) + '");')
        assert dhus_availability_data_maps_l1_grd == map_l1_grd_tooltip_info[0]
        
        planned_imaging = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-16T18:10:59.878756", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-16T18:16:12.831484", "op": "=="}])
        
        dhus_product_completeness_l2ocn = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L2_OCN", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-16T18:11:09.878756", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-16T18:15:52.831484", "op": "=="}])
        
        map_l2ocn_tooltip_info = [
            {
                "id": str(dhus_product_completeness_l2ocn[0].event_uuid),
                "geometries": [{
                    "name": "footprint",
                    "type": "geometry",
                    "value": "POLYGON ((-146.527938 79.608563, -147.25676 79.432294, -147.96247 79.25449, -148.646159 79.075244, -149.3085 78.89459600000001, -149.950364 78.712614, -150.572737 78.529381, -151.176415 78.344954, -151.762008 78.15937099999999, -152.33025 77.972686, -152.882055 77.78497400000001, -153.417949 77.596266, -153.938493 77.406597, -154.444297 77.21601, -154.93622 77.024576, -155.414543 76.832303, -155.879793 76.639224, -156.332535 76.445382, -156.773407 76.25082399999999, -157.202654 76.055559, -157.620719 75.85961399999999, -158.028143 75.66303000000001, -158.425348 75.465836, -158.812576 75.26804, -159.190196 75.069667, -159.558732 74.870757, -159.91842 74.671322, -160.269503 74.471371, -160.61229 74.270926, -160.947296 74.07002799999999, -161.274592 73.868673, -161.594431 73.66687400000001, -161.90711 73.464653, -162.213025 73.26204, -162.51222 73.05903000000001, -162.80492 72.855636, -163.091434 72.65188000000001, -163.372006 72.44777999999999, -163.646705 72.243334, -163.91572 72.03855299999999, -164.179374 71.833462, -164.437777 71.628066, -164.691021 71.422366, -164.939271 71.216373, -165.182861 71.010113, -165.421781 70.80358, -165.656153 70.59678, -165.886139 70.389723, -166.112018 70.18243200000001, -166.333744 69.974897, -166.551441 69.76712499999999, -166.765297 69.55913, -166.975475 69.35092400000001, -167.181963 69.1425, -167.384868 68.93386599999999, -167.584402 68.725038, -167.780623 68.51601700000001, -167.973553 68.306802, -168.163284 68.097399, -168.350052 67.887826, -168.53382 67.678077, -168.714642 67.468154, -168.892611 67.258062, -169.067946 67.047821, -169.240563 66.837418, -169.410532 66.626858, -169.577977 66.41615, -169.743022 66.205303, -169.905618 65.99431, -170.065829 65.783175, -170.223803 65.57190900000001, -170.379579 65.36051399999999, -170.533143 65.14898700000001, -170.68455 64.93733, -170.833975 64.725559, -170.981377 64.513666, -171.126774 64.301652, -171.270219 64.089521, -171.411898 63.877288, -179.788062 64.682958, -179.710233 64.89884000000001, -179.631741 65.114701, -179.55236 65.330533, -179.47206 65.54633699999999, -179.390862 65.762112, -179.308876 65.977863, -179.225898 66.193584, -179.141899 66.409273, -179.056956 66.624934, -178.971068 66.84056699999999, -178.884076 67.056167, -178.795947 67.271734, -178.706816 67.487273, -178.616563 67.70277900000001, -178.525076 67.91825, -178.432318 68.133684, -178.338485 68.34909, -178.243329 68.564459, -178.146788 68.77978899999999, -178.048862 68.995081, -177.949687 69.210341, -177.848999 69.42556, -177.746751 69.640736, -177.643 69.855873, -177.537755 70.070972, -177.430799 70.28602600000001, -177.322074 70.50103300000001, -177.211703 70.715999, -177.099551 70.93092, -176.985453 71.145791, -176.869339 71.36060999999999, -176.751402 71.57538599999999, -176.63135 71.790108, -176.50907 72.004775, -176.384516 72.219385, -176.257846 72.43394600000001, -176.128702 72.648445, -175.996991 72.862881, -175.86273 73.077257, -175.725919 73.291573, -175.586243 73.505819, -175.443589 73.719993, -175.298041 73.934101, -175.149419 74.14813599999999, -174.997454 74.362092, -174.842008 74.575965, -174.683234 74.78976400000001, -174.520751 75.00347600000001, -174.354333 75.217096, -174.183837 75.43062, -174.009411 75.644058, -173.830517 75.857393, -173.646953 76.070618, -173.458624 76.28373499999999, -173.265464 76.496746, -173.066959 76.709633, -172.862848 76.922391, -172.653091 77.135024, -172.437365 77.347523, -172.215169 77.55987500000001, -171.98617 77.772071, -171.75037 77.98412, -171.507143 78.196001, -171.255987 78.407702, -170.996477 78.619214, -170.728613 78.830546, -170.451431 79.041667, -170.164394 79.252565, -169.867054 79.463234, -169.559045 79.673669, -169.239317 79.88383899999999, -168.90714 80.09372999999999, -168.562002 80.30333299999999, -168.203064 80.512631, -167.829123 80.721591, -167.439168 80.93019, -167.032546 81.13842099999999, -166.607792 81.34624700000001, -146.527938 79.608563))"
                }],
                "style": {"stroke_color": "red", "fill_color": "rgba(255,0,0,0.3)"},
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L2_OCN</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37027.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l2ocn[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l2ocn[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>4.716</td></tr>" +
                "<tr><td>Imaging mode</td><td>EXTRA_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-red' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>MISSING</a></td></tr>" +
                "<tr><td>Product</td><td><a class='bold-red'>N/A</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td><a class='bold-red'>N/A</a></td></tr>" +
                "<tr><td>Size (GB)</td><td><a class='bold-red'>N/A</a></td></tr>" +
                "<tr><td>Datatake id</td><td>45B92</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-16T18:10:59.878756</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-16T18:16:12.831484</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>5.216</td></tr>"
                "</table>"
            } 
        ]

        dhus_availability_data_maps_l2_ocn = self.driver.execute_script('return dhus_availability_data_maps["L2_OCN"].find(element => element.id === "' + str(dhus_product_completeness_l2ocn[0].event_uuid) + '");')
        assert dhus_availability_data_maps_l2_ocn == map_l2ocn_tooltip_info[0]

        # Timeline
        timeline_section = self.driver.find_element_by_id("dhus-availability-timeline")

        condition = timeline_section.is_displayed()

        assert condition is True

        planned_imaging = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:10:33.066685", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:17:48.873819", "op": "=="}])
        
        dhus_product_completeness_l1_grd = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:10:43.066685", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:17:28.873819", "op": "=="}])

        timeline_l1_grd_tooltip_info = [
            {
                "className": "fill-border-red",
                "group": "S1A",
                "id": str(dhus_product_completeness_l1_grd[0].event_uuid),
                
                "start": "2021-03-17T04:10:43.066685",
                "stop": "2021-03-17T04:17:28.873819",
                "timeline": "L1_GRD",
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_GRD</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_grd[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_grd[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>6.763</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-red' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>MISSING</a></td></tr>" +
                "<tr><td>Product</td><td><a class='bold-red'>N/A</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td><a class='bold-red'>N/A</a></td></tr>" +
                "<tr><td>Size (GB)</td><td><a class='bold-red'>N/A</a></td></tr>" +
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>"
            }
        ]

        dhus_availability_data_timeline_l1_grd = self.driver.execute_script('return dhus_availability_data_timeline.find(element => element.id === "' + str(dhus_product_completeness_l1_grd[0].event_uuid) + '");')
        assert dhus_availability_data_timeline_l1_grd == timeline_l1_grd_tooltip_info[0]

        # Check complete table
        missing_table = self.driver.find_element_by_id("dhus-completeness-list-table-MISSING")

        # Row 1
        level = missing_table.find_element_by_xpath("tbody/tr[1]/td[1]")

        assert level.text == "L0"

        satellite = missing_table.find_element_by_xpath("tbody/tr[1]/td[2]")

        assert satellite.text == "S1A"

        orbit = missing_table.find_element_by_xpath("tbody/tr[1]/td[3]")

        assert orbit.text == "37027.0"

        start = missing_table.find_element_by_xpath("tbody/tr[1]/td[4]")

        assert start.text == "2021-03-16T18:11:09.878756"

        stop = missing_table.find_element_by_xpath("tbody/tr[1]/td[5]")

        assert stop.text == "2021-03-16T18:15:52.831484"

        duration = missing_table.find_element_by_xpath("tbody/tr[1]/td[6]")

        assert duration.text == "4.716"

        imaging_mode = missing_table.find_element_by_xpath("tbody/tr[1]/td[7]")

        assert imaging_mode.text == "EXTRA_WIDE_SWATH"

        status = missing_table.find_element_by_xpath("tbody/tr[1]/td[8]")

        assert status.text == "MISSING"

        product = missing_table.find_element_by_xpath("tbody/tr[1]/td[9]")

        assert product.text == "N/A"

        time_dhus_publication = missing_table.find_element_by_xpath("tbody/tr[1]/td[10]")

        assert time_dhus_publication.text == "N/A"

        size = missing_table.find_element_by_xpath("tbody/tr[1]/td[11]")

        assert size.text == "N/A"

        datatake_id = missing_table.find_element_by_xpath("tbody/tr[1]/td[12]")

        assert datatake_id.text == "45B92"

        start = missing_table.find_element_by_xpath("tbody/tr[1]/td[13]")

        assert start.text == "2021-03-16T18:10:59.878756"

        stop = missing_table.find_element_by_xpath("tbody/tr[1]/td[14]")

        assert stop.text == "2021-03-16T18:16:12.831484"

        datatake_duration = missing_table.find_element_by_xpath("tbody/tr[1]/td[15]")

        assert datatake_duration.text == "5.216"

        # Check complete table
        complete_table = self.driver.find_element_by_id("dhus-completeness-list-table-COMPLETE")

        # Row 1
        level = complete_table.find_element_by_xpath("tbody/tr[1]/td[1]")

        assert level.text == "L0"

        satellite = complete_table.find_element_by_xpath("tbody/tr[1]/td[2]")

        assert satellite.text == "S1A"

        orbit = complete_table.find_element_by_xpath("tbody/tr[1]/td[3]")

        assert orbit.text == "37027.0"

        start = complete_table.find_element_by_xpath("tbody/tr[1]/td[4]")

        assert start.text == "2021-03-16T18:11:09.878756"

        stop = complete_table.find_element_by_xpath("tbody/tr[1]/td[5]")

        assert stop.text == "2021-03-16T18:15:52.831484"

        duration = complete_table.find_element_by_xpath("tbody/tr[1]/td[6]")

        assert duration.text == "4.716"

        imaging_mode = complete_table.find_element_by_xpath("tbody/tr[1]/td[7]")

        assert imaging_mode.text == "EXTRA_WIDE_SWATH"

        status = complete_table.find_element_by_xpath("tbody/tr[1]/td[8]")

        assert status.text == "MISSING"

        product = complete_table.find_element_by_xpath("tbody/tr[1]/td[9]")

        assert product.text == "N/A"

        time_dhus_publication = complete_table.find_element_by_xpath("tbody/tr[1]/td[10]")

        assert time_dhus_publication.text == "N/A"

        size = complete_table.find_element_by_xpath("tbody/tr[1]/td[11]")

        assert size.text == "N/A"

        datatake_id = complete_table.find_element_by_xpath("tbody/tr[1]/td[12]")

        assert datatake_id.text == "45B92"

        start = complete_table.find_element_by_xpath("tbody/tr[1]/td[13]")

        assert start.text == "2021-03-16T18:10:59.878756"

        stop = complete_table.find_element_by_xpath("tbody/tr[1]/td[14]")

        assert stop.text == "2021-03-16T18:16:12.831484"

        datatake_duration = complete_table.find_element_by_xpath("tbody/tr[1]/td[15]")

        assert datatake_duration.text == "5.216"

    def test_dhus_availability_only_opdhus(self):

        filename = "DEC_OPER_OPDHUS_S1A_AUIP_20210419T135405_V20210316T000000_20210319T000000_2161_2150_SHORTENED.xml"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/inputs/" + filename

        exit_status = ingestion.command_process_file("s1boa.ingestions.ingestion_dhus_products.ingestion_dhus_products", file_path, "2018-01-01T00:00:00")

        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/views/dhus-availability")

        functions.query(self.driver, wait, "S1_", start = "2021-03-17T00:00:00", stop = "2021-03-17T23:59:59")

        """ # Check summary pies
        # L0
        processing_data_l0_pie_info = [1,0]

        returned_processing_data_l0_pie_info = self.driver.execute_script('return processing_data_l0;')
        assert processing_data_l0_pie_info == returned_processing_data_l0_pie_info

        # L1B
        processing_data_l1b_pie_info = [1,0]

        returned_processing_data_l1b_pie_info = self.driver.execute_script('return processing_data_l1b;')
        assert processing_data_l1b_pie_info == returned_processing_data_l1b_pie_info

        # L1C
        processing_data_l1c_pie_info = [1,0]

        returned_processing_data_l1c_pie_info = self.driver.execute_script('return processing_data_l1c;')
        assert processing_data_l1c_pie_info == returned_processing_data_l1c_pie_info
        
        # L2A
        processing_data_l2a_pie_info = [1,0]

        returned_processing_data_l2a_pie_info = self.driver.execute_script('return processing_data_l2a;')
        assert processing_data_l2a_pie_info == returned_processing_data_l2a_pie_info """
        
        # Check summary ununexpected duration L0
        summary_unexpected_l0 = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-unexpected-duration-L0")))

        assert summary_unexpected_l0

        assert summary_unexpected_l0.text == "2.472"

        # Check summary ununexpected duration L1_SLC
        summary_unexpected_l1_slc = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-unexpected-duration-L1_SLC")))

        assert summary_unexpected_l1_slc

        assert summary_unexpected_l1_slc.text == "2.221"

        # Check summary unexpected duration L1_GRD
        summary_unexpected_l1_grd = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-unexpected-duration-L1_GRD")))

        assert summary_unexpected_l1_grd

        assert summary_unexpected_l1_grd.text == "2.562"

        # Check summary unexpected duration L2_OCN
        summary_unexpected_l2_ocn = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-unexpected-duration-L2_OCN")))

        assert summary_unexpected_l2_ocn

        assert summary_unexpected_l2_ocn.text == "1.884"

        # Check summary expected duration L0
        summary_expected_l0 = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-available-duration-L0")))

        assert summary_expected_l0

        assert summary_expected_l0.text == "0.0"

        # Check summary expected duration L1_SLC
        summary_expected_l1_slc = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-available-duration-L1_SLC")))

        assert summary_expected_l1_slc

        assert summary_expected_l1_slc.text == "0.0"

        # Check summary expected duration L1_GRD
        summary_expected_l1_grd = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-available-duration-L1_GRD")))

        assert summary_expected_l1_grd

        assert summary_expected_l1_grd.text == "0.0"

       # Check summary expected duration L2_OCN
        summary_expected_l2_ocn = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-available-duration-L2_OCN")))

        assert summary_expected_l2_ocn

        assert summary_expected_l2_ocn.text == "0.0"

        # Summary data pie L0
        data_pie_l0 = [0, 0, 2.472]

        returned_data_pie_l0 = self.driver.execute_script('return completeness.L0.slice(0, 3);')
        assert data_pie_l0 == returned_data_pie_l0

        # Summary data pie L1_SLC
        data_pie_l1_slc = [0, 0, 2.221]

        returned_data_pie_l1_slc = self.driver.execute_script('return completeness.L1_SLC.slice(0, 3);')
        assert data_pie_l1_slc == returned_data_pie_l1_slc

        # Summary data pie L1_GRD
        data_pie_l1_grd = [0, 0, 2.562]

        returned_data_pie_l1_grd = self.driver.execute_script('return completeness.L1_GRD.slice(0, 3);')
        assert data_pie_l1_grd == returned_data_pie_l1_grd

        # Summary data pie L2_OCN
        data_pie_l2_ocn = [0, 0, 1.884]

        returned_data_pie_l2_ocn = self.driver.execute_script('return completeness.L2_OCN.slice(0, 3);')
        assert data_pie_l2_ocn == returned_data_pie_l2_ocn
        
        # Summary data pie volumes
        data_pie_volumes = ["7.210", "18.849", "3.934"]

        returned_data_pie_volumes = self.driver.execute_script('return data_pie_volumes.datasets[0].data.slice(0, 3);')
        assert data_pie_volumes == returned_data_pie_volumes

        # Check whether the map is displayed
        map_section = self.driver.find_element_by_id("dhus-availability-maps-section")

        condition = map_section.is_displayed()

        assert condition is True

        l0_map_section = self.driver.find_element_by_id("dhus-availability-map-L0-section")

        condition = l0_map_section.is_displayed()

        assert condition is True

        l1_slc_map_section = self.driver.find_element_by_id("dhus-availability-map-L1_SLC-section")

        condition = l1_slc_map_section.is_displayed()

        assert condition is True

        l1_grd_map_section = self.driver.find_element_by_id("dhus-availability-map-L1_GRD-section")

        condition = l1_grd_map_section.is_displayed()

        assert condition is True

        l2_ocn_map_section = self.driver.find_element_by_id("dhus-availability-map-L2_OCN-section")

        condition = l2_ocn_map_section.is_displayed()

        assert condition is True

        dhus_product_completeness_l0 = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:16:40.803000", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:17:14.203000", "op": "=="}])
        
        map_l0_tooltip_info = [
            {
                "id": str(dhus_product_completeness_l0[0].event_uuid),
                "geometries": [{
                    "name": "footprint",
                    "type": "geometry",
                    "value": "POLYGON ((27.694101 34.295553, 27.642358 34.072066, 27.590754 33.848562, 27.539292 33.625041, 27.487971 33.401505, 27.436734 33.177954, 27.385626 32.954387, 27.334653 32.730805, 27.283811 32.507207, 27.233047 32.283595, 24.594085 32.684286, 24.638196 32.907564, 24.682299 33.130832, 24.726466 33.354088, 24.770698 33.577332, 24.814987 33.800564, 24.859272 34.023786, 24.903625 34.246996, 24.948049 34.470194, 24.992536 34.693379, 27.694101 34.295553))"
                }],
                "style": {"stroke_color": "blue", "fill_color": "rgba(0,0,255,0.3)"},
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L0</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td>37033.0</td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l0[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l0[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.557</td></tr>" +
                "<tr><td>Imaging mode</td><td>IW</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-blue'>UNEXPECTED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l0[0].event_uuid) + "'>S1A_IW_RAW__0SDV_20210317T041641_20210317T041714_037033_045BC0_11CF</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>48.29</td></tr>" +
                "<tr><td>Size (GB)</td><td>1.664</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>N/A</td></tr>" +
                "<tr><td>Datatake stop</td><td>N/A</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>N/A</td></tr>"
                "</table>"
            } 
        ]

        dhus_availability_data_maps_l0 = self.driver.execute_script('return dhus_availability_data_maps["L0"].find(element => element.id === "' + str(dhus_product_completeness_l0[0].event_uuid) + '");')
        assert dhus_availability_data_maps_l0 == map_l0_tooltip_info[0]
        
        dhus_product_completeness_l1_slc = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:17:08.174000", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:17:44.528000", "op": "=="}])

        map_l1_slc_tooltip_info = [
            {
                "id": str(dhus_product_completeness_l1_slc[0].event_uuid),
                "geometries": [{
                    "name": "footprint",
                    "type": "geometry",
                    "value": "POLYGON ((27.315539 32.646864, 27.26576 32.427823, 27.216108 32.208767, 27.166526 31.989698, 27.117058 31.770614, 27.067712 31.551516, 27.01848 31.332403, 26.969309 31.113278, 26.920253 30.894139, 26.871312 30.674986, 26.822465 30.455819, 24.235282 30.859376, 24.278161 31.078187, 24.321068 31.296987, 24.36403 31.515777, 24.407047 31.734556, 24.450046 31.953326, 24.493096 32.172085, 24.536205 32.390833, 24.579363 32.60957, 24.62251 32.828298, 24.665719 33.047014, 27.315539 32.646864))"
                }],
                "style": {"stroke_color": "blue", "fill_color": "rgba(0,0,255,0.3)"},
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_SLC</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td>37033.0</td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_slc[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_slc[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.606</td></tr>" +
                "<tr><td>Imaging mode</td><td>IW</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-blue'>UNEXPECTED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_slc[0].event_uuid) + "'>S1A_IW_SLC__1SDV_20210317T041709_20210317T041744_037033_045BC0_460C</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>459.015</td></tr>" +
                "<tr><td>Size (GB)</td><td>5.376</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>N/A</td></tr>" +
                "<tr><td>Datatake stop</td><td>N/A</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>N/A</td></tr>"
                "</table>"
            } 
        ]

        dhus_availability_data_maps_l1_slc = self.driver.execute_script('return dhus_availability_data_maps["L1_SLC"].find(element => element.id === "' + str(dhus_product_completeness_l1_slc[0].event_uuid) + '");')
        assert dhus_availability_data_maps_l1_slc == map_l1_slc_tooltip_info[0]

        dhus_product_completeness_l1_grd = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:16:19.501000", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:16:45.499000", "op": "=="}])

        map_l1_grd_tooltip_info = [
            {
                "id": str(dhus_product_completeness_l1_grd[0].event_uuid),
                "geometries": [{
                    "name": "footprint",
                    "type": "geometry",
                    "value": "POLYGON ((27.993583 35.578075, 27.941029 35.354507, 27.888633 35.130922, 27.836385 34.90732, 27.784233 34.683703, 27.732234 34.460069, 27.680383 34.236418, 27.628672 34.012751, 24.936282 34.41096, 24.980741 34.634324, 25.025264 34.857675, 25.069861 35.081014, 25.114533 35.304341, 25.15921 35.527656, 25.203953 35.750959, 25.248777 35.97425, 27.993583 35.578075))"
                }],
                "style": {"stroke_color": "blue", "fill_color": "rgba(0,0,255,0.3)"},
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_GRD</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td>37033.0</td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_grd[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_grd[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>IW</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-blue'>UNEXPECTED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_grd[0].event_uuid) + "'>S1A_IW_GRDH_1SDV_20210317T041620_20210317T041645_037033_045BC0_8316</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>99.662</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.848</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>N/A</td></tr>" +
                "<tr><td>Datatake stop</td><td>N/A</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>N/A</td></tr>"
                "</table>"
            } 
        ]

        dhus_availability_data_maps_l1_grd = self.driver.execute_script('return dhus_availability_data_maps["L1_GRD"].find(element => element.id === "' + str(dhus_product_completeness_l1_grd[0].event_uuid) + '");')
        assert dhus_availability_data_maps_l1_grd == map_l1_grd_tooltip_info[0]
        
        dhus_product_completeness_l2ocn = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L2_OCN", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:16:44.501000", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:17:10.499000", "op": "=="}])
        
        map_l2ocn_tooltip_info = [
            {
                "id": str(dhus_product_completeness_l2ocn[0].event_uuid),
                "geometries": [{
                    "name": "footprint",
                    "type": "geometry",
                    "value": "POLYGON ((27.64254 34.072855, 27.590896 33.849177, 27.539394 33.625483, 27.488033 33.401772, 27.436755 33.178048, 27.385608 32.954307, 27.334595 32.730551, 27.283714 32.506778, 24.638111 32.907136, 24.682249 33.130578, 24.72645 33.354008, 24.770716 33.577425, 24.81504 33.800832, 24.85936 34.024227, 24.903747 34.247611, 24.948206 34.470982, 27.64254 34.072855))"
                }],
                "style": {"stroke_color": "blue", "fill_color": "rgba(0,0,255,0.3)"},
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L2_OCN</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td>37033.0</td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l2ocn[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l2ocn[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>IW</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-blue'>UNEXPECTED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l2ocn[0].event_uuid) + "'>S1A_IW_OCN__2SDV_20210317T041645_20210317T041710_037033_045BC0_563F</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>70.536</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.007</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>N/A</td></tr>" +
                "<tr><td>Datatake stop</td><td>N/A</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>N/A</td></tr>"
                "</table>"
            } 
        ]

        dhus_availability_data_maps_l2_ocn = self.driver.execute_script('return dhus_availability_data_maps["L2_OCN"].find(element => element.id === "' + str(dhus_product_completeness_l2ocn[0].event_uuid) + '");')
        assert dhus_availability_data_maps_l2_ocn == map_l2ocn_tooltip_info[0]

        # Check whether the timeliness is displayed
        timeliness_section = self.driver.find_element_by_id("dhus-availability-timeliness-section")

        condition = timeliness_section.is_displayed()

        assert condition is True

        l0_timeliness_section = self.driver.find_element_by_id("dhus-availability-timeliness-L0")

        condition = l0_timeliness_section.is_displayed()

        assert condition is True

        l1_slc_timeliness_section = self.driver.find_element_by_id("dhus-availability-timeliness-L1_SLC")

        condition = l1_slc_timeliness_section.is_displayed()

        assert condition is True

        l1_grd_timeliness_section = self.driver.find_element_by_id("dhus-availability-timeliness-L1_GRD")

        condition = l1_grd_timeliness_section.is_displayed()

        assert condition is True

        l2_ocn_timeliness_section = self.driver.find_element_by_id("dhus-availability-timeliness-L2_OCN")

        condition = l2_ocn_timeliness_section.is_displayed()

        assert condition is True

        # L0
        # Timeliness statics
        timeliness_average_l0 = self.driver.find_element_by_id("summary-dhus-timeliness-average-delta-to-dhus-L0")

        assert timeliness_average_l0.text == "90.492"

        timeliness_minimum_l0 = self.driver.find_element_by_id("summary-dhus-timeliness-minimum-delta-to-dhus-L0")

        assert timeliness_minimum_l0.text == "45.171"

        timeliness_maximum_l0 = self.driver.find_element_by_id("summary-dhus-timeliness-maximum-delta-to-dhus-L0")

        assert timeliness_maximum_l0.text == "169.216"

        timeliness_std_l0 = self.driver.find_element_by_id("summary-dhus-timeliness-std-delta-to-dhus-L0")

        assert timeliness_std_l0.text == "60.910"

        timeliness_l0_tooltip_info = [
            {
                "className": "fill-border-blue",
                "group": "S1A",
                "id": str(dhus_product_completeness_l0[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L0</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td>37033.0</td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l0[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l0[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.557</td></tr>" +
                "<tr><td>Imaging mode</td><td>IW</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-blue'>UNEXPECTED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l0[0].event_uuid) + "'>S1A_IW_RAW__0SDV_20210317T041641_20210317T041714_037033_045BC0_11CF</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>48.29</td></tr>" +
                "<tr><td>Size (GB)</td><td>1.664</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>N/A</td></tr>" +
                "<tr><td>Datatake stop</td><td>N/A</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>N/A</td></tr>"
                "</table>",
                "x": "2021-03-17T04:16:40.803000",
                "y": "48.29"
            } 
        ]

        dhus_availability_data_timeliness_l0 = self.driver.execute_script('return dhus_availability_data_timeliness["L0"].find(element => element.id === "' + str(dhus_product_completeness_l0[0].event_uuid) + '");')
        assert dhus_availability_data_timeliness_l0 == timeliness_l0_tooltip_info[0]

        # L1_SLC
        # Timeliness statics
        timeliness_average_l1_slc = self.driver.find_element_by_id("summary-dhus-timeliness-average-delta-to-dhus-L1_SLC")

        assert timeliness_average_l1_slc.text == "397.468"

        timeliness_minimum_l1_slc = self.driver.find_element_by_id("summary-dhus-timeliness-minimum-delta-to-dhus-L1_SLC")

        assert timeliness_minimum_l1_slc.text == "304.113"

        timeliness_maximum_l1_slc = self.driver.find_element_by_id("summary-dhus-timeliness-maximum-delta-to-dhus-L1_SLC")

        assert timeliness_maximum_l1_slc.text == "459.015"

        timeliness_std_l1_slc = self.driver.find_element_by_id("summary-dhus-timeliness-std-delta-to-dhus-L1_SLC")

        assert timeliness_std_l1_slc.text == "63.241"
        
        timeliness_l1_slc_tooltip_info = [
            {
                "className": "fill-border-blue",
                "group": "S1A",
                "id": str(dhus_product_completeness_l1_slc[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_SLC</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td>37033.0</td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_slc[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_slc[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.606</td></tr>" +
                "<tr><td>Imaging mode</td><td>IW</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-blue'>UNEXPECTED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_slc[0].event_uuid) + "'>S1A_IW_SLC__1SDV_20210317T041709_20210317T041744_037033_045BC0_460C</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>459.015</td></tr>" +
                "<tr><td>Size (GB)</td><td>5.376</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>N/A</td></tr>" +
                "<tr><td>Datatake stop</td><td>N/A</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>N/A</td></tr>"
                "</table>",
                "x": "2021-03-17T04:17:08.174000",
                "y": "459.015"
            } 
        ]

        dhus_availability_data_timeliness_l1_slc = self.driver.execute_script('return dhus_availability_data_timeliness["L1_SLC"].find(element => element.id === "' + str(dhus_product_completeness_l1_slc[0].event_uuid) + '");')
        assert dhus_availability_data_timeliness_l1_slc == timeliness_l1_slc_tooltip_info[0]
        
        # L1_GRD
        # Timeliness statics
        timeliness_average_l1_grd = self.driver.find_element_by_id("summary-dhus-timeliness-average-delta-to-dhus-L1_GRD")

        assert timeliness_average_l1_grd.text == "130.289"

        timeliness_minimum_l1_grd = self.driver.find_element_by_id("summary-dhus-timeliness-minimum-delta-to-dhus-L1_GRD")

        assert timeliness_minimum_l1_grd.text == "94.133"

        timeliness_maximum_l1_grd = self.driver.find_element_by_id("summary-dhus-timeliness-maximum-delta-to-dhus-L1_GRD")

        assert timeliness_maximum_l1_grd.text == "193.798"

        timeliness_std_l1_grd = self.driver.find_element_by_id("summary-dhus-timeliness-std-delta-to-dhus-L1_GRD")

        assert timeliness_std_l1_grd.text == "43.627"
        
        timeliness_l1_grd_tooltip_info = [
            {
                "className": "fill-border-blue",
                "group": "S1A",
                "id": str(dhus_product_completeness_l1_grd[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_GRD</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td>37033.0</td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_grd[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_grd[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>IW</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-blue'>UNEXPECTED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_grd[0].event_uuid) + "'>S1A_IW_GRDH_1SDV_20210317T041620_20210317T041645_037033_045BC0_8316</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>99.662</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.848</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>N/A</td></tr>" +
                "<tr><td>Datatake stop</td><td>N/A</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>N/A</td></tr>"
                "</table>",
                "x": "2021-03-17T04:16:19.501000",
                "y": "99.662"
            } 
        ]

        dhus_availability_data_timeliness_l1_grd = self.driver.execute_script('return dhus_availability_data_timeliness["L1_GRD"].find(element => element.id === "' + str(dhus_product_completeness_l1_grd[0].event_uuid) + '");')
        assert dhus_availability_data_timeliness_l1_grd == timeliness_l1_grd_tooltip_info[0]
        
        # L2_OCN
        # Timeliness statics
        timeliness_average_l2_ocn = self.driver.find_element_by_id("summary-dhus-timeliness-average-delta-to-dhus-L2_OCN")

        assert timeliness_average_l2_ocn.text == "81.261"

        timeliness_minimum_l2_ocn = self.driver.find_element_by_id("summary-dhus-timeliness-minimum-delta-to-dhus-L2_OCN")

        assert timeliness_minimum_l2_ocn.text == "62.759"

        timeliness_maximum_l2_ocn = self.driver.find_element_by_id("summary-dhus-timeliness-maximum-delta-to-dhus-L2_OCN")

        assert timeliness_maximum_l2_ocn.text == "98.023"

        timeliness_std_l2_ocn = self.driver.find_element_by_id("summary-dhus-timeliness-std-delta-to-dhus-L2_OCN")

        assert timeliness_std_l2_ocn.text == "17.260"
        
        timeliness_l2ocn_tooltip_info = [
            {
                "className": "fill-border-blue",
                "group": "S1A",
                "id": str(dhus_product_completeness_l2ocn[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L2_OCN</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td>37033.0</td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l2ocn[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l2ocn[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>IW</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-blue'>UNEXPECTED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l2ocn[0].event_uuid) + "'>S1A_IW_OCN__2SDV_20210317T041645_20210317T041710_037033_045BC0_563F</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>70.536</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.007</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>N/A</td></tr>" +
                "<tr><td>Datatake stop</td><td>N/A</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>N/A</td></tr>"
                "</table>",
                "x": "2021-03-17T04:16:44.501000",
                "y": "70.536"
            } 
        ]

        dhus_availability_data_timeliness_l2_ocn = self.driver.execute_script('return dhus_availability_data_timeliness["L2_OCN"].find(element => element.id === "' + str(dhus_product_completeness_l2ocn[0].event_uuid) + '");')
        assert dhus_availability_data_timeliness_l2_ocn == timeliness_l2ocn_tooltip_info[0]
      
        # Check whether the volumes is displayed
        volume_section = self.driver.find_element_by_id("dhus-availability-volumes-section")

        condition = volume_section.is_displayed()

        assert condition is True

        l0_volume_section = self.driver.find_element_by_id("dhus-availability-volumes-L0")

        condition = l0_volume_section.is_displayed()

        assert condition is True

        l1_slc_volume_section = self.driver.find_element_by_id("dhus-availability-volumes-L1_SLC")

        condition = l1_slc_volume_section.is_displayed()

        assert condition is True

        l1_grd_volume_section = self.driver.find_element_by_id("dhus-availability-volumes-L1_GRD")

        condition = l1_grd_volume_section.is_displayed()

        assert condition is True

        l2_ocn_volume_section = self.driver.find_element_by_id("dhus-availability-volumes-L2_OCN")

        condition = l2_ocn_volume_section.is_displayed()

        assert condition is True

        # L0
        # Volumes statics
        volume_total_l0 = self.driver.find_element_by_id("summary-dhus-volumes-total-L0")

        assert volume_total_l0.text == "7.210"

        volume_average_l0 = self.driver.find_element_by_id("summary-dhus-volumes-average-L0")

        assert volume_average_l0.text == "1.442"

        volume_minimum_l0 = self.driver.find_element_by_id("summary-dhus-volumes-minimum-L0")

        assert volume_minimum_l0.text == "0.418"

        volume_maximum_l0 = self.driver.find_element_by_id("summary-dhus-volumes-maximum-L0")

        assert volume_maximum_l0.text == "1.843"

        volume_std_l0 = self.driver.find_element_by_id("summary-dhus-volumes-std-L0")

        assert volume_std_l0.text == "0.579"


        volume_l0_tooltip_info = [
            {
                "className": "fill-border-blue",
                "group": "S1A",
                "id": str(dhus_product_completeness_l0[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L0</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td>37033.0</td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l0[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l0[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.557</td></tr>" +
                "<tr><td>Imaging mode</td><td>IW</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-blue'>UNEXPECTED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l0[0].event_uuid) + "'>S1A_IW_RAW__0SDV_20210317T041641_20210317T041714_037033_045BC0_11CF</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>48.29</td></tr>" +
                "<tr><td>Size (GB)</td><td>1.664</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>N/A</td></tr>" +
                "<tr><td>Datatake stop</td><td>N/A</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>N/A</td></tr>"
                "</table>",
                "x": "2021-03-17T04:16:40.803000",
                "y": 3.341
            } 
        ]

        dhus_availability_data_volumes_l0 = self.driver.execute_script('return dhus_availability_data_volumes["L0"].find(element => element.id === "' + str(dhus_product_completeness_l0[0].event_uuid) + '");')
        assert dhus_availability_data_volumes_l0 == volume_l0_tooltip_info[0]

        # L1_SLC
        # Volumes statics
        volume_total_l1_slc = self.driver.find_element_by_id("summary-dhus-volumes-total-L1_SLC")

        assert volume_total_l1_slc.text == "18.849"

        volume_average_l1_slc = self.driver.find_element_by_id("summary-dhus-volumes-average-L1_SLC")

        assert volume_average_l1_slc.text == "3.770"

        volume_minimum_l1_slc = self.driver.find_element_by_id("summary-dhus-volumes-minimum-L1_SLC")

        assert volume_minimum_l1_slc.text == "1.196"

        volume_maximum_l1_slc = self.driver.find_element_by_id("summary-dhus-volumes-maximum-L1_SLC")

        assert volume_maximum_l1_slc.text == "5.376"

        volume_std_l1_slc = self.driver.find_element_by_id("summary-dhus-volumes-std-L1_SLC")

        assert volume_std_l1_slc.text == "1.545"
        
        volume_l1_slc_tooltip_info = [
            {
                "className": "fill-border-blue",
                "group": "S1A",
                "id": str(dhus_product_completeness_l1_slc[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_SLC</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td>37033.0</td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_slc[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_slc[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.606</td></tr>" +
                "<tr><td>Imaging mode</td><td>IW</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-blue'>UNEXPECTED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_slc[0].event_uuid) + "'>S1A_IW_SLC__1SDV_20210317T041709_20210317T041744_037033_045BC0_460C</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>459.015</td></tr>" +
                "<tr><td>Size (GB)</td><td>5.376</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>N/A</td></tr>" +
                "<tr><td>Datatake stop</td><td>N/A</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>N/A</td></tr>"
                "</table>",
                "x": "2021-03-17T04:17:08.174000",
                "y": 13.408000000000001
            } 
        ]

        dhus_availability_data_volumes_l1_slc = self.driver.execute_script('return dhus_availability_data_volumes["L1_SLC"].find(element => element.id === "' + str(dhus_product_completeness_l1_slc[0].event_uuid) + '");')
        assert dhus_availability_data_volumes_l1_slc == volume_l1_slc_tooltip_info[0]
        
        # L1_GRD
        # Volumes statics
        volume_total_l1_grd = self.driver.find_element_by_id("summary-dhus-volumes-total-L1_GRD")

        assert volume_total_l1_grd.text == "3.934"

        volume_average_l1_grd = self.driver.find_element_by_id("summary-dhus-volumes-average-L1_GRD")

        assert volume_average_l1_grd.text == "0.656"

        volume_minimum_l1_grd = self.driver.find_element_by_id("summary-dhus-volumes-minimum-L1_GRD")

        assert volume_minimum_l1_grd.text == "0.071"

        volume_maximum_l1_grd = self.driver.find_element_by_id("summary-dhus-volumes-maximum-L1_GRD")

        assert volume_maximum_l1_grd.text == "1.087"

        volume_std_l1_grd = self.driver.find_element_by_id("summary-dhus-volumes-std-L1_GRD")

        assert volume_std_l1_grd.text == "0.403"
        
        volume_l1_grd_tooltip_info = [
            {
                "className": "fill-border-blue",
                "group": "S1A",
                "id": str(dhus_product_completeness_l1_grd[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_GRD</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td>37033.0</td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_grd[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_grd[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>IW</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-blue'>UNEXPECTED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_grd[0].event_uuid) + "'>S1A_IW_GRDH_1SDV_20210317T041620_20210317T041645_037033_045BC0_8316</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>99.662</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.848</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>N/A</td></tr>" +
                "<tr><td>Datatake stop</td><td>N/A</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>N/A</td></tr>"
                "</table>",
                "x": "2021-03-17T04:16:19.501000",
                "y": 1.702
            } 
        ]

        dhus_availability_data_volumes_l1_grd = self.driver.execute_script('return dhus_availability_data_volumes["L1_GRD"].find(element => element.id === "' + str(dhus_product_completeness_l1_grd[0].event_uuid) + '");')
        assert dhus_availability_data_volumes_l1_grd == volume_l1_grd_tooltip_info[0]
        
        # L2_OCN
        # Volumes statics
        volume_total_l2_ocn = self.driver.find_element_by_id("summary-dhus-volumes-total-L2_OCN")

        assert volume_total_l2_ocn.text == "0.029"

        volume_average_l2_ocn = self.driver.find_element_by_id("summary-dhus-volumes-average-L2_OCN")

        assert volume_average_l2_ocn.text == "0.007"

        volume_minimum_l2_ocn = self.driver.find_element_by_id("summary-dhus-volumes-minimum-L2_OCN")

        assert volume_minimum_l2_ocn.text == "0.007"

        volume_maximum_l2_ocn = self.driver.find_element_by_id("summary-dhus-volumes-maximum-L2_OCN")

        assert volume_maximum_l2_ocn.text == "0.008"

        volume_std_l2_ocn = self.driver.find_element_by_id("summary-dhus-volumes-std-L2_OCN")

        assert volume_std_l2_ocn.text == "0.001"
        
        volume_l2ocn_tooltip_info = [
            {
                "className": "fill-border-blue",
                "group": "S1A",
                "id": str(dhus_product_completeness_l2ocn[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L2_OCN</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td>37033.0</td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l2ocn[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l2ocn[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>IW</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-blue'>UNEXPECTED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l2ocn[0].event_uuid) + "'>S1A_IW_OCN__2SDV_20210317T041645_20210317T041710_037033_045BC0_563F</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>70.536</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.007</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>N/A</td></tr>" +
                "<tr><td>Datatake stop</td><td>N/A</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>N/A</td></tr>"
                "</table>",
                "x": "2021-03-17T04:16:44.501000",
                "y": 0.021
            } 
        ]

        dhus_availability_data_volumes_l2_ocn = self.driver.execute_script('return dhus_availability_data_volumes["L2_OCN"].find(element => element.id === "' + str(dhus_product_completeness_l2ocn[0].event_uuid) + '");')
        assert dhus_availability_data_volumes_l2_ocn == volume_l2ocn_tooltip_info[0]

        # Timeline
        timeline_section = self.driver.find_element_by_id("dhus-availability-timeline")

        condition = timeline_section.is_displayed()

        assert condition is True

        dhus_product_completeness_l0 = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:16:15.803000", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:16:49.203000", "op": "=="}])
        
        timeline_l0_tooltip_info = [
            {
                "className": "fill-border-blue",
                "group": "S1A",
                "id": str(dhus_product_completeness_l0[0].event_uuid),
                "start": "2021-03-17T04:16:15.803000",
                "stop": "2021-03-17T04:16:49.203000",
                "timeline": "L0",
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L0</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td>37033.0</td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l0[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l0[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.557</td></tr>" +
                "<tr><td>Imaging mode</td><td>IW</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-blue'>UNEXPECTED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l0[0].event_uuid) + "'>S1A_IW_RAW__0SDV_20210317T041616_20210317T041649_037033_045BC0_9A1C</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>46.06</td></tr>" +
                "<tr><td>Size (GB)</td><td>1.677</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>N/A</td></tr>" +
                "<tr><td>Datatake stop</td><td>N/A</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>N/A</td></tr>"
                "</table>"
            } 
        ]
        
        returned_dhus_availability_data_timeline_l0 = self.driver.execute_script('return dhus_availability_data_timeline.find(element => element.id === "' + str(dhus_product_completeness_l0[0].event_uuid) + '");')
        assert returned_dhus_availability_data_timeline_l0 == timeline_l0_tooltip_info[0]
        
        # Check complete table
        complete_table = self.driver.find_element_by_id("dhus-completeness-list-table-COMPLETE")

        # Row 1
        level = complete_table.find_element_by_xpath("tbody/tr[1]/td[1]")

        assert level.text == "L1_GRD"

        satellite = complete_table.find_element_by_xpath("tbody/tr[1]/td[2]")

        assert satellite.text == "S1A"

        orbit = complete_table.find_element_by_xpath("tbody/tr[1]/td[3]")

        assert orbit.text == "37033.0"

        start = complete_table.find_element_by_xpath("tbody/tr[1]/td[4]")

        assert start.text == "2021-03-17T04:15:54.500000"

        stop = complete_table.find_element_by_xpath("tbody/tr[1]/td[5]")

        assert stop.text == "2021-03-17T04:16:20.500000"

        duration = complete_table.find_element_by_xpath("tbody/tr[1]/td[6]")

        assert duration.text == "0.433"

        imaging_mode = complete_table.find_element_by_xpath("tbody/tr[1]/td[7]")

        assert imaging_mode.text == "IW"

        status = complete_table.find_element_by_xpath("tbody/tr[1]/td[8]")

        assert status.text == "UNEXPECTED"

        product = complete_table.find_element_by_xpath("tbody/tr[1]/td[9]")

        assert product.text == "S1A_IW_GRDH_1SDV_20210317T041555_20210317T041620_037033_045BC0_4630"

        time_dhus_publication = complete_table.find_element_by_xpath("tbody/tr[1]/td[10]")

        assert time_dhus_publication.text == "94.133"

        size = complete_table.find_element_by_xpath("tbody/tr[1]/td[11]")

        assert size.text == "0.854"

        datatake_id = complete_table.find_element_by_xpath("tbody/tr[1]/td[12]")

        assert datatake_id.text == "45BC0"

        start = complete_table.find_element_by_xpath("tbody/tr[1]/td[13]")

        assert start.text == "N/A"

        stop = complete_table.find_element_by_xpath("tbody/tr[1]/td[14]")

        assert stop.text == "N/A"

        datatake_duration = complete_table.find_element_by_xpath("tbody/tr[1]/td[15]")

        assert datatake_duration.text == "N/A"

        # Row 2
        level = complete_table.find_element_by_xpath("tbody/tr[2]/td[1]")

        assert level.text == "L2_OCN"

        satellite = complete_table.find_element_by_xpath("tbody/tr[2]/td[2]")

        assert satellite.text == "S1A"

        orbit = complete_table.find_element_by_xpath("tbody/tr[2]/td[3]")

        assert orbit.text == "37033.0"

        start = complete_table.find_element_by_xpath("tbody/tr[2]/td[4]")

        assert start.text == "2021-03-17T04:15:54.500000"

        stop = complete_table.find_element_by_xpath("tbody/tr[2]/td[5]")

        assert stop.text == "2021-03-17T04:16:20.500000"

        duration = complete_table.find_element_by_xpath("tbody/tr[2]/td[6]")

        assert duration.text == "0.433"

        imaging_mode = complete_table.find_element_by_xpath("tbody/tr[2]/td[7]")

        assert imaging_mode.text == "IW"

        status = complete_table.find_element_by_xpath("tbody/tr[2]/td[8]")

        assert status.text == "UNEXPECTED"

        product = complete_table.find_element_by_xpath("tbody/tr[2]/td[9]")

        assert product.text == "S1A_IW_OCN__2SDV_20210317T041555_20210317T041620_037033_045BC0_015F"

        time_dhus_publication = complete_table.find_element_by_xpath("tbody/tr[2]/td[10]")

        assert time_dhus_publication.text == "62.759"

        size = complete_table.find_element_by_xpath("tbody/tr[2]/td[11]")

        assert size.text == "0.007"

        datatake_id = complete_table.find_element_by_xpath("tbody/tr[2]/td[12]")

        assert datatake_id.text == "45BC0"

        start = complete_table.find_element_by_xpath("tbody/tr[2]/td[13]")

        assert start.text == "N/A"

        stop = complete_table.find_element_by_xpath("tbody/tr[2]/td[14]")

        assert stop.text == "N/A"

        datatake_duration = complete_table.find_element_by_xpath("tbody/tr[2]/td[15]")

        assert datatake_duration.text == "N/A"

        # Row 3
        level = complete_table.find_element_by_xpath("tbody/tr[3]/td[1]")

        assert level.text == "L0"

        satellite = complete_table.find_element_by_xpath("tbody/tr[3]/td[2]")

        assert satellite.text == "S1A"

        orbit = complete_table.find_element_by_xpath("tbody/tr[3]/td[3]")

        assert orbit.text == "37033.0"

        start = complete_table.find_element_by_xpath("tbody/tr[3]/td[4]")

        assert start.text == "2021-03-17T04:16:15.803000"

        stop = complete_table.find_element_by_xpath("tbody/tr[3]/td[5]")

        assert stop.text == "2021-03-17T04:16:49.203000"

        duration = complete_table.find_element_by_xpath("tbody/tr[3]/td[6]")

        assert duration.text == "0.557"

        imaging_mode = complete_table.find_element_by_xpath("tbody/tr[3]/td[7]")

        assert imaging_mode.text == "IW"

        status = complete_table.find_element_by_xpath("tbody/tr[3]/td[8]")

        assert status.text == "UNEXPECTED"

        product = complete_table.find_element_by_xpath("tbody/tr[3]/td[9]")

        assert product.text == "S1A_IW_RAW__0SDV_20210317T041616_20210317T041649_037033_045BC0_9A1C"

        time_dhus_publication = complete_table.find_element_by_xpath("tbody/tr[3]/td[10]")

        assert time_dhus_publication.text == "46.06"

        size = complete_table.find_element_by_xpath("tbody/tr[3]/td[11]")

        assert size.text == "1.677"

        datatake_id = complete_table.find_element_by_xpath("tbody/tr[3]/td[12]")

        assert datatake_id.text == "45BC0"

        start = complete_table.find_element_by_xpath("tbody/tr[3]/td[13]")

        assert start.text == "N/A"

        stop = complete_table.find_element_by_xpath("tbody/tr[3]/td[14]")

        assert stop.text == "N/A"

        datatake_duration = complete_table.find_element_by_xpath("tbody/tr[3]/td[15]")

        assert datatake_duration.text == "N/A"

        # Row 4
        level = complete_table.find_element_by_xpath("tbody/tr[4]/td[1]")

        assert level.text == "L1_SLC"

        satellite = complete_table.find_element_by_xpath("tbody/tr[4]/td[2]")

        assert satellite.text == "S1A"

        orbit = complete_table.find_element_by_xpath("tbody/tr[4]/td[3]")

        assert orbit.text == "37033.0"

        start = complete_table.find_element_by_xpath("tbody/tr[4]/td[4]")

        assert start.text == "2021-03-17T04:16:18.520000"

        stop = complete_table.find_element_by_xpath("tbody/tr[4]/td[5]")

        assert stop.text == "2021-03-17T04:16:46.604000"

        duration = complete_table.find_element_by_xpath("tbody/tr[4]/td[6]")

        assert duration.text == "0.468"

        imaging_mode = complete_table.find_element_by_xpath("tbody/tr[4]/td[7]")

        assert imaging_mode.text == "IW"

        status = complete_table.find_element_by_xpath("tbody/tr[4]/td[8]")

        assert status.text == "UNEXPECTED"

        product = complete_table.find_element_by_xpath("tbody/tr[4]/td[9]")

        assert product.text == "S1A_IW_SLC__1SDV_20210317T041619_20210317T041646_037033_045BC0_B8DB"

        time_dhus_publication = complete_table.find_element_by_xpath("tbody/tr[4]/td[10]")

        assert time_dhus_publication.text == "451.445"

        size = complete_table.find_element_by_xpath("tbody/tr[4]/td[11]")

        assert size.text == "4.052"

        datatake_id = complete_table.find_element_by_xpath("tbody/tr[4]/td[12]")

        assert datatake_id.text == "45BC0"

        start = complete_table.find_element_by_xpath("tbody/tr[4]/td[13]")

        assert start.text == "N/A"

        stop = complete_table.find_element_by_xpath("tbody/tr[4]/td[14]")

        assert stop.text == "N/A"

        datatake_duration = complete_table.find_element_by_xpath("tbody/tr[4]/td[15]")

        assert datatake_duration.text == "N/A"    

    def test_dhus_availability_plan_opdhus(self):

        filename = "S1A_OPER_MPL__NPPF__20210316T160000_20210405T180000_0001_SHORTENED.EOF"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/inputs/" + filename

        exit_status = ingestion.command_process_file("s1boa.ingestions.ingestion_nppf.ingestion_nppf", file_path, "2018-01-01T00:00:00")

        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0

        filename = "DEC_OPER_OPDHUS_S1A_AUIP_20210419T135405_V20210316T000000_20210319T000000_2161_2150_SHORTENED.xml"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/inputs/" + filename

        exit_status = ingestion.command_process_file("s1boa.ingestions.ingestion_dhus_products.ingestion_dhus_products", file_path, "2018-01-01T00:00:00")

        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/views/dhus-availability")

        functions.query(self.driver, wait, "S1_", start = "2021-03-16T00:00:00	", stop = "2021-03-17T23:59:59")

        # Check summary expected duration L0
        summary_expected_l0 = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-available-duration-L0")))

        assert summary_expected_l0

        assert summary_expected_l0.text == "2.472"

        # Check summary expected duration L1_SLC
        summary_expected_l1_slc = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-available-duration-L1_SLC")))

        assert summary_expected_l1_slc

        assert summary_expected_l1_slc.text == "2.221"

        # Check summary expected duration L1_GRD
        summary_expected_l1_grd = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-available-duration-L1_GRD")))

        assert summary_expected_l1_grd

        assert summary_expected_l1_grd.text == "2.562"

       # Check summary expected duration L2_OCN
        summary_expected_l2_ocn = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-available-duration-L2_OCN")))

        assert summary_expected_l2_ocn

        assert summary_expected_l2_ocn.text == "1.884"

        # Summary data pie L0
        data_pie_l0 = [2.472, 0, 0]

        returned_data_pie_l0 = self.driver.execute_script('return completeness.L0.slice(0, 3);')
        assert data_pie_l0 == returned_data_pie_l0

        # Summary data pie L1_SLC
        data_pie_l1_slc = [2.221, 0, 0]

        returned_data_pie_l1_slc = self.driver.execute_script('return completeness.L1_SLC.slice(0, 3);')
        assert data_pie_l1_slc == returned_data_pie_l1_slc

        # Summary data pie L1_GRD
        data_pie_l1_grd = [2.562, 0, 0]

        returned_data_pie_l1_grd = self.driver.execute_script('return completeness.L1_GRD.slice(0, 3);')
        assert data_pie_l1_grd == returned_data_pie_l1_grd

        # Summary data pie L2_OCN
        data_pie_l2_ocn = [1.884, 0, 0]

        returned_data_pie_l2_ocn = self.driver.execute_script('return completeness.L2_OCN.slice(0, 3);')
        assert data_pie_l2_ocn == returned_data_pie_l2_ocn
        
        # Summary data pie volumes
        data_pie_volumes = ["7.210", "18.849", "3.934", "0.029"]

        returned_data_pie_volumes = self.driver.execute_script('return data_pie_volumes.datasets[0].data.slice(0, 4);')
        assert data_pie_volumes == returned_data_pie_volumes

        # Check whether the map is displayed
        map_section = self.driver.find_element_by_id("dhus-availability-maps-section")

        condition = map_section.is_displayed()

        assert condition is True

        l0_map_section = self.driver.find_element_by_id("dhus-availability-map-L0-section")

        condition = l0_map_section.is_displayed()

        assert condition is True

        l1_slc_map_section = self.driver.find_element_by_id("dhus-availability-map-L1_SLC-section")

        condition = l1_slc_map_section.is_displayed()

        assert condition is True

        l1_grd_map_section = self.driver.find_element_by_id("dhus-availability-map-L1_GRD-section")

        condition = l1_grd_map_section.is_displayed()

        assert condition is True

        l2_ocn_map_section = self.driver.find_element_by_id("dhus-availability-map-L2_OCN-section")

        condition = l2_ocn_map_section.is_displayed()

        assert condition is True

        planned_imaging = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:10:33.066685", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:17:48.873819", "op": "=="}])

        dhus_product_completeness_l0 = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:16:40.803000", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:17:14.203000", "op": "=="}])
        
        map_l0_tooltip_info = [
            {
                "id": str(dhus_product_completeness_l0[0].event_uuid),
                "geometries": [{
                    "name": "footprint",
                    "type": "geometry",
                    "value": "POLYGON ((27.694101 34.295553, 27.642358 34.072066, 27.590754 33.848562, 27.539292 33.625041, 27.487971 33.401505, 27.436734 33.177954, 27.385626 32.954387, 27.334653 32.730805, 27.283811 32.507207, 27.233047 32.283595, 24.594085 32.684286, 24.638196 32.907564, 24.682299 33.130832, 24.726466 33.354088, 24.770698 33.577332, 24.814987 33.800564, 24.859272 34.023786, 24.903625 34.246996, 24.948049 34.470194, 24.992536 34.693379, 27.694101 34.295553))"
                }],
                "style": {"stroke_color": "green", "fill_color": "rgba(0,255,0,0.3)"},
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L0</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l0[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l0[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.557</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l0[0].event_uuid) + "'>S1A_IW_RAW__0SDV_20210317T041641_20210317T041714_037033_045BC0_11CF</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>47.712</td></tr>" +
                "<tr><td>Size (GB)</td><td>1.664</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>"
            } 
        ]

        dhus_availability_data_maps_l0 = self.driver.execute_script('return dhus_availability_data_maps["L0"].find(element => element.id === "' + str(dhus_product_completeness_l0[0].event_uuid) + '");')
        assert dhus_availability_data_maps_l0 == map_l0_tooltip_info[0]
        
        dhus_product_completeness_l1_slc = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:17:08.174000", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:17:44.528000", "op": "=="}])

        map_l1_slc_tooltip_info = [
            {
                "id": str(dhus_product_completeness_l1_slc[0].event_uuid),
                "geometries": [{
                    "name": "footprint",
                    "type": "geometry",
                    "value": "POLYGON ((27.315539 32.646864, 27.26576 32.427823, 27.216108 32.208767, 27.166526 31.989698, 27.117058 31.770614, 27.067712 31.551516, 27.01848 31.332403, 26.969309 31.113278, 26.920253 30.894139, 26.871312 30.674986, 26.822465 30.455819, 24.235282 30.859376, 24.278161 31.078187, 24.321068 31.296987, 24.36403 31.515777, 24.407047 31.734556, 24.450046 31.953326, 24.493096 32.172085, 24.536205 32.390833, 24.579363 32.60957, 24.62251 32.828298, 24.665719 33.047014, 27.315539 32.646864))"
                }],
                "style": {"stroke_color": "green", "fill_color": "rgba(0,255,0,0.3)"},
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_SLC</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_slc[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_slc[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.606</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_slc[0].event_uuid) + "'>S1A_IW_SLC__1SDV_20210317T041709_20210317T041744_037033_045BC0_460C</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>458.943</td></tr>" +
                "<tr><td>Size (GB)</td><td>5.376</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>"
            } 
        ]

        dhus_availability_data_maps_l1_slc = self.driver.execute_script('return dhus_availability_data_maps["L1_SLC"].find(element => element.id === "' + str(dhus_product_completeness_l1_slc[0].event_uuid) + '");')
        assert dhus_availability_data_maps_l1_slc == map_l1_slc_tooltip_info[0]
        
        dhus_product_completeness_l1_grd = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:16:19.501000", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:16:45.499000", "op": "=="}])

        map_l1_grd_tooltip_info = [
            {
                "id": str(dhus_product_completeness_l1_grd[0].event_uuid),
                "geometries": [{
                    "name": "footprint",
                    "type": "geometry",
                    "value": "POLYGON ((27.993583 35.578075, 27.941029 35.354507, 27.888633 35.130922, 27.836385 34.90732, 27.784233 34.683703, 27.732234 34.460069, 27.680383 34.236418, 27.628672 34.012751, 24.936282 34.41096, 24.980741 34.634324, 25.025264 34.857675, 25.069861 35.081014, 25.114533 35.304341, 25.15921 35.527656, 25.203953 35.750959, 25.248777 35.97425, 27.993583 35.578075))"
                }],
                "style": {"stroke_color": "green", "fill_color": "rgba(0,255,0,0.3)"},
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_GRD</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_grd[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_grd[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_grd[0].event_uuid) + "'>S1A_IW_GRDH_1SDV_20210317T041620_20210317T041645_037033_045BC0_8316</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>98.605</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.848</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>"
            } 
        ]

        dhus_availability_data_maps_l1_grd = self.driver.execute_script('return dhus_availability_data_maps["L1_GRD"].find(element => element.id === "' + str(dhus_product_completeness_l1_grd[0].event_uuid) + '");')
        assert dhus_availability_data_maps_l1_grd == map_l1_grd_tooltip_info[0]
        
        dhus_product_completeness_l2ocn = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L2_OCN", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:16:44.501000", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:17:10.499000", "op": "=="}])
        
        map_l2ocn_tooltip_info = [
            {
                "id": str(dhus_product_completeness_l2ocn[0].event_uuid),
                "geometries": [{
                    "name": "footprint",
                    "type": "geometry",
                    "value": "POLYGON ((27.64254 34.072855, 27.590896 33.849177, 27.539394 33.625483, 27.488033 33.401772, 27.436755 33.178048, 27.385608 32.954307, 27.334595 32.730551, 27.283714 32.506778, 24.638111 32.907136, 24.682249 33.130578, 24.72645 33.354008, 24.770716 33.577425, 24.81504 33.800832, 24.85936 34.024227, 24.903747 34.247611, 24.948206 34.470982, 27.64254 34.072855))"
                }],
                "style": {"stroke_color": "green", "fill_color": "rgba(0,255,0,0.3)"},
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L2_OCN</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l2ocn[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l2ocn[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l2ocn[0].event_uuid) + "'>S1A_IW_OCN__2SDV_20210317T041645_20210317T041710_037033_045BC0_563F</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>69.896</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.007</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>"
            } 
        ]

        dhus_availability_data_maps_l2_ocn = self.driver.execute_script('return dhus_availability_data_maps["L2_OCN"].find(element => element.id === "' + str(dhus_product_completeness_l2ocn[0].event_uuid) + '");')
        assert dhus_availability_data_maps_l2_ocn == map_l2ocn_tooltip_info[0]

        # Check whether the timeliness is displayed
        timeliness_section = self.driver.find_element_by_id("dhus-availability-timeliness-section")

        condition = timeliness_section.is_displayed()

        assert condition is True

        l0_timeliness_section = self.driver.find_element_by_id("dhus-availability-timeliness-L0")

        condition = l0_timeliness_section.is_displayed()

        assert condition is True

        l1_slc_timeliness_section = self.driver.find_element_by_id("dhus-availability-timeliness-L1_SLC")

        condition = l1_slc_timeliness_section.is_displayed()

        assert condition is True

        l1_grd_timeliness_section = self.driver.find_element_by_id("dhus-availability-timeliness-L1_GRD")

        condition = l1_grd_timeliness_section.is_displayed()

        assert condition is True

        l2_ocn_timeliness_section = self.driver.find_element_by_id("dhus-availability-timeliness-L2_OCN")

        condition = l2_ocn_timeliness_section.is_displayed()

        assert condition is True

        # L0
        # Timeliness statics
        timeliness_average_l0 = self.driver.find_element_by_id("summary-dhus-timeliness-average-delta-to-dhus-L0")

        assert timeliness_average_l0.text == "90.127"

        timeliness_minimum_l0 = self.driver.find_element_by_id("summary-dhus-timeliness-minimum-delta-to-dhus-L0")

        assert timeliness_minimum_l0.text == "45.065"

        timeliness_maximum_l0 = self.driver.find_element_by_id("summary-dhus-timeliness-maximum-delta-to-dhus-L0")

        assert timeliness_maximum_l0.text == "169.128"

        timeliness_std_l0 = self.driver.find_element_by_id("summary-dhus-timeliness-std-delta-to-dhus-L0")

        assert timeliness_std_l0.text == "61.160"

        timeliness_l0_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l0[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L0</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l0[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l0[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.557</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l0[0].event_uuid) + "'>S1A_IW_RAW__0SDV_20210317T041641_20210317T041714_037033_045BC0_11CF</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>47.712</td></tr>" +
                "<tr><td>Size (GB)</td><td>1.664</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>",
                "x": "2021-03-17T04:16:40.803000",
                "y": "47.712"
            } 
        ]

        dhus_availability_data_timeliness_l0 = self.driver.execute_script('return dhus_availability_data_timeliness["L0"].find(element => element.id === "' + str(dhus_product_completeness_l0[0].event_uuid) + '");')
        assert dhus_availability_data_timeliness_l0 == timeliness_l0_tooltip_info[0]

        # L1_SLC
        # Timeliness statics
        timeliness_average_l1_slc = self.driver.find_element_by_id("summary-dhus-timeliness-average-delta-to-dhus-L1_SLC")

        assert timeliness_average_l1_slc.text == "397.082"

        timeliness_minimum_l1_slc = self.driver.find_element_by_id("summary-dhus-timeliness-minimum-delta-to-dhus-L1_SLC")

        assert timeliness_minimum_l1_slc.text == "303.489"

        timeliness_maximum_l1_slc = self.driver.find_element_by_id("summary-dhus-timeliness-maximum-delta-to-dhus-L1_SLC")

        assert timeliness_maximum_l1_slc.text == "458.943"

        timeliness_std_l1_slc = self.driver.find_element_by_id("summary-dhus-timeliness-std-delta-to-dhus-L1_SLC")

        assert timeliness_std_l1_slc.text == "63.242"
        
        timeliness_l1_slc_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l1_slc[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_SLC</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_slc[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_slc[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.606</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_slc[0].event_uuid) + "'>S1A_IW_SLC__1SDV_20210317T041709_20210317T041744_037033_045BC0_460C</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>458.943</td></tr>" +
                "<tr><td>Size (GB)</td><td>5.376</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>",
                "x": "2021-03-17T04:17:08.174000",
                "y": "458.943"
            } 
        ]

        dhus_availability_data_timeliness_l1_slc = self.driver.execute_script('return dhus_availability_data_timeliness["L1_SLC"].find(element => element.id === "' + str(dhus_product_completeness_l1_slc[0].event_uuid) + '");')
        assert dhus_availability_data_timeliness_l1_slc == timeliness_l1_slc_tooltip_info[0]
        
        # L1_GRD
        # Timeliness statics
        timeliness_average_l1_grd = self.driver.find_element_by_id("summary-dhus-timeliness-average-delta-to-dhus-L1_GRD")

        assert timeliness_average_l1_grd.text == "129.716"

        timeliness_minimum_l1_grd = self.driver.find_element_by_id("summary-dhus-timeliness-minimum-delta-to-dhus-L1_GRD")

        assert timeliness_minimum_l1_grd.text == "92.660"

        timeliness_maximum_l1_grd = self.driver.find_element_by_id("summary-dhus-timeliness-maximum-delta-to-dhus-L1_GRD")

        assert timeliness_maximum_l1_grd.text == "193.702"

        timeliness_std_l1_grd = self.driver.find_element_by_id("summary-dhus-timeliness-std-delta-to-dhus-L1_GRD")

        assert timeliness_std_l1_grd.text == "44.076"
        
        timeliness_l1_grd_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l1_grd[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_GRD</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_grd[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_grd[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_grd[0].event_uuid) + "'>S1A_IW_GRDH_1SDV_20210317T041620_20210317T041645_037033_045BC0_8316</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>98.605</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.848</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>",
                "x": "2021-03-17T04:16:19.501000",
                "y": "98.605"
            } 
        ]

        dhus_availability_data_timeliness_l1_grd = self.driver.execute_script('return dhus_availability_data_timeliness["L1_GRD"].find(element => element.id === "' + str(dhus_product_completeness_l1_grd[0].event_uuid) + '");')
        assert dhus_availability_data_timeliness_l1_grd == timeliness_l1_grd_tooltip_info[0]
        
        # L2_OCN
        # Timeliness statics
        timeliness_average_l2_ocn = self.driver.find_element_by_id("summary-dhus-timeliness-average-delta-to-dhus-L2_OCN")

        assert timeliness_average_l2_ocn.text == "80.450"

        timeliness_minimum_l2_ocn = self.driver.find_element_by_id("summary-dhus-timeliness-minimum-delta-to-dhus-L2_OCN")

        assert timeliness_minimum_l2_ocn.text == "61.287"

        timeliness_maximum_l2_ocn = self.driver.find_element_by_id("summary-dhus-timeliness-maximum-delta-to-dhus-L2_OCN")

        assert timeliness_maximum_l2_ocn.text == "97.950"

        timeliness_std_l2_ocn = self.driver.find_element_by_id("summary-dhus-timeliness-std-delta-to-dhus-L2_OCN")

        assert timeliness_std_l2_ocn.text == "17.646"
        
        timeliness_l2ocn_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l2ocn[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L2_OCN</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l2ocn[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l2ocn[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l2ocn[0].event_uuid) + "'>S1A_IW_OCN__2SDV_20210317T041645_20210317T041710_037033_045BC0_563F</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>69.896</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.007</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>",
                "x": "2021-03-17T04:16:44.501000",
                "y": "69.896"
            } 
        ]

        dhus_availability_data_timeliness_l2_ocn = self.driver.execute_script('return dhus_availability_data_timeliness["L2_OCN"].find(element => element.id === "' + str(dhus_product_completeness_l2ocn[0].event_uuid) + '");')
        assert dhus_availability_data_timeliness_l2_ocn == timeliness_l2ocn_tooltip_info[0]
      
        # Check whether the volumes is displayed
        volume_section = self.driver.find_element_by_id("dhus-availability-volumes-section")

        condition = volume_section.is_displayed()

        assert condition is True

        l0_volume_section = self.driver.find_element_by_id("dhus-availability-volumes-L0")

        condition = l0_volume_section.is_displayed()

        assert condition is True

        l1_slc_volume_section = self.driver.find_element_by_id("dhus-availability-volumes-L1_SLC")

        condition = l1_slc_volume_section.is_displayed()

        assert condition is True

        l1_grd_volume_section = self.driver.find_element_by_id("dhus-availability-volumes-L1_GRD")

        condition = l1_grd_volume_section.is_displayed()

        assert condition is True

        l2_ocn_volume_section = self.driver.find_element_by_id("dhus-availability-volumes-L2_OCN")

        condition = l2_ocn_volume_section.is_displayed()

        assert condition is True

        # L0
        # Volumes statics
        volume_total_l0 = self.driver.find_element_by_id("summary-dhus-volumes-total-L0")

        assert volume_total_l0.text == "7.210"

        volume_average_l0 = self.driver.find_element_by_id("summary-dhus-volumes-average-L0")

        assert volume_average_l0.text == "1.442"

        volume_minimum_l0 = self.driver.find_element_by_id("summary-dhus-volumes-minimum-L0")

        assert volume_minimum_l0.text == "0.418"

        volume_maximum_l0 = self.driver.find_element_by_id("summary-dhus-volumes-maximum-L0")

        assert volume_maximum_l0.text == "1.843"

        volume_std_l0 = self.driver.find_element_by_id("summary-dhus-volumes-std-L0")

        assert volume_std_l0.text == "0.579"


        volume_l0_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l0[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L0</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l0[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l0[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.557</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l0[0].event_uuid) + "'>S1A_IW_RAW__0SDV_20210317T041641_20210317T041714_037033_045BC0_11CF</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>47.712</td></tr>" +
                "<tr><td>Size (GB)</td><td>1.664</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>",
                "x": "2021-03-17T04:16:40.803000",
                "y": 3.341
            } 
        ]

        dhus_availability_data_volumes_l0 = self.driver.execute_script('return dhus_availability_data_volumes["L0"].find(element => element.id === "' + str(dhus_product_completeness_l0[0].event_uuid) + '");')
        assert dhus_availability_data_volumes_l0 == volume_l0_tooltip_info[0]

        # L1_SLC
        # Volumes statics
        volume_total_l1_slc = self.driver.find_element_by_id("summary-dhus-volumes-total-L1_SLC")

        assert volume_total_l1_slc.text == "18.849"

        volume_average_l1_slc = self.driver.find_element_by_id("summary-dhus-volumes-average-L1_SLC")

        assert volume_average_l1_slc.text == "3.770"

        volume_minimum_l1_slc = self.driver.find_element_by_id("summary-dhus-volumes-minimum-L1_SLC")

        assert volume_minimum_l1_slc.text == "1.196"

        volume_maximum_l1_slc = self.driver.find_element_by_id("summary-dhus-volumes-maximum-L1_SLC")

        assert volume_maximum_l1_slc.text == "5.376"

        volume_std_l1_slc = self.driver.find_element_by_id("summary-dhus-volumes-std-L1_SLC")

        assert volume_std_l1_slc.text == "1.545"
        
        volume_l1_slc_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l1_slc[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_SLC</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_slc[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_slc[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.606</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_slc[0].event_uuid) + "'>S1A_IW_SLC__1SDV_20210317T041709_20210317T041744_037033_045BC0_460C</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>458.943</td></tr>" +
                "<tr><td>Size (GB)</td><td>5.376</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>",
                "x": "2021-03-17T04:17:08.174000",
                "y": 13.408000000000001
            } 
        ]

        dhus_availability_data_volumes_l1_slc = self.driver.execute_script('return dhus_availability_data_volumes["L1_SLC"].find(element => element.id === "' + str(dhus_product_completeness_l1_slc[0].event_uuid) + '");')
        assert dhus_availability_data_volumes_l1_slc == volume_l1_slc_tooltip_info[0]
        
        # L1_GRD
        # Volumes statics
        volume_total_l1_grd = self.driver.find_element_by_id("summary-dhus-volumes-total-L1_GRD")

        assert volume_total_l1_grd.text == "3.934"

        volume_average_l1_grd = self.driver.find_element_by_id("summary-dhus-volumes-average-L1_GRD")

        assert volume_average_l1_grd.text == "0.656"

        volume_minimum_l1_grd = self.driver.find_element_by_id("summary-dhus-volumes-minimum-L1_GRD")

        assert volume_minimum_l1_grd.text == "0.071"

        volume_maximum_l1_grd = self.driver.find_element_by_id("summary-dhus-volumes-maximum-L1_GRD")

        assert volume_maximum_l1_grd.text == "1.087"

        volume_std_l1_grd = self.driver.find_element_by_id("summary-dhus-volumes-std-L1_GRD")

        assert volume_std_l1_grd.text == "0.403"
        
        volume_l1_grd_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l1_grd[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_GRD</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_grd[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_grd[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_grd[0].event_uuid) + "'>S1A_IW_GRDH_1SDV_20210317T041620_20210317T041645_037033_045BC0_8316</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>98.605</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.848</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>",
                "x": "2021-03-17T04:16:19.501000",
                "y": 1.702
            } 
        ]

        dhus_availability_data_volumes_l1_grd = self.driver.execute_script('return dhus_availability_data_volumes["L1_GRD"].find(element => element.id === "' + str(dhus_product_completeness_l1_grd[0].event_uuid) + '");')
        assert dhus_availability_data_volumes_l1_grd == volume_l1_grd_tooltip_info[0]
        
        # L2_OCN
        # Volumes statics
        volume_total_l2_ocn = self.driver.find_element_by_id("summary-dhus-volumes-total-L2_OCN")

        assert volume_total_l2_ocn.text == "0.029"

        volume_average_l2_ocn = self.driver.find_element_by_id("summary-dhus-volumes-average-L2_OCN")

        assert volume_average_l2_ocn.text == "0.007"

        volume_minimum_l2_ocn = self.driver.find_element_by_id("summary-dhus-volumes-minimum-L2_OCN")

        assert volume_minimum_l2_ocn.text == "0.007"

        volume_maximum_l2_ocn = self.driver.find_element_by_id("summary-dhus-volumes-maximum-L2_OCN")

        assert volume_maximum_l2_ocn.text == "0.008"

        volume_std_l2_ocn = self.driver.find_element_by_id("summary-dhus-volumes-std-L2_OCN")

        assert volume_std_l2_ocn.text == "0.001"
        
        volume_l2ocn_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l2ocn[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L2_OCN</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l2ocn[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l2ocn[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l2ocn[0].event_uuid) + "'>S1A_IW_OCN__2SDV_20210317T041645_20210317T041710_037033_045BC0_563F</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>69.896</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.007</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>",
                "x": "2021-03-17T04:16:44.501000",
                "y": 0.021
            } 
        ]

        dhus_availability_data_volumes_l2_ocn = self.driver.execute_script('return dhus_availability_data_volumes["L2_OCN"].find(element => element.id === "' + str(dhus_product_completeness_l2ocn[0].event_uuid) + '");')
        assert dhus_availability_data_volumes_l2_ocn == volume_l2ocn_tooltip_info[0]

        # Timeline
        timeline_section = self.driver.find_element_by_id("dhus-availability-timeline")

        condition = timeline_section.is_displayed()

        assert condition is True

        dhus_product_completeness_l0 = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:16:15.803000", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:16:49.203000", "op": "=="}])
        
        timeline_l0_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l0[0].event_uuid),
                "start": "2021-03-17T04:16:15.803000",
                "stop": "2021-03-17T04:16:49.203000",
                "timeline": "L0",
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L0</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l0[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l0[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.557</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l0[0].event_uuid) + "'>S1A_IW_RAW__0SDV_20210317T041616_20210317T041649_037033_045BC0_9A1C</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>45.065</td></tr>" +
                "<tr><td>Size (GB)</td><td>1.677</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>"
            } 
        ]
        
        returned_dhus_availability_data_timeline_l0 = self.driver.execute_script('return dhus_availability_data_timeline.find(element => element.id === "' + str(dhus_product_completeness_l0[0].event_uuid) + '");')
        assert returned_dhus_availability_data_timeline_l0 == timeline_l0_tooltip_info[0]
        
        # Check complete table
        complete_table = self.driver.find_element_by_id("dhus-completeness-list-table-COMPLETE")

        # Row 1
        level = complete_table.find_element_by_xpath("tbody/tr[1]/td[1]")

        assert level.text == "L1_GRD"

        satellite = complete_table.find_element_by_xpath("tbody/tr[1]/td[2]")

        assert satellite.text == "S1A"

        orbit = complete_table.find_element_by_xpath("tbody/tr[1]/td[3]")

        assert orbit.text == "37033.0"

        start = complete_table.find_element_by_xpath("tbody/tr[1]/td[4]")

        assert start.text == "2021-03-17T04:15:54.500000"

        stop = complete_table.find_element_by_xpath("tbody/tr[1]/td[5]")

        assert stop.text == "2021-03-17T04:16:20.500000"

        duration = complete_table.find_element_by_xpath("tbody/tr[1]/td[6]")

        assert duration.text == "0.433"

        imaging_mode = complete_table.find_element_by_xpath("tbody/tr[1]/td[7]")

        assert imaging_mode.text == "INTERFEROMETRIC_WIDE_SWATH"

        status = complete_table.find_element_by_xpath("tbody/tr[1]/td[8]")

        assert status.text == "PUBLISHED"

        product = complete_table.find_element_by_xpath("tbody/tr[1]/td[9]")

        assert product.text == "S1A_IW_GRDH_1SDV_20210317T041555_20210317T041620_037033_045BC0_4630"

        time_dhus_publication = complete_table.find_element_by_xpath("tbody/tr[1]/td[10]")

        assert time_dhus_publication.text == "92.66"

        size = complete_table.find_element_by_xpath("tbody/tr[1]/td[11]")

        assert size.text == "0.854"

        datatake_id = complete_table.find_element_by_xpath("tbody/tr[1]/td[12]")

        assert datatake_id.text == "45BC0"

        start = complete_table.find_element_by_xpath("tbody/tr[1]/td[13]")

        assert start.text == "2021-03-17T04:10:33.066685"

        stop = complete_table.find_element_by_xpath("tbody/tr[1]/td[14]")

        assert stop.text == "2021-03-17T04:17:48.873819"

        datatake_duration = complete_table.find_element_by_xpath("tbody/tr[1]/td[15]")

        assert datatake_duration.text == "7.263"

        # Row 2
        level = complete_table.find_element_by_xpath("tbody/tr[2]/td[1]")

        assert level.text == "L2_OCN"

        satellite = complete_table.find_element_by_xpath("tbody/tr[2]/td[2]")

        assert satellite.text == "S1A"

        orbit = complete_table.find_element_by_xpath("tbody/tr[2]/td[3]")

        assert orbit.text == "37033.0"

        start = complete_table.find_element_by_xpath("tbody/tr[2]/td[4]")

        assert start.text == "2021-03-17T04:15:54.500000"

        stop = complete_table.find_element_by_xpath("tbody/tr[2]/td[5]")

        assert stop.text == "2021-03-17T04:16:20.500000"

        duration = complete_table.find_element_by_xpath("tbody/tr[2]/td[6]")

        assert duration.text == "0.433"

        imaging_mode = complete_table.find_element_by_xpath("tbody/tr[2]/td[7]")

        assert imaging_mode.text == "INTERFEROMETRIC_WIDE_SWATH"

        status = complete_table.find_element_by_xpath("tbody/tr[2]/td[8]")

        assert status.text == "PUBLISHED"

        product = complete_table.find_element_by_xpath("tbody/tr[2]/td[9]")

        assert product.text == "S1A_IW_OCN__2SDV_20210317T041555_20210317T041620_037033_045BC0_015F"

        time_dhus_publication = complete_table.find_element_by_xpath("tbody/tr[2]/td[10]")

        assert time_dhus_publication.text == "61.287"

        size = complete_table.find_element_by_xpath("tbody/tr[2]/td[11]")

        assert size.text == "0.007"

        datatake_id = complete_table.find_element_by_xpath("tbody/tr[2]/td[12]")

        assert datatake_id.text == "45BC0"

        start = complete_table.find_element_by_xpath("tbody/tr[2]/td[13]")

        assert start.text == "2021-03-17T04:10:33.066685"

        stop = complete_table.find_element_by_xpath("tbody/tr[2]/td[14]")

        assert stop.text == "2021-03-17T04:17:48.873819"

        datatake_duration = complete_table.find_element_by_xpath("tbody/tr[2]/td[15]")

        assert datatake_duration.text == "7.263"

        # Row 3
        level = complete_table.find_element_by_xpath("tbody/tr[3]/td[1]")

        assert level.text == "L0"

        satellite = complete_table.find_element_by_xpath("tbody/tr[3]/td[2]")

        assert satellite.text == "S1A"

        orbit = complete_table.find_element_by_xpath("tbody/tr[3]/td[3]")

        assert orbit.text == "37033.0"

        start = complete_table.find_element_by_xpath("tbody/tr[3]/td[4]")

        assert start.text == "2021-03-17T04:16:15.803000"

        stop = complete_table.find_element_by_xpath("tbody/tr[3]/td[5]")

        assert stop.text == "2021-03-17T04:16:49.203000"

        duration = complete_table.find_element_by_xpath("tbody/tr[3]/td[6]")

        assert duration.text == "0.557"

        imaging_mode = complete_table.find_element_by_xpath("tbody/tr[3]/td[7]")

        assert imaging_mode.text == "INTERFEROMETRIC_WIDE_SWATH"

        status = complete_table.find_element_by_xpath("tbody/tr[3]/td[8]")

        assert status.text == "PUBLISHED"

        product = complete_table.find_element_by_xpath("tbody/tr[3]/td[9]")

        assert product.text == "S1A_IW_RAW__0SDV_20210317T041616_20210317T041649_037033_045BC0_9A1C"

        time_dhus_publication = complete_table.find_element_by_xpath("tbody/tr[3]/td[10]")

        assert time_dhus_publication.text == "45.065"

        size = complete_table.find_element_by_xpath("tbody/tr[3]/td[11]")

        assert size.text == "1.677"

        datatake_id = complete_table.find_element_by_xpath("tbody/tr[3]/td[12]")

        assert datatake_id.text == "45BC0"

        start = complete_table.find_element_by_xpath("tbody/tr[3]/td[13]")

        assert start.text == "2021-03-17T04:10:33.066685"

        stop = complete_table.find_element_by_xpath("tbody/tr[3]/td[14]")

        assert stop.text == "2021-03-17T04:17:48.873819"

        datatake_duration = complete_table.find_element_by_xpath("tbody/tr[3]/td[15]")

        assert datatake_duration.text == "7.263"

        # Row 4
        level = complete_table.find_element_by_xpath("tbody/tr[4]/td[1]")

        assert level.text == "L1_SLC"

        satellite = complete_table.find_element_by_xpath("tbody/tr[4]/td[2]")

        assert satellite.text == "S1A"

        orbit = complete_table.find_element_by_xpath("tbody/tr[4]/td[3]")

        assert orbit.text == "37033.0"

        start = complete_table.find_element_by_xpath("tbody/tr[4]/td[4]")

        assert start.text == "2021-03-17T04:16:18.520000"

        stop = complete_table.find_element_by_xpath("tbody/tr[4]/td[5]")

        assert stop.text == "2021-03-17T04:16:46.604000"

        duration = complete_table.find_element_by_xpath("tbody/tr[4]/td[6]")

        assert duration.text == "0.468"

        imaging_mode = complete_table.find_element_by_xpath("tbody/tr[4]/td[7]")

        assert imaging_mode.text == "INTERFEROMETRIC_WIDE_SWATH"

        status = complete_table.find_element_by_xpath("tbody/tr[4]/td[8]")

        assert status.text == "PUBLISHED"

        product = complete_table.find_element_by_xpath("tbody/tr[4]/td[9]")

        assert product.text == "S1A_IW_SLC__1SDV_20210317T041619_20210317T041646_037033_045BC0_B8DB"

        time_dhus_publication = complete_table.find_element_by_xpath("tbody/tr[4]/td[10]")

        assert time_dhus_publication.text == "450.408"

        size = complete_table.find_element_by_xpath("tbody/tr[4]/td[11]")

        assert size.text == "4.052"

        datatake_id = complete_table.find_element_by_xpath("tbody/tr[4]/td[12]")

        assert datatake_id.text == "45BC0"

        start = complete_table.find_element_by_xpath("tbody/tr[4]/td[13]")

        assert start.text == "2021-03-17T04:10:33.066685"

        stop = complete_table.find_element_by_xpath("tbody/tr[4]/td[14]")

        assert stop.text == "2021-03-17T04:17:48.873819"

        datatake_duration = complete_table.find_element_by_xpath("tbody/tr[4]/td[15]")

        assert datatake_duration.text == "7.263"

    def test_dhus_availability_plan_opdhus_per_level(self):

        filename = "S1A_OPER_MPL__NPPF__20210316T160000_20210405T180000_0001_SHORTENED.EOF"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/inputs/" + filename

        exit_status = ingestion.command_process_file("s1boa.ingestions.ingestion_nppf.ingestion_nppf", file_path, "2018-01-01T00:00:00")

        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0

        filename = "DEC_OPER_OPDHUS_S1A_AUIP_20210419T135405_V20210316T000000_20210319T000000_2161_2150_SHORTENED.xml"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/inputs/" + filename

        exit_status = ingestion.command_process_file("s1boa.ingestions.ingestion_dhus_products.ingestion_dhus_products", file_path, "2018-01-01T00:00:00")

        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/views/dhus-availability")

        ### Level L0
        functions.query(self.driver, wait, "S1_", "L0", start = "2021-03-16T00:00:00", stop = "2021-03-17T23:59:59")

        # Check summary expected duration L0
        summary_expected_l0 = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-available-duration-L0")))

        assert summary_expected_l0

        assert summary_expected_l0.text == "2.472"

        # Summary data pie L0
        data_pie_l0 = [2.472, 0, 0]

        returned_data_pie_l0 = self.driver.execute_script('return completeness.L0.slice(0, 3);')
        assert data_pie_l0 == returned_data_pie_l0
        
        # Summary data pie volumes
        data_pie_volumes = ["7.210"]

        returned_data_pie_volumes = self.driver.execute_script('return data_pie_volumes.datasets[0].data.slice(0, 4);')
        assert data_pie_volumes == returned_data_pie_volumes
        
        # Check whether the map is displayed
        map_section = self.driver.find_element_by_id("dhus-availability-maps-section")

        condition = map_section.is_displayed()

        assert condition is True

        l0_map_section = self.driver.find_element_by_id("dhus-availability-map-L0-section")

        condition = l0_map_section.is_displayed()

        assert condition is True

        planned_imaging = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:10:33.066685", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:17:48.873819", "op": "=="}])

        dhus_product_completeness_l0 = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:16:40.803000", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:17:14.203000", "op": "=="}])
        
        map_l0_tooltip_info = [
            {
                "id": str(dhus_product_completeness_l0[0].event_uuid),
                "geometries": [{
                    "name": "footprint",
                    "type": "geometry",
                    "value": "POLYGON ((27.694101 34.295553, 27.642358 34.072066, 27.590754 33.848562, 27.539292 33.625041, 27.487971 33.401505, 27.436734 33.177954, 27.385626 32.954387, 27.334653 32.730805, 27.283811 32.507207, 27.233047 32.283595, 24.594085 32.684286, 24.638196 32.907564, 24.682299 33.130832, 24.726466 33.354088, 24.770698 33.577332, 24.814987 33.800564, 24.859272 34.023786, 24.903625 34.246996, 24.948049 34.470194, 24.992536 34.693379, 27.694101 34.295553))"
                }],
                "style": {"stroke_color": "green", "fill_color": "rgba(0,255,0,0.3)"},
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L0</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l0[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l0[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.557</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l0[0].event_uuid) + "'>S1A_IW_RAW__0SDV_20210317T041641_20210317T041714_037033_045BC0_11CF</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>47.712</td></tr>" +
                "<tr><td>Size (GB)</td><td>1.664</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>"
            } 
        ]

        dhus_availability_data_maps_l0 = self.driver.execute_script('return dhus_availability_data_maps["L0"].find(element => element.id === "' + str(dhus_product_completeness_l0[0].event_uuid) + '");')
        assert dhus_availability_data_maps_l0 == map_l0_tooltip_info[0]
        
        # Check whether the timeliness is displayed
        timeliness_section = self.driver.find_element_by_id("dhus-availability-timeliness-section")

        condition = timeliness_section.is_displayed()

        assert condition is True

        l0_timeliness_section = self.driver.find_element_by_id("dhus-availability-timeliness-L0")

        condition = l0_timeliness_section.is_displayed()

        assert condition is True

        # L0
        # Timeliness statics
        timeliness_average_l0 = self.driver.find_element_by_id("summary-dhus-timeliness-average-delta-to-dhus-L0")

        assert timeliness_average_l0.text == "90.127"

        timeliness_minimum_l0 = self.driver.find_element_by_id("summary-dhus-timeliness-minimum-delta-to-dhus-L0")

        assert timeliness_minimum_l0.text == "45.065"

        timeliness_maximum_l0 = self.driver.find_element_by_id("summary-dhus-timeliness-maximum-delta-to-dhus-L0")

        assert timeliness_maximum_l0.text == "169.128"

        timeliness_std_l0 = self.driver.find_element_by_id("summary-dhus-timeliness-std-delta-to-dhus-L0")

        assert timeliness_std_l0.text == "61.160"

        timeliness_l0_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l0[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L0</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l0[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l0[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.557</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l0[0].event_uuid) + "'>S1A_IW_RAW__0SDV_20210317T041641_20210317T041714_037033_045BC0_11CF</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>47.712</td></tr>" +
                "<tr><td>Size (GB)</td><td>1.664</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>",
                "x": "2021-03-17T04:16:40.803000",
                "y": "47.712"
            } 
        ]

        dhus_availability_data_timeliness_l0 = self.driver.execute_script('return dhus_availability_data_timeliness["L0"].find(element => element.id === "' + str(dhus_product_completeness_l0[0].event_uuid) + '");')
        assert dhus_availability_data_timeliness_l0 == timeliness_l0_tooltip_info[0]

        # Check whether the volumes is displayed
        volume_section = self.driver.find_element_by_id("dhus-availability-volumes-section")

        condition = volume_section.is_displayed()

        assert condition is True

        l0_volume_section = self.driver.find_element_by_id("dhus-availability-volumes-L0")

        condition = l0_volume_section.is_displayed()

        assert condition is True

        # L0
        # Volumes statics
        volume_total_l0 = self.driver.find_element_by_id("summary-dhus-volumes-total-L0")

        assert volume_total_l0.text == "7.210"

        volume_average_l0 = self.driver.find_element_by_id("summary-dhus-volumes-average-L0")

        assert volume_average_l0.text == "1.442"

        volume_minimum_l0 = self.driver.find_element_by_id("summary-dhus-volumes-minimum-L0")

        assert volume_minimum_l0.text == "0.418"

        volume_maximum_l0 = self.driver.find_element_by_id("summary-dhus-volumes-maximum-L0")

        assert volume_maximum_l0.text == "1.843"

        volume_std_l0 = self.driver.find_element_by_id("summary-dhus-volumes-std-L0")

        assert volume_std_l0.text == "0.579"


        volume_l0_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l0[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L0</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l0[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l0[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.557</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l0[0].event_uuid) + "'>S1A_IW_RAW__0SDV_20210317T041641_20210317T041714_037033_045BC0_11CF</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>47.712</td></tr>" +
                "<tr><td>Size (GB)</td><td>1.664</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>",
                "x": "2021-03-17T04:16:40.803000",
                "y": 3.341
            } 
        ]

        dhus_availability_data_volumes_l0 = self.driver.execute_script('return dhus_availability_data_volumes["L0"].find(element => element.id === "' + str(dhus_product_completeness_l0[0].event_uuid) + '");')
        assert dhus_availability_data_volumes_l0 == volume_l0_tooltip_info[0]

        # Timeline
        timeline_section = self.driver.find_element_by_id("dhus-availability-timeline")

        condition = timeline_section.is_displayed()

        assert condition is True
        
        dhus_product_completeness_l0 = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:16:15.803000", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:16:49.203000", "op": "=="}])
        
        timeline_l0_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l0[0].event_uuid),
                "start": "2021-03-17T04:16:15.803000",
                "stop": "2021-03-17T04:16:49.203000",
                "timeline": "L0",
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L0</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l0[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l0[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.557</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l0[0].event_uuid) + "'>S1A_IW_RAW__0SDV_20210317T041616_20210317T041649_037033_045BC0_9A1C</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>45.065</td></tr>" +
                "<tr><td>Size (GB)</td><td>1.677</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>"
            } 
        ]
        
        returned_dhus_availability_data_timeline_l0 = self.driver.execute_script('return dhus_availability_data_timeline.find(element => element.id === "' + str(dhus_product_completeness_l0[0].event_uuid) + '");')
        assert returned_dhus_availability_data_timeline_l0 == timeline_l0_tooltip_info[0]

        # Check complete table
        complete_table = self.driver.find_element_by_id("dhus-completeness-list-table-COMPLETE")

        # Row 1
        level = complete_table.find_element_by_xpath("tbody/tr[1]/td[1]")

        assert level.text == "L0"

        satellite = complete_table.find_element_by_xpath("tbody/tr[1]/td[2]")

        assert satellite.text == "S1A"

        orbit = complete_table.find_element_by_xpath("tbody/tr[1]/td[3]")

        assert orbit.text == "37033.0"

        start = complete_table.find_element_by_xpath("tbody/tr[1]/td[4]")

        assert start.text == "2021-03-17T04:16:15.803000"

        stop = complete_table.find_element_by_xpath("tbody/tr[1]/td[5]")

        assert stop.text == "2021-03-17T04:16:49.203000"

        duration = complete_table.find_element_by_xpath("tbody/tr[1]/td[6]")

        assert duration.text == "0.557"

        imaging_mode = complete_table.find_element_by_xpath("tbody/tr[1]/td[7]")

        assert imaging_mode.text == "INTERFEROMETRIC_WIDE_SWATH"

        status = complete_table.find_element_by_xpath("tbody/tr[1]/td[8]")

        assert status.text == "PUBLISHED"

        product = complete_table.find_element_by_xpath("tbody/tr[1]/td[9]")

        assert product.text == "S1A_IW_RAW__0SDV_20210317T041616_20210317T041649_037033_045BC0_9A1C"

        time_dhus_publication = complete_table.find_element_by_xpath("tbody/tr[1]/td[10]")

        assert time_dhus_publication.text == "45.065"

        size = complete_table.find_element_by_xpath("tbody/tr[1]/td[11]")

        assert size.text == "1.677"

        datatake_id = complete_table.find_element_by_xpath("tbody/tr[1]/td[12]")

        assert datatake_id.text == "45BC0"

        start = complete_table.find_element_by_xpath("tbody/tr[1]/td[13]")

        assert start.text == "2021-03-17T04:10:33.066685"

        stop = complete_table.find_element_by_xpath("tbody/tr[1]/td[14]")

        assert stop.text == "2021-03-17T04:17:48.873819"

        datatake_duration = complete_table.find_element_by_xpath("tbody/tr[1]/td[15]")

        assert datatake_duration.text == "7.263"
        
        ### Level L1_SLC
        functions.query(self.driver, wait, "S1_", "L1_SLC", start = "2021-03-16T00:00:00", stop = "2021-03-17T23:59:59")

        # Check summary expected duration L1_SLC
        summary_expected_l1_slc = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-available-duration-L1_SLC")))

        assert summary_expected_l1_slc

        assert summary_expected_l1_slc.text == "2.221"

        # Summary data pie L1_SLC
        data_pie_l1_slc = [2.221, 0, 0]

        returned_data_pie_l1_slc = self.driver.execute_script('return completeness.L1_SLC.slice(0, 3);')
        assert data_pie_l1_slc == returned_data_pie_l1_slc

        # Summary data pie volumes
        data_pie_volumes = ["18.849"]

        returned_data_pie_volumes = self.driver.execute_script('return data_pie_volumes.datasets[0].data.slice(0, 4);')
        assert data_pie_volumes == returned_data_pie_volumes
        
        # Check whether the map is displayed
        map_section = self.driver.find_element_by_id("dhus-availability-maps-section")

        condition = map_section.is_displayed()

        assert condition is True

        l1_slc_map_section = self.driver.find_element_by_id("dhus-availability-map-L1_SLC-section")

        condition = l1_slc_map_section.is_displayed()

        assert condition is True

        dhus_product_completeness_l1_slc = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:17:08.174000", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:17:44.528000", "op": "=="}])

        map_l1_slc_tooltip_info = [
            {
                "id": str(dhus_product_completeness_l1_slc[0].event_uuid),
                "geometries": [{
                    "name": "footprint",
                    "type": "geometry",
                    "value": "POLYGON ((27.315539 32.646864, 27.26576 32.427823, 27.216108 32.208767, 27.166526 31.989698, 27.117058 31.770614, 27.067712 31.551516, 27.01848 31.332403, 26.969309 31.113278, 26.920253 30.894139, 26.871312 30.674986, 26.822465 30.455819, 24.235282 30.859376, 24.278161 31.078187, 24.321068 31.296987, 24.36403 31.515777, 24.407047 31.734556, 24.450046 31.953326, 24.493096 32.172085, 24.536205 32.390833, 24.579363 32.60957, 24.62251 32.828298, 24.665719 33.047014, 27.315539 32.646864))"
                }],
                "style": {"stroke_color": "green", "fill_color": "rgba(0,255,0,0.3)"},
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_SLC</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_slc[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_slc[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.606</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_slc[0].event_uuid) + "'>S1A_IW_SLC__1SDV_20210317T041709_20210317T041744_037033_045BC0_460C</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>458.943</td></tr>" +
                "<tr><td>Size (GB)</td><td>5.376</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>"
            } 
        ]

        dhus_availability_data_maps_l1_slc = self.driver.execute_script('return dhus_availability_data_maps["L1_SLC"].find(element => element.id === "' + str(dhus_product_completeness_l1_slc[0].event_uuid) + '");')
        assert dhus_availability_data_maps_l1_slc == map_l1_slc_tooltip_info[0]

        # Check whether the timeliness is displayed
        timeliness_section = self.driver.find_element_by_id("dhus-availability-timeliness-section")

        condition = timeliness_section.is_displayed()

        assert condition is True

        l1_slc_timeliness_section = self.driver.find_element_by_id("dhus-availability-timeliness-L1_SLC")

        condition = l1_slc_timeliness_section.is_displayed()

        assert condition is True

        # L1_SLC
        # Timeliness statics
        timeliness_average_l1_slc = self.driver.find_element_by_id("summary-dhus-timeliness-average-delta-to-dhus-L1_SLC")

        assert timeliness_average_l1_slc.text == "397.082"

        timeliness_minimum_l1_slc = self.driver.find_element_by_id("summary-dhus-timeliness-minimum-delta-to-dhus-L1_SLC")

        assert timeliness_minimum_l1_slc.text == "303.489"

        timeliness_maximum_l1_slc = self.driver.find_element_by_id("summary-dhus-timeliness-maximum-delta-to-dhus-L1_SLC")

        assert timeliness_maximum_l1_slc.text == "458.943"

        timeliness_std_l1_slc = self.driver.find_element_by_id("summary-dhus-timeliness-std-delta-to-dhus-L1_SLC")

        assert timeliness_std_l1_slc.text == "63.242"
        
        timeliness_l1_slc_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l1_slc[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_SLC</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_slc[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_slc[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.606</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_slc[0].event_uuid) + "'>S1A_IW_SLC__1SDV_20210317T041709_20210317T041744_037033_045BC0_460C</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>458.943</td></tr>" +
                "<tr><td>Size (GB)</td><td>5.376</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>",
                "x": "2021-03-17T04:17:08.174000",
                "y": "458.943"
            } 
        ]

        dhus_availability_data_timeliness_l1_slc = self.driver.execute_script('return dhus_availability_data_timeliness["L1_SLC"].find(element => element.id === "' + str(dhus_product_completeness_l1_slc[0].event_uuid) + '");')
        assert dhus_availability_data_timeliness_l1_slc == timeliness_l1_slc_tooltip_info[0]
        
        # Check whether the volumes is displayed
        volume_section = self.driver.find_element_by_id("dhus-availability-volumes-section")

        condition = volume_section.is_displayed()

        assert condition is True

        l1_slc_volume_section = self.driver.find_element_by_id("dhus-availability-volumes-L1_SLC")

        condition = l1_slc_volume_section.is_displayed()

        assert condition is True

        # L1_SLC
        # Volumes statics
        volume_total_l1_slc = self.driver.find_element_by_id("summary-dhus-volumes-total-L1_SLC")

        assert volume_total_l1_slc.text == "18.849"

        volume_average_l1_slc = self.driver.find_element_by_id("summary-dhus-volumes-average-L1_SLC")

        assert volume_average_l1_slc.text == "3.770"

        volume_minimum_l1_slc = self.driver.find_element_by_id("summary-dhus-volumes-minimum-L1_SLC")

        assert volume_minimum_l1_slc.text == "1.196"

        volume_maximum_l1_slc = self.driver.find_element_by_id("summary-dhus-volumes-maximum-L1_SLC")

        assert volume_maximum_l1_slc.text == "5.376"

        volume_std_l1_slc = self.driver.find_element_by_id("summary-dhus-volumes-std-L1_SLC")

        assert volume_std_l1_slc.text == "1.545"
        
        volume_l1_slc_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l1_slc[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_SLC</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_slc[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_slc[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.606</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_slc[0].event_uuid) + "'>S1A_IW_SLC__1SDV_20210317T041709_20210317T041744_037033_045BC0_460C</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>458.943</td></tr>" +
                "<tr><td>Size (GB)</td><td>5.376</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>",
                "x": "2021-03-17T04:17:08.174000",
                "y": 13.408000000000001
            } 
        ]

        dhus_availability_data_volumes_l1_slc = self.driver.execute_script('return dhus_availability_data_volumes["L1_SLC"].find(element => element.id === "' + str(dhus_product_completeness_l1_slc[0].event_uuid) + '");')
        assert dhus_availability_data_volumes_l1_slc == volume_l1_slc_tooltip_info[0]
        
        # Timeline
        timeline_section = self.driver.find_element_by_id("dhus-availability-timeline")

        condition = timeline_section.is_displayed()

        assert condition is True

        timeline_l1_slc_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l1_slc[0].event_uuid),
                "start": "2021-03-17T04:17:08.174000",
                "stop": "2021-03-17T04:17:44.528000",
                "timeline": "L1_SLC",
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_SLC</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_slc[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_slc[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.606</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_slc[0].event_uuid) + "'>S1A_IW_SLC__1SDV_20210317T041709_20210317T041744_037033_045BC0_460C</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>458.943</td></tr>" +
                "<tr><td>Size (GB)</td><td>5.376</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>"
            } 
        ]
        
        returned_dhus_availability_data_timeline_l1_slc = self.driver.execute_script('return dhus_availability_data_timeline.find(element => element.id === "' + str(dhus_product_completeness_l1_slc[0].event_uuid) + '");')
        assert returned_dhus_availability_data_timeline_l1_slc == timeline_l1_slc_tooltip_info[0]

        # Check complete table
        complete_table = self.driver.find_element_by_id("dhus-completeness-list-table-COMPLETE")

        # Row 1
        level = complete_table.find_element_by_xpath("tbody/tr[1]/td[1]")

        assert level.text == "L1_SLC"

        satellite = complete_table.find_element_by_xpath("tbody/tr[1]/td[2]")

        assert satellite.text == "S1A"

        orbit = complete_table.find_element_by_xpath("tbody/tr[1]/td[3]")

        assert orbit.text == "37033.0"

        start = complete_table.find_element_by_xpath("tbody/tr[1]/td[4]")

        assert start.text == "2021-03-17T04:16:18.520000"

        stop = complete_table.find_element_by_xpath("tbody/tr[1]/td[5]")

        assert stop.text == "2021-03-17T04:16:46.604000"

        duration = complete_table.find_element_by_xpath("tbody/tr[1]/td[6]")

        assert duration.text == "0.468"

        imaging_mode = complete_table.find_element_by_xpath("tbody/tr[1]/td[7]")

        assert imaging_mode.text == "INTERFEROMETRIC_WIDE_SWATH"

        status = complete_table.find_element_by_xpath("tbody/tr[1]/td[8]")

        assert status.text == "PUBLISHED"

        product = complete_table.find_element_by_xpath("tbody/tr[1]/td[9]")

        assert product.text == "S1A_IW_SLC__1SDV_20210317T041619_20210317T041646_037033_045BC0_B8DB"

        time_dhus_publication = complete_table.find_element_by_xpath("tbody/tr[1]/td[10]")

        assert time_dhus_publication.text == "450.408"

        size = complete_table.find_element_by_xpath("tbody/tr[1]/td[11]")

        assert size.text == "4.052"

        datatake_id = complete_table.find_element_by_xpath("tbody/tr[1]/td[12]")

        assert datatake_id.text == "45BC0"

        start = complete_table.find_element_by_xpath("tbody/tr[1]/td[13]")

        assert start.text == "2021-03-17T04:10:33.066685"

        stop = complete_table.find_element_by_xpath("tbody/tr[1]/td[14]")

        assert stop.text == "2021-03-17T04:17:48.873819"

        datatake_duration = complete_table.find_element_by_xpath("tbody/tr[1]/td[15]")

        assert datatake_duration.text == "7.263"

        ### Level L1_GRD
        functions.query(self.driver, wait, "S1_", "L1_GRD", start = "2021-03-16T00:00:00", stop = "2021-03-17T23:59:59")
        
        # Check summary expected duration L1_GRD
        summary_expected_l1_grd = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-available-duration-L1_GRD")))

        assert summary_expected_l1_grd

        assert summary_expected_l1_grd.text == "2.562"

        # Summary data pie L1_GRD
        data_pie_l1_grd = [2.562, 0, 0]

        returned_data_pie_l1_grd = self.driver.execute_script('return completeness.L1_GRD.slice(0, 3);')
        assert data_pie_l1_grd == returned_data_pie_l1_grd
       
        # Summary data pie volumes
        data_pie_volumes = ["3.934"]

        returned_data_pie_volumes = self.driver.execute_script('return data_pie_volumes.datasets[0].data.slice(0, 4);')
        assert data_pie_volumes == returned_data_pie_volumes
        
        # Check whether the map is displayed
        map_section = self.driver.find_element_by_id("dhus-availability-maps-section")

        condition = map_section.is_displayed()

        assert condition is True
        
        l1_grd_map_section = self.driver.find_element_by_id("dhus-availability-map-L1_GRD-section")

        condition = l1_grd_map_section.is_displayed()

        assert condition is True
        
        dhus_product_completeness_l1_grd = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:16:19.501000", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:16:45.499000", "op": "=="}])

        map_l1_grd_tooltip_info = [
            {
                "id": str(dhus_product_completeness_l1_grd[0].event_uuid),
                "geometries": [{
                    "name": "footprint",
                    "type": "geometry",
                    "value": "POLYGON ((27.993583 35.578075, 27.941029 35.354507, 27.888633 35.130922, 27.836385 34.90732, 27.784233 34.683703, 27.732234 34.460069, 27.680383 34.236418, 27.628672 34.012751, 24.936282 34.41096, 24.980741 34.634324, 25.025264 34.857675, 25.069861 35.081014, 25.114533 35.304341, 25.15921 35.527656, 25.203953 35.750959, 25.248777 35.97425, 27.993583 35.578075))"
                }],
                "style": {"stroke_color": "green", "fill_color": "rgba(0,255,0,0.3)"},
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_GRD</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_grd[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_grd[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_grd[0].event_uuid) + "'>S1A_IW_GRDH_1SDV_20210317T041620_20210317T041645_037033_045BC0_8316</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>98.605</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.848</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>"
            } 
        ]

        dhus_availability_data_maps_l1_grd = self.driver.execute_script('return dhus_availability_data_maps["L1_GRD"].find(element => element.id === "' + str(dhus_product_completeness_l1_grd[0].event_uuid) + '");')
        assert dhus_availability_data_maps_l1_grd == map_l1_grd_tooltip_info[0]

        # Check whether the timeliness is displayed
        timeliness_section = self.driver.find_element_by_id("dhus-availability-timeliness-section")

        condition = timeliness_section.is_displayed()

        assert condition is True

        l1_grd_timeliness_section = self.driver.find_element_by_id("dhus-availability-timeliness-L1_GRD")

        condition = l1_grd_timeliness_section.is_displayed()

        assert condition is True

        # L1_GRD
        # Timeliness statics
        timeliness_average_l1_grd = self.driver.find_element_by_id("summary-dhus-timeliness-average-delta-to-dhus-L1_GRD")

        assert timeliness_average_l1_grd.text == "129.716"

        timeliness_minimum_l1_grd = self.driver.find_element_by_id("summary-dhus-timeliness-minimum-delta-to-dhus-L1_GRD")

        assert timeliness_minimum_l1_grd.text == "92.660"

        timeliness_maximum_l1_grd = self.driver.find_element_by_id("summary-dhus-timeliness-maximum-delta-to-dhus-L1_GRD")

        assert timeliness_maximum_l1_grd.text == "193.702"

        timeliness_std_l1_grd = self.driver.find_element_by_id("summary-dhus-timeliness-std-delta-to-dhus-L1_GRD")

        assert timeliness_std_l1_grd.text == "44.076"
        
        timeliness_l1_grd_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l1_grd[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_GRD</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_grd[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_grd[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_grd[0].event_uuid) + "'>S1A_IW_GRDH_1SDV_20210317T041620_20210317T041645_037033_045BC0_8316</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>98.605</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.848</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>",
                "x": "2021-03-17T04:16:19.501000",
                "y": "98.605"
            } 
        ]

        dhus_availability_data_timeliness_l1_grd = self.driver.execute_script('return dhus_availability_data_timeliness["L1_GRD"].find(element => element.id === "' + str(dhus_product_completeness_l1_grd[0].event_uuid) + '");')
        assert dhus_availability_data_timeliness_l1_grd == timeliness_l1_grd_tooltip_info[0]

        # Check whether the volumes is displayed
        volume_section = self.driver.find_element_by_id("dhus-availability-volumes-section")

        condition = volume_section.is_displayed()

        assert condition is True

        l1_grd_volume_section = self.driver.find_element_by_id("dhus-availability-volumes-L1_GRD")

        condition = l1_grd_volume_section.is_displayed()

        assert condition is True

        # L1_GRD
        # Volumes statics
        volume_total_l1_grd = self.driver.find_element_by_id("summary-dhus-volumes-total-L1_GRD")

        assert volume_total_l1_grd.text == "3.934"

        volume_average_l1_grd = self.driver.find_element_by_id("summary-dhus-volumes-average-L1_GRD")

        assert volume_average_l1_grd.text == "0.656"

        volume_minimum_l1_grd = self.driver.find_element_by_id("summary-dhus-volumes-minimum-L1_GRD")

        assert volume_minimum_l1_grd.text == "0.071"

        volume_maximum_l1_grd = self.driver.find_element_by_id("summary-dhus-volumes-maximum-L1_GRD")

        assert volume_maximum_l1_grd.text == "1.087"

        volume_std_l1_grd = self.driver.find_element_by_id("summary-dhus-volumes-std-L1_GRD")

        assert volume_std_l1_grd.text == "0.403"
        
        volume_l1_grd_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l1_grd[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_GRD</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_grd[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_grd[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_grd[0].event_uuid) + "'>S1A_IW_GRDH_1SDV_20210317T041620_20210317T041645_037033_045BC0_8316</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>98.605</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.848</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>",
                "x": "2021-03-17T04:16:19.501000",
                "y": 1.702
            } 
        ]

        dhus_availability_data_volumes_l1_grd = self.driver.execute_script('return dhus_availability_data_volumes["L1_GRD"].find(element => element.id === "' + str(dhus_product_completeness_l1_grd[0].event_uuid) + '");')
        assert dhus_availability_data_volumes_l1_grd == volume_l1_grd_tooltip_info[0]

        # Timeline
        timeline_section = self.driver.find_element_by_id("dhus-availability-timeline")

        condition = timeline_section.is_displayed()

        assert condition is True

        timeline_l1_grd_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l1_grd[0].event_uuid),
                "start": "2021-03-17T04:16:19.501000",
                "stop": "2021-03-17T04:16:45.499000",
                "timeline": "L1_GRD",
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L1_GRD</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l1_grd[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l1_grd[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l1_grd[0].event_uuid) + "'>S1A_IW_GRDH_1SDV_20210317T041620_20210317T041645_037033_045BC0_8316</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>98.605</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.848</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>"
            } 
        ]
        
        returned_dhus_availability_data_timeline_l1_grd = self.driver.execute_script('return dhus_availability_data_timeline.find(element => element.id === "' + str(dhus_product_completeness_l1_grd[0].event_uuid) + '");')
        assert returned_dhus_availability_data_timeline_l1_grd == timeline_l1_grd_tooltip_info[0]

        # Check complete table
        complete_table = self.driver.find_element_by_id("dhus-completeness-list-table-COMPLETE")
        
        # Row 1
        level = complete_table.find_element_by_xpath("tbody/tr[1]/td[1]")

        assert level.text == "L1_GRD"

        satellite = complete_table.find_element_by_xpath("tbody/tr[1]/td[2]")

        assert satellite.text == "S1A"

        orbit = complete_table.find_element_by_xpath("tbody/tr[1]/td[3]")

        assert orbit.text == "37033.0"

        start = complete_table.find_element_by_xpath("tbody/tr[1]/td[4]")

        assert start.text == "2021-03-17T04:15:54.500000"

        stop = complete_table.find_element_by_xpath("tbody/tr[1]/td[5]")

        assert stop.text == "2021-03-17T04:16:20.500000"

        duration = complete_table.find_element_by_xpath("tbody/tr[1]/td[6]")

        assert duration.text == "0.433"

        imaging_mode = complete_table.find_element_by_xpath("tbody/tr[1]/td[7]")

        assert imaging_mode.text == "INTERFEROMETRIC_WIDE_SWATH"

        status = complete_table.find_element_by_xpath("tbody/tr[1]/td[8]")

        assert status.text == "PUBLISHED"

        product = complete_table.find_element_by_xpath("tbody/tr[1]/td[9]")

        assert product.text == "S1A_IW_GRDH_1SDV_20210317T041555_20210317T041620_037033_045BC0_4630"

        time_dhus_publication = complete_table.find_element_by_xpath("tbody/tr[1]/td[10]")

        assert time_dhus_publication.text == "92.66"

        size = complete_table.find_element_by_xpath("tbody/tr[1]/td[11]")

        assert size.text == "0.854"

        datatake_id = complete_table.find_element_by_xpath("tbody/tr[1]/td[12]")

        assert datatake_id.text == "45BC0"

        start = complete_table.find_element_by_xpath("tbody/tr[1]/td[13]")

        assert start.text == "2021-03-17T04:10:33.066685"

        stop = complete_table.find_element_by_xpath("tbody/tr[1]/td[14]")

        assert stop.text == "2021-03-17T04:17:48.873819"

        datatake_duration = complete_table.find_element_by_xpath("tbody/tr[1]/td[15]")

        assert datatake_duration.text == "7.263"
        
        ### Level L2_OCN
        functions.query(self.driver, wait, "S1_", "L2_OCN", start = "2021-03-16T00:00:00", stop = "2021-03-17T23:59:59")

        # Check summary expected duration L2_OCN
        summary_expected_l2_ocn = wait.until(EC.visibility_of_element_located((By.ID,"summary-dhus-completeness-available-duration-L2_OCN")))

        assert summary_expected_l2_ocn

        assert summary_expected_l2_ocn.text == "1.884"

        # Summary data pie L2_OCN
        data_pie_l2_ocn = [1.884, 0, 0]

        returned_data_pie_l2_ocn = self.driver.execute_script('return completeness.L2_OCN.slice(0, 3);')
        assert data_pie_l2_ocn == returned_data_pie_l2_ocn
        
        # Summary data pie volumes
        data_pie_volumes = ["0.029"]

        returned_data_pie_volumes = self.driver.execute_script('return data_pie_volumes.datasets[0].data.slice(0, 4);')
        assert data_pie_volumes == returned_data_pie_volumes

        # Check whether the map is displayed
        map_section = self.driver.find_element_by_id("dhus-availability-maps-section")

        condition = map_section.is_displayed()

        assert condition is True

        l2_ocn_map_section = self.driver.find_element_by_id("dhus-availability-map-L2_OCN-section")

        condition = l2_ocn_map_section.is_displayed()

        assert condition is True
        
        dhus_product_completeness_l2ocn = self.query_eboa.get_events(gauge_names ={"filter": "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L2_OCN", "op":"=="},
                                                                    start_filters =[{"date": "2021-03-17T04:16:44.501000", "op":"=="}],
                                                                    stop_filters = [{"date": "2021-03-17T04:17:10.499000", "op": "=="}])
        
        map_l2ocn_tooltip_info = [
            {
                "id": str(dhus_product_completeness_l2ocn[0].event_uuid),
                "geometries": [{
                    "name": "footprint",
                    "type": "geometry",
                    "value": "POLYGON ((27.64254 34.072855, 27.590896 33.849177, 27.539394 33.625483, 27.488033 33.401772, 27.436755 33.178048, 27.385608 32.954307, 27.334595 32.730551, 27.283714 32.506778, 24.638111 32.907136, 24.682249 33.130578, 24.72645 33.354008, 24.770716 33.577425, 24.81504 33.800832, 24.85936 34.024227, 24.903747 34.247611, 24.948206 34.470982, 27.64254 34.072855))"
                }],
                "style": {"stroke_color": "green", "fill_color": "rgba(0,255,0,0.3)"},
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L2_OCN</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l2ocn[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l2ocn[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l2ocn[0].event_uuid) + "'>S1A_IW_OCN__2SDV_20210317T041645_20210317T041710_037033_045BC0_563F</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>69.896</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.007</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>"
            } 
        ]

        dhus_availability_data_maps_l2_ocn = self.driver.execute_script('return dhus_availability_data_maps["L2_OCN"].find(element => element.id === "' + str(dhus_product_completeness_l2ocn[0].event_uuid) + '");')
        assert dhus_availability_data_maps_l2_ocn == map_l2ocn_tooltip_info[0]

        # Check whether the timeliness is displayed
        timeliness_section = self.driver.find_element_by_id("dhus-availability-timeliness-section")

        condition = timeliness_section.is_displayed()

        assert condition is True

        l2_ocn_timeliness_section = self.driver.find_element_by_id("dhus-availability-timeliness-L2_OCN")

        condition = l2_ocn_timeliness_section.is_displayed()

        assert condition is True
        
        # L2_OCN
        # Timeliness statics
        timeliness_average_l2_ocn = self.driver.find_element_by_id("summary-dhus-timeliness-average-delta-to-dhus-L2_OCN")

        assert timeliness_average_l2_ocn.text == "80.450"

        timeliness_minimum_l2_ocn = self.driver.find_element_by_id("summary-dhus-timeliness-minimum-delta-to-dhus-L2_OCN")

        assert timeliness_minimum_l2_ocn.text == "61.287"

        timeliness_maximum_l2_ocn = self.driver.find_element_by_id("summary-dhus-timeliness-maximum-delta-to-dhus-L2_OCN")

        assert timeliness_maximum_l2_ocn.text == "97.950"

        timeliness_std_l2_ocn = self.driver.find_element_by_id("summary-dhus-timeliness-std-delta-to-dhus-L2_OCN")

        assert timeliness_std_l2_ocn.text == "17.646"
        
        timeliness_l2ocn_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l2ocn[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L2_OCN</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l2ocn[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l2ocn[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l2ocn[0].event_uuid) + "'>S1A_IW_OCN__2SDV_20210317T041645_20210317T041710_037033_045BC0_563F</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>69.896</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.007</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>",
                "x": "2021-03-17T04:16:44.501000",
                "y": "69.896"
            } 
        ]

        dhus_availability_data_timeliness_l2_ocn = self.driver.execute_script('return dhus_availability_data_timeliness["L2_OCN"].find(element => element.id === "' + str(dhus_product_completeness_l2ocn[0].event_uuid) + '");')
        assert dhus_availability_data_timeliness_l2_ocn == timeliness_l2ocn_tooltip_info[0]
      
        # Check whether the volumes is displayed
        volume_section = self.driver.find_element_by_id("dhus-availability-volumes-section")

        condition = volume_section.is_displayed()

        assert condition is True

        l2_ocn_volume_section = self.driver.find_element_by_id("dhus-availability-volumes-L2_OCN")

        condition = l2_ocn_volume_section.is_displayed()

        assert condition is True
        
        # L2_OCN
        # Volumes statics
        volume_total_l2_ocn = self.driver.find_element_by_id("summary-dhus-volumes-total-L2_OCN")

        assert volume_total_l2_ocn.text == "0.029"

        volume_average_l2_ocn = self.driver.find_element_by_id("summary-dhus-volumes-average-L2_OCN")

        assert volume_average_l2_ocn.text == "0.007"

        volume_minimum_l2_ocn = self.driver.find_element_by_id("summary-dhus-volumes-minimum-L2_OCN")

        assert volume_minimum_l2_ocn.text == "0.007"

        volume_maximum_l2_ocn = self.driver.find_element_by_id("summary-dhus-volumes-maximum-L2_OCN")

        assert volume_maximum_l2_ocn.text == "0.008"

        volume_std_l2_ocn = self.driver.find_element_by_id("summary-dhus-volumes-std-L2_OCN")

        assert volume_std_l2_ocn.text == "0.001"
        
        volume_l2ocn_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l2ocn[0].event_uuid),
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L2_OCN</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l2ocn[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l2ocn[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l2ocn[0].event_uuid) + "'>S1A_IW_OCN__2SDV_20210317T041645_20210317T041710_037033_045BC0_563F</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>69.896</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.007</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>",
                "x": "2021-03-17T04:16:44.501000",
                "y": 0.021
            } 
        ]

        dhus_availability_data_volumes_l2_ocn = self.driver.execute_script('return dhus_availability_data_volumes["L2_OCN"].find(element => element.id === "' + str(dhus_product_completeness_l2ocn[0].event_uuid) + '");')
        assert dhus_availability_data_volumes_l2_ocn == volume_l2ocn_tooltip_info[0]

        # Timeline
        timeline_section = self.driver.find_element_by_id("dhus-availability-timeline")

        condition = timeline_section.is_displayed()

        assert condition is True

        timeline_l2_ocn_tooltip_info = [
            {
                "className": "fill-border-green",
                "group": "S1A",
                "id": str(dhus_product_completeness_l2ocn[0].event_uuid),
                "start": "2021-03-17T04:16:44.501000",
                "stop": "2021-03-17T04:17:10.499000",
                "timeline": "L2_OCN",
                "tooltip": "<table border='1'>" + 
                "<tr><td>Level</td><td>L2_OCN</td></tr>" + 
                "<tr><td>Satellite</td><td>S1A</td></tr>" + 
                "<tr><td>Orbit</td><td><a href='/eboa_nav/query-event-links/" + str(planned_imaging[0].event_uuid) + "'>37033.0</a></td></tr>" +
                "<tr><td>Start</td><td>" + dhus_product_completeness_l2ocn[0].start.isoformat() + "</td></tr>" +
                "<tr><td>Stop</td><td>" + dhus_product_completeness_l2ocn[0].stop.isoformat() + "</td></tr>" +
                "<tr><td>Duration (m)</td><td>0.433</td></tr>" +
                "<tr><td>Imaging mode</td><td>INTERFEROMETRIC_WIDE_SWATH</td></tr>" +
                "<tr><td>Status</td><td><a class='bold-green' href='/views/dhus-availability-by-datatake/" + str(planned_imaging[0].event_uuid) + "'>PUBLISHED</a></td></tr>" +
                "<tr><td>Product</td><td><a href='/eboa_nav/query-event-links/" + str(dhus_product_completeness_l2ocn[0].event_uuid) + "'>S1A_IW_OCN__2SDV_20210317T041645_20210317T041710_037033_045BC0_563F</a></td></tr>"
                "<tr><td>Time to DHUS publication (m)</td><td>69.896</td></tr>" +
                "<tr><td>Size (GB)</td><td>0.007</td></tr>" + 
                "<tr><td>Datatake id</td><td>45BC0</td></tr>" +
                "<tr><td>Datatake start</td><td>2021-03-17T04:10:33.066685</td></tr>" +
                "<tr><td>Datatake stop</td><td>2021-03-17T04:17:48.873819</td></tr>" +
                "<tr><td>Datatake duration(m)</td><td>7.263</td></tr>"
                "</table>"
            } 
        ]
        
        returned_dhus_availability_data_timeline_l2_ocn = self.driver.execute_script('return dhus_availability_data_timeline.find(element => element.id === "' + str(dhus_product_completeness_l2ocn[0].event_uuid) + '");')
        assert returned_dhus_availability_data_timeline_l2_ocn == timeline_l2_ocn_tooltip_info[0]
        
        # Check complete table
        complete_table = self.driver.find_element_by_id("dhus-completeness-list-table-COMPLETE")

        # Row 1
        level = complete_table.find_element_by_xpath("tbody/tr[1]/td[1]")

        assert level.text == "L2_OCN"

        satellite = complete_table.find_element_by_xpath("tbody/tr[1]/td[2]")

        assert satellite.text == "S1A"

        orbit = complete_table.find_element_by_xpath("tbody/tr[1]/td[3]")

        assert orbit.text == "37033.0"

        start = complete_table.find_element_by_xpath("tbody/tr[1]/td[4]")

        assert start.text == "2021-03-17T04:15:54.500000"

        stop = complete_table.find_element_by_xpath("tbody/tr[1]/td[5]")

        assert stop.text == "2021-03-17T04:16:20.500000"

        duration = complete_table.find_element_by_xpath("tbody/tr[1]/td[6]")

        assert duration.text == "0.433"

        imaging_mode = complete_table.find_element_by_xpath("tbody/tr[1]/td[7]")

        assert imaging_mode.text == "INTERFEROMETRIC_WIDE_SWATH"

        status = complete_table.find_element_by_xpath("tbody/tr[1]/td[8]")

        assert status.text == "PUBLISHED"

        product = complete_table.find_element_by_xpath("tbody/tr[1]/td[9]")

        assert product.text == "S1A_IW_OCN__2SDV_20210317T041555_20210317T041620_037033_045BC0_015F"

        time_dhus_publication = complete_table.find_element_by_xpath("tbody/tr[1]/td[10]")

        assert time_dhus_publication.text == "61.287"

        size = complete_table.find_element_by_xpath("tbody/tr[1]/td[11]")

        assert size.text == "0.007"

        datatake_id = complete_table.find_element_by_xpath("tbody/tr[1]/td[12]")

        assert datatake_id.text == "45BC0"

        start = complete_table.find_element_by_xpath("tbody/tr[1]/td[13]")

        assert start.text == "2021-03-17T04:10:33.066685"

        stop = complete_table.find_element_by_xpath("tbody/tr[1]/td[14]")

        assert stop.text == "2021-03-17T04:17:48.873819"

        datatake_duration = complete_table.find_element_by_xpath("tbody/tr[1]/td[15]")

        assert datatake_duration.text == "7.263"