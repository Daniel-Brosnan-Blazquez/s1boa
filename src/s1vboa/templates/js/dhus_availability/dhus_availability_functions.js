/* Function to create the text for the tooltip of the widgets */
function create_dhus_availability_tooltip(level, satellite, orbit, start, stop, duration, status, product, delta_to_dhus, size, datatake_id, datatake_start, datatake_stop, datatake_duration){

    
    
    var table = "<table border='1'>" +
        "<tr><td>Level</td><td>" + level + "</td></tr>" +
        "<tr><td>Satellite</td><td>" + satellite + "</td></tr>" +
        "<tr><td>Orbit</td><td>" + orbit + "</td></tr>" +
        "<tr><td>Start</td><td>" + start + "</td></tr>" +
        "<tr><td>Stop</td><td>" + stop + "</td></tr>" +
        "<tr><td>Duration (m)</td><td>" + duration + "</td></tr>" +
        "<tr><td>Status</td><td>" + status + "</td></tr>" +
        "<tr><td>Product</td><td>" + product + "</td></tr>"

    if (delta_to_dhus != "DISCARD"){
        table = table + "<tr><td>Time to DHUS publication (m)</td><td>" + delta_to_dhus + "</td></tr>"
    }
    
    if (size != "DISCARD"){
        table = table + "<tr><td>Size (GB)</td><td>" + size + "</td></tr>"
    }
    
    table = table + "<tr><td>Datatake id</td><td>" + datatake_id + "</td></tr>" +
        "<tr><td>Datatake start</td><td>" + datatake_start + "</td></tr>" +
        "<tr><td>Datatake stop</td><td>" + datatake_stop + "</td></tr>" +
        "<tr><td>Datatake duration(m)</td><td>" + datatake_duration + "</td></tr>" +
        "</table>"

    return table
};
