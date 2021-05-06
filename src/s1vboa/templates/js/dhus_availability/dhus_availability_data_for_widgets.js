var dhus_availability_data_timeline = []
var dhus_availability_data_timeliness = {}
var dhus_availability_data_timeliness_for_statistics = {}

{% for completeness in list_products_completeness %}

{# Obtain planned imaging #}
{% set planned_imaging = completeness|get_linking_event("PLANNED_IMAGING", data) %}

{# Obtain level #}
{% set level = completeness["gauge"]["name"].replace("PLANNED_IMAGING_DHUS_PRODUCT_COMPLETENESS_", "") %}

{# Obtain relevant values #}
{% set values = completeness|get_values([{"name": {"filter": "satellite","op": "=="}, "group":"satellite"}, {"name": {"filter": ["orbit","start_orbit"],"op": "in"}, "group":"orbit"}, {"name": {"filter": "status","op": "=="}, "group":"status"}, {"name": {"filter": "datatake_id","op": "=="}, "group":"datatake_id"}]) %}
{# Obtain satellite #}
{% set satellite = values["satellite"][0]["value"] %}

{# Obtain sensing orbit #}
{% set orbit = values["orbit"][0]["value"] %}

{% if planned_imaging %}
{% set orbit_for_tooltip = "<a href='/eboa_nav/query-event-links/" + planned_imaging.event_uuid + "'>" + orbit + "</a>" %}
{% else %}
{% set orbit_for_tooltip = orbit %}
{% endif %}

{# Obtain status #}
{% set status = values["status"][0]["value"] %}

{# Obtain datatake id #}
{% set datatake_id = values["datatake_id"][0]["value"] %}

{# Obtain information related to the product if available #}
{% set dhus_product = "N/A" %}

{% if data["metadata"]["show"]["timeliness"] %}
{% set delta_to_dhus_for_tooltip = "<a class='bold-red'>N/A</a>" %}
{% else %}
{% set delta_to_dhus_for_tooltip = "DISCARD" %}
{% endif %}

{% if data["metadata"]["show"]["volumes"] %}
{% set size_for_tooltip = "<a class='bold-red'>N/A</a>" %}
{% else %}
{% set size_for_tooltip = "DISCARD" %}
{% endif %}

{% if "explicit_reference" in completeness %}
{% set dhus_product = completeness["explicit_reference"]["name"] %}
{% endif %}

{# Define status class #}
{% if status == "MISSING" %}

{% set class_name = "fill-border-red" %}
{% set status_class = "bold-red" %}

{% elif status == "UNEXPECTED" %}

{% set class_name = "fill-border-blue" %}
{% set status_class = "bold-blue" %}

{% else %}

{% set class_name = "fill-border-green" %}
{% set status_class = "bold-green" %}

{% if data["metadata"]["show"]["timeliness"] or data["metadata"]["show"]["volumes"] %}
{% set er = data["explicit_references"][completeness["explicit_reference"]["uuid"]] %}

{% set annotations = er|get_annotations([{"name": {"filter": "DHUS_METADATA_INFORMATION","op": "=="}, "group":"metadata"}, {"name": {"filter": "DHUS_PUBLICATION_TIME","op": "=="}, "group":"publication_time"}]) %}

{% if data["metadata"]["show"]["timeliness"] %}

{% set publication_time_values = annotations["publication_time"]|get_annotations_from_data(data)|first|get_values([{"name": {"filter": "dhus_publication_time","op": "=="}, "group":"publication_time"}]) %}

{% set delta_to_dhus = (publication_time_values["publication_time"][0]["value"]|date_op(planned_imaging.stop, "-") / 60)|round(3) %}

{% set delta_to_dhus_for_tooltip = delta_to_dhus %}

{% endif %}

{% if data["metadata"]["show"]["volumes"] %}

{% set size_values = annotations["metadata"]|get_annotations_from_data(data)|first|get_values([{"name": {"filter": "size","op": "=="}, "group":"size"}]) %}

{% set size = (size_values["size"][0]["value"]|float / 1000 / 1000 / 1000)|round(3) %}

{% set size_for_tooltip = size %}

{% endif %}
{% endif %}

{% endif %}

{% set status_for_tooltip = "<a class='" + status_class + "' href='/views/dhus-availability-by-datatake/" + planned_imaging.event_uuid + "'>" + status + "</a>" %}

{% if dhus_product != "N/A" %}
{% set dhus_product_for_tooltip = "<a href='/eboa_nav/query-event-links/" + completeness.event_uuid + "'>" + dhus_product + "</a>" %}
{% else %}
{% set dhus_product_for_tooltip = "<a class='" + status_class + "'>" + dhus_product + "</a>" %}
{% endif %}

{% if data["metadata"]["show"]["completeness"] %}
dhus_availability_data_timeline.push({
    "id": "{{ completeness.event_uuid }}",
    "group": "{{ satellite }}",
    "timeline": "{{ level }}",
    "start": "{{ completeness['start'] }}",
    "stop": "{{ completeness['stop'] }}",
    "tooltip": create_dhus_availability_tooltip("{{ level }}", "{{ satellite }}", "{{ orbit_for_tooltip }}", "{{ completeness.start }}", "{{ completeness.stop }}", "{{ (completeness.duration / 60)|round(3) }}", "{{ status_for_tooltip }}", "{{ dhus_product_for_tooltip }}", "{{ delta_to_dhus_for_tooltip }}", "{{ size_for_tooltip }}", "{{ datatake_id }}", "{{ planned_imaging.start }}", "{{ planned_imaging.stop }}", "{{ (planned_imaging.duration / 60)|round(3) }}"),
    "className": "{{ class_name }}"
})
{% endif %}

{% if data["metadata"]["show"]["timeliness"] %}
if (!("{{ level }}" in dhus_availability_data_timeliness)){
    dhus_availability_data_timeliness["{{ level }}"] = []
}
dhus_availability_data_timeliness["{{ level }}"].push({
    "id": "{{ completeness.event_uuid }}",
    "group": "{{ satellite }}",
    "x": "{{ completeness.start }}",
    "y": "{{ delta_to_dhus }}",
    "tooltip": create_dhus_availability_tooltip("{{ level }}", "{{ satellite }}", "{{ orbit_for_tooltip }}", "{{ completeness.start }}", "{{ completeness.stop }}", "{{ (completeness.duration / 60)|round(3) }}", "{{ status_for_tooltip }}", "{{ dhus_product_for_tooltip }}", "{{ delta_to_dhus_for_tooltip }}", "{{ size_for_tooltip }}", "{{ datatake_id }}", "{{ planned_imaging.start }}", "{{ planned_imaging.stop }}", "{{ (planned_imaging.duration / 60)|round(3) }}"),
    "className": "{{ class_name }}"
})
if (!("{{ level }}" in dhus_availability_data_timeliness_for_statistics)){
    dhus_availability_data_timeliness_for_statistics["{{ level }}"] = []
}
dhus_availability_data_timeliness_for_statistics["{{ level }}"].push({{ delta_to_dhus }})
{% endif %}

{% endfor %}
