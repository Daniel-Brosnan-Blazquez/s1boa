"""
Data availability in DHUS (completeness from planning) view for s1boa

Written by DEIMOS Space S.L. (dibb)

module s1vboa
"""
# Import python utilities
import sys
import json
import datetime
from dateutil import parser

# Import flask utilities
from flask import Blueprint, flash, g, current_app, redirect, render_template, request, url_for
from flask_debugtoolbar import DebugToolbarExtension
from flask import jsonify

# Import eboa utilities
from eboa.engine.query import Query
import eboa.engine.engine as eboa_engine
from eboa.engine.engine import Engine
from eboa.engine import export as eboa_export

# Import views functions
from svboa.views import functions as svboa_functions

bp = Blueprint("dhus-completeness", __name__, url_prefix="/views")
query = Query()

@bp.route("/dhus-completeness", methods=["GET", "POST"])
def show_dhus_completeness():
    """
    DHUS completeness view for the Sentinel-1 mission.
    """
    current_app.logger.debug("DHUS completeness view")

    filters = {}
    filters["limit"] = ["20"]    
    if request.method == "POST":
        filters = request.form.to_dict(flat=False).copy()
    # end if
    filters["offset"] = [""]

    # Initialize reporting period (now - 1 days, now)
    start_filter = {
        "date": (datetime.datetime.now()).isoformat(),
        "op": "<="
    }
    stop_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat(),
        "op": ">="
    }
    mission = "S1_"
    levels = "ALL"

    window_size = 1
    start_filter_calculated, stop_filter_calculated = svboa_functions.get_start_stop_filters(query, current_app, request, window_size, mission, filters)

    if start_filter_calculated != None:
        start_filter = start_filter_calculated
    # end if

    if stop_filter_calculated != None:
        stop_filter = stop_filter_calculated
    # end if

    if request.method == "POST":

        if request.form["mission"] != "":
            mission = request.form["mission"]
        # end if
        if request.form["levels"] != "":
                levels = request.form["levels"]
        # end if

    # end if

    filters["start"] = [stop_filter["date"]]
    filters["stop"] = [start_filter["date"]]
    filters["mission"] = [mission]
    filters["levels"] = levels

    return query_dhus_completeness_and_render(start_filter, stop_filter, mission, levels, filters = filters)

@bp.route("/dhus-completeness-by-datatake/<string:planned_imaging_uuid>")
def show_specific_datatake(planned_imaging_uuid):
    """
    Specific dhus completeness view for one datatake related to the Sentinel-1 mission.
    """
    current_app.logger.debug("Specific dhus completeness view")

    # Get the events of the datatake
    planned_imaging = query.get_events(event_uuids = {"filter": planned_imaging_uuid, "op": "=="})[0]
    
    filters = {}
    filters["limit"] = [""]
    filters["offset"] = [""]
    start_filter = {
        "date": planned_imaging.stop.isoformat(),
        "op": "<="
    }
    stop_filter = {
        "date": planned_imaging.start.isoformat(),
        "op": ">="
    }
    mission = "S1_"
    levels = "ALL"

    filters["start"] = [stop_filter["date"]]
    filters["stop"] = [start_filter["date"]]
    filters["mission"] = [mission]

    filters["start"] = [stop_filter["date"]]
    filters["stop"] = [start_filter["date"]]
    filters["mission"] = [mission]
    filters["levels"] = levels

    return query_dhus_completeness_and_render(start_filter, stop_filter, mission, levels, filters = filters, planned_imaging_uuid = planned_imaging_uuid)

@bp.route("/dhus-completeness-pages", methods=["POST"])
def query_dhus_completeness_pages():
    """
    DHUS completeness view for the Sentinel-1 mission using pages.
    """
    current_app.logger.debug("DHUS completeness view using pages")
    filters = request.json

    mission = filters["mission"][0]
    levels = filters["levels"]

    # window_size is not used, here only for using the same API
    window_size = None
    start_filter, stop_filter = svboa_functions.get_start_stop_filters(query, current_app, request, window_size, mission, filters)

    return query_dhus_completeness_and_render(start_filter, stop_filter, mission, levels, filters = filters)

@bp.route("/sliding-dhus-completeness-parameters", methods=["GET", "POST"])
def show_sliding_dhus_completeness_parameters():
    """
    DHUS completeness sliding view for the Sentinel-1 mission.
    """
    current_app.logger.debug("Sliding acquistion view with parameters")

    window_delay = float(request.args.get("window_delay"))
    window_size = float(request.args.get("window_size"))
    repeat_cycle = float(request.args.get("repeat_cycle"))
    mission = request.args.get("mission")
    levels = "ALL"
    if request.args.get("levels") != "":
        levels = request.args.get("levels")
    # end if


    start_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=window_delay)).isoformat(),
        "op": "<="
    }
    stop_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=(window_delay+window_size))).isoformat(),
        "op": ">="
    }

    sliding_window = {
        "window_delay": window_delay,
        "window_size": window_size,
        "repeat_cycle": repeat_cycle,
        "mission": mission,
        "levels": levels
    }

    return query_dhus_completeness_and_render(start_filter, stop_filter, mission, levels, sliding_window)

@bp.route("/sliding-dhus-completeness", methods=["GET", "POST"])
def show_sliding_dhus_completeness():
    """
    DHUS completeness sliding view for the Sentinel-1 mission.
    """
    current_app.logger.debug("Sliding acquisition view")

    window_delay=0
    window_size=1
    repeat_cycle=1

    mission = "S1_"
    levels = "ALL"
    
    if request.method == "POST":

        if request.form["mission"] != "":
            mission = request.form["mission"]
        # end if

        if request.form["levels"] != "":
            levels = request.form["levels"]
        # end if

        if request.form["dhus_completeness_window_delay"] != "":
            window_delay = float(request.form["dhus_completeness_window_delay"])
        # end if

        if request.form["dhus_completeness_window_size"] != "":
            window_size = float(request.form["dhus_completeness_window_size"])
        # end if

        if request.form["dhus_completeness_repeat_cycle"] != "":
            repeat_cycle = float(request.form["dhus_completeness_repeat_cycle"])
        # end if

    # end if

    start_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=window_delay)).isoformat(),
        "op": "<="
    }
    stop_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=(window_delay+window_size))).isoformat(),
        "op": ">="
    }

    sliding_window = {
        "window_delay": window_delay,
        "window_size": window_size,
        "repeat_cycle": repeat_cycle,
        "mission": mission,
        "levels": levels
    }

    return query_dhus_completeness_and_render(start_filter, stop_filter, mission, levels, sliding_window)

def query_dhus_completeness_and_render(start_filter, stop_filter, mission, levels, sliding_window = None, filters = None, planned_imaging_uuid = None):

    data = query_dhus_completeness_structure(start_filter, stop_filter, mission, levels, filters, planned_imaging_uuid)

    # orbpre_events = svboa_functions.query_orbpre_events(query, current_app, start_filter, stop_filter, mission)

    #####
    # Metadata
    #####
    data["metadata"] = {}
    metadata = data["metadata"]
    metadata["levels"] = levels
    metadata["reporting_start"] = stop_filter["date"]
    metadata["reporting_stop"] = start_filter["date"]

    # Save data and obtain path to json
    
    route = "views/dhus_completeness/dhus_completeness.html"
    if planned_imaging_uuid != None:
        route = "views/dhus_completeness/dhus_completeness_datatake.html"
    # end if

    return render_template(route, data=data, sliding_window=sliding_window, filters=filters)

def query_dhus_completeness_structure(start_filter, stop_filter, mission, levels, filters, planned_imaging_uuid = None):
    """
    Query planned acquisition events.
    """
    current_app.logger.debug("Query planned acquisition events")

    kwargs = {}

    if planned_imaging_uuid == None:
        # Set offset and limit for the query
        if filters and "offset" in filters and filters["offset"][0] != "":
            kwargs["offset"] = filters["offset"][0]
        # end if
        if filters and "limit" in filters and filters["limit"][0] != "":
            kwargs["limit"] = filters["limit"][0]
        # end if

        # Set order by reception_time descending
        kwargs["order_by"] = {"field": "start", "descending": True}

        # Start filter
        if start_filter:
            kwargs["start_filters"] = [{"date": start_filter["date"], "op": start_filter["op"]}]
        # end if

        # Stop filter
        if stop_filter:
            kwargs["stop_filters"] = [{"date": stop_filter["date"], "op": stop_filter["op"]}]
        # end if

        # Mission
        if mission:
            kwargs["value_filters"] = [{"name": {"op": "==", "filter": "satellite"},
                                        "type": "text",
                                        "value": {"op": "like", "filter": mission}
                                    }]
        # end if
        kwargs["gauge_names"] = {"filter": "PLANNED_IMAGING", "op": "=="}
    else:
        kwargs["event_uuids"] = {"filter": planned_imaging_uuid, "op": "=="}
    # end if
    
    ####
    # Query planned imagings
    ####
    kwargs["link_names"] = {"filter": ["DHUS_PRODUCT_COMPLETENESS"], "op": "in"}
    planned_imaging_events = query.get_linking_events_group_by_link_name(**kwargs)

    # Build data dictionary
    data = {}
    
    # Export PLANNED_IMAGING events
    eboa_export.export_events(data, planned_imaging_events["prime_events"], group = "planned_imaging")

    # Export DHUS_PRODUCT_COMPLETENESS events for L0
    dhus_product_completeness_l0 = [event for event in planned_imaging_events["linking_events"]["DHUS_PRODUCT_COMPLETENESS"] if event.gauge.name == "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L0"]
    eboa_export.export_events(data, dhus_product_completeness_l0, group = "dhus_product_completeness_l0")
    
    # Export DHUS_PRODUCT_COMPLETENESS events for L1 SLC
    dhus_product_completeness_l1_slc = [event for event in planned_imaging_events["linking_events"]["DHUS_PRODUCT_COMPLETENESS"] if event.gauge.name == "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_SLC"]
    eboa_export.export_events(data, dhus_product_completeness_l1_slc, group = "dhus_product_completeness_l1_slc")

    # Export DHUS_PRODUCT_COMPLETENESS events for L1 GRD
    dhus_product_completeness_l1_grd = [event for event in planned_imaging_events["linking_events"]["DHUS_PRODUCT_COMPLETENESS"] if event.gauge.name == "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L1_GRD"]
    eboa_export.export_events(data, dhus_product_completeness_l1_grd, group = "dhus_product_completeness_l1_grd")

    # Export DHUS_PRODUCT_COMPLETENESS events for L2 OCN
    dhus_product_completeness_l2_ocn = [event for event in planned_imaging_events["linking_events"]["DHUS_PRODUCT_COMPLETENESS"] if event.gauge.name == "PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_L2_OCN"]
    eboa_export.export_events(data, dhus_product_completeness_l2_ocn, group = "dhus_product_completeness_l2_ocn")

    return data
