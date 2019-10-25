"""
Templates and other static data for constructing the Mjolnir status website.
"""


SINGLEPAGE_TEMPLATE = """
_model: single-layout
---

show_home_nav: false
---
hero_title:
---
hero_description:
---
hero_image:
---
starting_block_bg: dark
---

main_content:

{content_blocks}
---

"""


DASHBOARD_SECTION_TEMPLATE = """
#### dashboard ####
section_id: {section_id}
----
title: {section_title}
----
description: {section_description}
----
nav_label: {section_nav_label}
----
widgets:

{widgets}
----
update_script:

{update_script}

"""


DASHBOARD_ITEM_TEMPLATE = """
##### widget #####
title: {plot_title}
-----
description: {plot_description}
-----
content:

<div id="{plot_id}" class="widget-container"></div>
-----

"""


DASHBOARD_SCRIPT_TEMPLATE = """
function convertNaN(value) {{
    if (value == {sentinel_value_json}) {{
        return NaN;
    }};
    return value;
}};


var plotConfig_{section_id} = {{
    editable: false,
    responsive: true,
    scrollzoom: false,
    staticplot: true,
    displayModeBar: false,
}};

var lastCheck_{section_id} = null;
var lastUpdate_{section_id} = null;
var maxLatency_{section_id} = 0;

var allPlots_{section_id} = {{
    {all_plots}
}};


Object.keys(allPlots_{section_id}).forEach(function(plotid) {{
    Plotly.newPlot(plotid, allPlots_{section_id}[plotid].data, allPlots_{section_id}[plotid].layout, plotConfig_{section_id});
}});

function updatePlot(allPlots, plotid, statusData) {{
    data = allPlots[plotid].updateFunction(allPlots, plotid, statusData);
    Plotly.restyle(plotid, data);
}};


var fastUpdatePlots_{section_id} = {fast_update_plots};

function fastUpdateStatus_{section_id}() {{
    if (fastUpdatePlots_{section_id}.length > 0 && lastCheck_{section_id} != null) {{
        for (i = 0; i < fastUpdatePlots_{section_id}.length; i++) {{
            updatePlot(allPlots_{section_id}, fastUpdatePlots_{section_id}[i], null);
        }};
    }};
}};

if (fastUpdatePlots_{section_id}.length > 0) {{
    setInterval(fastUpdateStatus_{section_id}, {update_interval_fast_seconds} * 1000);
}};


var xhrUpdate_{section_id} = new XMLHttpRequest();
xhrUpdate_{section_id}.onreadystatechange = function() {{
    if (this.readyState == XMLHttpRequest.DONE && this.status < 300 && this.status >= 200) {{
        var statusData = JSON.parse(this.responseText);
        Object.keys(allPlots_{section_id}).forEach(function(plotid) {{
            if (fastUpdatePlots_{section_id}.indexOf(plotid) == -1) {{
                updatePlot(allPlots_{section_id}, plotid, statusData);
            }};
        }});
    }};
}};

var xhrCheck_{section_id} = new XMLHttpRequest();
xhrCheck_{section_id}.onreadystatechange = function() {{
    if (this.readyState == XMLHttpRequest.DONE && this.status < 300 && this.status >= 200) {{
        var lastUpdateData = JSON.parse(this.responseText);
        var currentCheck = new Date(lastUpdateData.lastCheck);
        if (lastCheck_{section_id} == null || lastCheck_{section_id}.getTime() != currentCheck.getTime()) {{
            lastCheck_{section_id} = new Date(lastUpdateData.lastCheck);
            fastUpdateStatus_{section_id}();
            var currentUpdate = new Date(lastUpdateData.lastUpdate);
            if (lastUpdate_{section_id} == null || lastUpdate_{section_id}.getTime() != currentUpdate.getTime()) {{
                    lastUpdate_{section_id} = currentUpdate;
                    xhrUpdate_{section_id}.open("GET", "{data_path}", true);
                    xhrUpdate_{section_id}.send();
            }};
        }};
    }};
}};

function updateStatus_{section_id}() {{
    xhrCheck_{section_id}.open("GET", "{lastupdate_path}", true);
    xhrCheck_{section_id}.send();
}};

updateStatus_{section_id}();
setInterval(updateStatus_{section_id}, {update_interval_seconds} * 1000);

"""


DASHBOARD_PLOT_TEMPLATE = """
{plot_id}: {{
    data: [
        {{
            domain: {{ x: [0, 1], y: [0, 1] }},
            value: {gauge_value},
            type: "indicator",
            mode: "{plot_mode}",
            delta: {{
                decreasing: {{ color: "{decreasing_color}" }},
                increasing: {{ color: "{increasing_color}" }},
                reference: {delta_reference},
            }},
            gauge: {{
                axis: {{
                    automargin: true,
                    autotick: false,
                    color: "{plot_fgcolor}",
                    dtick: {dtick},
                    range: {range},
                    tick0: {tick0},
                    ticksuffix: "{suffix}",
                    tickangle: 0,
                    tickwidth: 1,
                }},
                bar: {{ color: "cyan" }},
                bgcolor: "{plot_fgcolor}",
                borderwidth: 0,
                bordercolor: "black",
                steps: [ {steps}],
                threshold: {{
                    line: {{ color: "black", width: 4 }},
                    thickness: {threshold_thickness},
                    value: {threshold_value},
                }},
            }},
            number: {{
                font: {{ color: "{number_color}" }},
                suffix: "{suffix}",
            }},
        }},
    ],
    layout: {{
        autosize: true,
        font: {{ color: "{plot_fgcolor}" }},
        height: 200,
        margin: {{ t: 25, b: 5, l: 50, r: 50 }},
        paper_bgcolor: "rgba(0, 0, 0, 0)",
        plot_bgcolor: "rgba(0, 0, 0, 0)",
        seperators: ". ",
    }},
    updateFunction: function(allPlots, plotid, statusData) {{
        data = {{}};
        {plot_update_code}
        return data;
    }},
}},

"""

GAUGE_PLOT_UPDATE_CODE_VALUE = """
data["value"] = convertNaN(statusData[plotid][0]);
data["delta.reference"] = convertNaN(statusData[plotid][1]);
data["gauge.threshold.value"] = convertNaN(statusData[plotid][2]);

"""

GAUGE_PLOT_UPDATE_CODE_COLOR = """
var foundStep = false;
var allSteps = allPlots[plotid].data[0].gauge.steps;
for (i = 0; i < allSteps.length; i++) {
    if (data["value"] >= allSteps[i].range[0] && data["value"] <= allSteps[i].range[1]) {
        data["number.font.color"] = allSteps[i].color;
        foundStep = true;
        break;
    };
};
if (! foundStep) {
    data["number.font.color"] = "white";
};

"""

GAUGE_PLOT_UPDATE_CODE = (GAUGE_PLOT_UPDATE_CODE_VALUE
                          + GAUGE_PLOT_UPDATE_CODE_COLOR)

GAUGE_PLOT_STEPS_TEMPLATE = "{{ range: [{begin}, {end}], color: '{color}' }},"


CONTENT_SECTION_TEMPLATE = """
#### content ####
section_id: {section_id}
----
title: {section_title}
----
description: {section_description}
----
nav_label: {section_nav_label}
----
full_width: {full_width}
----
button_content: {button_content}
----
button_type: {button_type}
----
button_link: {button_link}
----
button_position: {button_position}
----
button_newtab: {button_newtab}
----
content:

{content}

"""


TABLE_CONTENT_TEMPLATE = """
<div id="{section_id}-container" class="content-container table-content-container">
  <div id="{section_id}-output" class="content-output table-content-output"></div>
</div>

<script>
var colorMap_{section_id} = {color_map};

function getColor_{section_id}(dataValue) {{
    if (dataValue.row == dataValue.value) {{
        return "table-cell-header";
    }};
    if (dataValue.value == null) {{
        return "table-cell-null";
    }};
    if (! colorMap_{section_id}.hasOwnProperty(dataValue.{color_map_axis})) {{
        return "table-cell-nocolor";
    }};
    var colorScale = Plotly.d3.scale.threshold()
    .domain(colorMap_{section_id}[dataValue.{color_map_axis}][0])
    .range(colorMap_{section_id}[dataValue.{color_map_axis}][1]);
    return "table-cell-".concat(colorScale(dataValue.value));
}};

var lastUpdate_{section_id} = null;
var columns_{section_id} = {final_colnames};

var dataTable_{section_id} = Plotly.d3.select("#{section_id}-output").append("table");
var tableHeader_{section_id} = dataTable_{section_id}.append("thead");
var tableBody_{section_id} = dataTable_{section_id}.append("tbody");

function createTableElement(dataValue) {{
    if (dataValue.row == dataValue.value) {{
        return document.createElement("th");
    }};
    return document.createElement("td");
}};

var xhrCheck_{section_id} = new XMLHttpRequest();
xhrCheck_{section_id}.onreadystatechange = function() {{
    if (this.readyState == XMLHttpRequest.DONE && this.status < 300 && this.status >= 200) {{
        var lastUpdateData = JSON.parse(this.responseText);
        var currentUpdate = new Date(lastUpdateData.lastUpdate);
        if (lastUpdate_{section_id} == null || lastUpdate_{section_id}.getTime() != currentUpdate.getTime()) {{
            lastUpdate_{section_id} = currentUpdate;
            Plotly.d3.json("{data_path}", function(error, data) {{
                tableHeader_{section_id}.selectAll("*").remove();
                tableBody_{section_id}.selectAll("*").remove();
                tableHeader_{section_id}.append("tr")
                    .selectAll("th")
                    .data(columns_{section_id})
                    .enter()
                    .append("th")
                    .text(function (column) {{ return column; }});

                var rows = tableBody_{section_id}.selectAll("tr")
                    .data(data)
                    .enter()
                    .append("tr")

                var cells = rows.selectAll("td")
                    .data(function (row) {{
                        return columns_{section_id}.map(function (column) {{
                            return {{column: column, row: row[columns_{section_id}[0]], value: row[column]}};
                        }});
                    }})
                    .enter()
                    .append(createTableElement)
                    .attr("class", getColor_{section_id})
                    .text(function (d) {{ return d.value; }});
            }});
        }};
    }};
}};


function updateStatus_{section_id}() {{
    xhrCheck_{section_id}.open("GET", "{lastupdate_path}", true);
    xhrCheck_{section_id}.send();
}};

updateStatus_{section_id}();
setInterval(updateStatus_{section_id}, {update_interval_seconds} * 1000);
</script>

"""


TEXT_CONTENT_TEMPLATE = """
<div id="{section_id}-container" class="content-container text-content-container">
  <code id="{section_id}-output" class="content-output text-content-output"></code>
</div>

<script>
var lastUpdate_{section_id} = null;
var replaceItems = {replace_items};
var xhrUpdate_{section_id} = new XMLHttpRequest();
xhrUpdate_{section_id}.onreadystatechange = function() {{
    if (this.readyState == XMLHttpRequest.DONE && this.status < 300 && this.status >= 200) {{
        var outputText = this.responseText;
        outputText = outputText.replace(new RegExp("\\n", "g"), "\\n<br>\\n");
        for (i = 0; i < replaceItems.length; i++) {{
            var regexPattern = new RegExp(replaceItems[i][0], "g");
            outputText = outputText.replace(regexPattern, replaceItems[i][1]);
        }};
        var nodeToModify = document.getElementById("{section_id}-output");
        nodeToModify.innerHTML = outputText;
    }};
}};

var xhrCheck_{section_id} = new XMLHttpRequest();
xhrCheck_{section_id}.onreadystatechange = function() {{
    if (this.readyState == XMLHttpRequest.DONE && this.status < 300 && this.status >= 200) {{
        var lastUpdateData = JSON.parse(this.responseText);
        var currentUpdate = new Date(lastUpdateData.lastUpdate);
        if (lastUpdate_{section_id} == null || lastUpdate_{section_id}.getTime() != currentUpdate.getTime()) {{
            lastUpdate_{section_id} = currentUpdate;
            xhrUpdate_{section_id}.open("GET", "{data_path}", true);
            xhrUpdate_{section_id}.send();
        }};
    }};
}};


function updateStatus_{section_id}() {{
    xhrCheck_{section_id}.open("GET", "{lastupdate_path}", true);
    xhrCheck_{section_id}.send();
}};

updateStatus_{section_id}();
setInterval(updateStatus_{section_id}, {update_interval_seconds} * 1000);
</script>

"""


PLOT_CONTENT_TEMPLATE = """
<div id="{section_id}-container" class="content-container plot-content-container">
  <div id="{section_id}-output" class="content-output plot-content-output"></div>
</div>

<script>

function unpack(rows, key) {{
    return rows.map(function(row) {{ return row[key]; }});
}};

var plotConfig_{section_id} = {{
    editable: false,
    responsive: true,
    scrollzoom: true,
    staticplot: false,
}};

var lastUpdate_{section_id} = null;

var subplots_{section_id} = [
    {sub_plots}
];

plotLayout_{section_id} = {{
    autosize: true,
    font: {{ color: "{plot_fgcolor}" }},
    grid: {{
        columns: 1,
        rows: subplots_{section_id}.length,
        roworder: "top to bottom",
        subplots: [{subplots_list}],
        xgap: 0,
        ygap: {y_gap},
    }},
    height: {plot_height},
    hovermode: "compare",
    margin: {plot_margin},
    paper_bgcolor: "rgba(0, 0, 0, 0)",
    plot_bgcolor: "{plot_bgcolor}",
    seperators: ". ",
    showlegend: false,
    title: {{ text: "{plot_title}" }},
    xaxis: {{
        automargin: true,
        color: "{plot_fgcolor}",
        type: "{xaxis_type}",
    }},
    {y_axes}
    shapes: [
    {shape_list}
    ],
}};


var firstUpdate = true;

function createSubplots(plotid, subplotList, statusData) {{
    for (i = 0; i < subplotList.length; i++) {{
        subplotList[i].x = statusData.{x_variable};
        subplotList[i].y = statusData[subplotList[i].name];
    }};
    Plotly.newPlot(plotid, subplotList, plotLayout_{section_id}, plotConfig_{section_id});
}};

function updateSubplots(plotid, subplotList, statusData) {{
    for (i = 0; i < subplotList.length; i++) {{
        var data = {{}}
        data["x"] = statusData.{x_variable};
        data["y"] = statusData[subplotList[i].name];
        Plotly.restyle(plotid, data, i);
    }};
}};

var xhrUpdate_{section_id} = new XMLHttpRequest();
xhrUpdate_{section_id}.onreadystatechange = function() {{
    if (this.readyState == XMLHttpRequest.DONE && this.status < 300 && this.status >= 200) {{
        var statusData = JSON.parse(this.responseText);
        if (firstUpdate) {{
            createSubplots("{section_id}-output", subplots_{section_id}, statusData);
        }} else {{
            updateSubplots("{section_id}-output", subplots_{section_id}, statusData);
            firstUpdate = false;
        }};
    }};
}};

var xhrCheck_{section_id} = new XMLHttpRequest();
xhrCheck_{section_id}.onreadystatechange = function() {{
    if (this.readyState == XMLHttpRequest.DONE && this.status < 300 && this.status >= 200) {{
        var lastUpdateData = JSON.parse(this.responseText);
        var currentUpdate = new Date(lastUpdateData.lastUpdate);
        if (lastUpdate_{section_id} == null || lastUpdate_{section_id}.getTime() != currentUpdate.getTime()) {{
            lastUpdate_{section_id} = currentUpdate;
            xhrUpdate_{section_id}.open("GET", "{data_path}", true);
            xhrUpdate_{section_id}.send();
        }};
    }};
}};

function updateStatus_{section_id}() {{
    xhrCheck_{section_id}.open("GET", "{lastupdate_path}", true);
    xhrCheck_{section_id}.send();
}};

updateStatus_{section_id}()
setInterval(updateStatus_{section_id}, {update_interval_seconds} * 1000);
</script>

"""

SUBPLOT_DATA_TEMPLATE = """
{{
    type: "scatter",
    connectgaps: false,
    hoverinfo: "x+y+text",
    hoverlabel: {{
        bgcolor: "{plot_bgcolor}",
        font: {{ color: "{plot_fgcolor}" }},
    }},
    line: {{ color: "{plot_fgcolor}" }},
    mode: "lines",
    name: "{subplot_variable}",
    text: "{subplot_title}",
    xaxis: "x",
    x: [0,],
    yaxis: "y{idx}",
    y: [0,],
}},

"""

SUBPLOT_AXIS_TEMPLATE = """
yaxis{idx}: {{
    automargin: true,
    color: "{plot_fgcolor}",
    dtick: {dtick},
    range: {range},
    tick0: {tick0},
    ticksuffix: "{suffix}",
    title: {{ text: "{subplot_title}" }},
    type: "linear",
    zerolinecolor: "gray",
}},

"""

SHAPE_RANGE_TEMPLATE = """
{{
    type: "rect",
    fillcolor: "{color}",
    layer: "below",
    line: {{ width: 0 }},
    opacity: 0.15,
    xref: "paper",
    x0: 0,
    x1: 1,
    yref: "y{idx}",
    y0: {begin},
    y1: {end},
}},

"""
