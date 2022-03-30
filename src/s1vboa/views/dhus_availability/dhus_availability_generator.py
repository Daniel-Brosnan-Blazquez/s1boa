"""
Generator module for the DHUS availability view for the monitoring of the Sentinel-1 constellation

Written by DEIMOS Space S.L. (dibb)

module s1vboa
"""
# Import python utilities
import os

# Import helpers
from vboa.functions import export_html

# Import vboa app creator
from s1vboa import create_app

version = "1.0"

def generate_report(begin, end, metadata, parameters = None):

    levels = "ALL"
    if "levels" in parameters:
        if parameters["levels"] in ["L0", "L1_SLC", "L1_GRD", "L2_OCN", "ALL"]:
            levels = parameters["levels"]
        # end if
    # end if
    
    app = create_app()
    client = app.test_client()
    response = client.post("/views/dhus-availability", data={
        "start": begin,
        "stop": end,
        "mission": "S2_",
        "levels": levels,
    })

    html_file_path = export_html(response)

    metadata["operations"][0]["report"]["generator_version"] = version
    metadata["operations"][0]["report"]["group"] = "DHUS_AVAILABILITY"
    metadata["operations"][0]["report"]["group_description"] = "Group of reports dedicated for the monitoring of the publication of Sentinel-1 production in DHUS"

    return html_file_path
