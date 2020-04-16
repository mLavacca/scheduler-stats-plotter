#!/usr/bin/python3.7

import collections

import plotly
import plotly.graph_objects as go
import json
import plotly.io as pio

from plotly.subplots import make_subplots

node_sizes = {}
edge_sizes = {}
node_costs = {}
edge_costs = {}
node_resources = {}
scheduling_times = {}
avg_scheduling_times = {}

avg_total_node_cost_sorted = 0
avg_total_node_cost = 0

avg_job_sizes = {}
avg_link_costs = {}

job_size_messages = {}
edge_size_messages = {}

cumulative_size_messages = {}

global_size = 0

names = []
fed_size = 0
total_cost = 0
total_cost_sorted = 0

fig1 = make_subplots(
    specs=[[{"secondary_y": True}]])

fig2 = make_subplots(
    specs=[[{"secondary_y": True}]])

fig3 = make_subplots(
    specs=[[{"secondary_y": True}]])

fig4 = make_subplots(
    specs=[[{"secondary_y": True}]])

plotly.io.orca.config.executable = "/home/mattia/anaconda3/bin/orca"

s = 49

for i in range(1, 3, 1):

    with open('/home/mattia/Desktop/scheduling/schedulingResults/fedGraph' + str(s) + "/trace" + str(i), 'r') as file:
        data = file.read()
        d = json.loads(data)

    for item in d['updates']:

        metric_name = item['name']

        metric_name, depl_name = metric_name.split("{")
        depl_name = depl_name.split(",")[0]

        if len(item) == 2:
            if "federation" in depl_name:
                if "Size" in metric_name:
                    fed_size = item['last']

                if "Cost" in metric_name:
                    if i == 1:
                        total_cost_sorted = item['last'] / 1000
                    else:
                        total_cost = item['last'] / 1000
            else:
                if depl_name not in names:
                    names.append(depl_name)

                    node_sizes[depl_name] = {}
                    node_costs[depl_name] = {}

                    edge_sizes[depl_name] = {}
                    edge_costs[depl_name] = {}

                if "nodeSize" in metric_name:
                    node_sizes[depl_name] = item["last"]

                if "edgeSize" in metric_name:
                    edge_sizes[depl_name] = item["last"]

                if "nodesCost" in metric_name:
                    node_costs[depl_name] = float(f"{item['last']:.2f}")

                if "edgesCost" in metric_name:
                    edge_costs[depl_name] = float(f"{item['last'] / 1000:.2f}")

                if "nodesResources" in metric_name:
                    node_resources[depl_name] = float(f"{item['last']:.2f}")

        else:
            if "scheduleDeployment" in metric_name:
                scheduling_times[depl_name] = float(f"{item['min'] / 1000000:.2f}")

    avg_node_costs = {}
    for k, v in node_sizes.items():

        if k not in node_resources:
            avg_job_sizes[k] = 0
            avg_scheduling_times[k] = 0
            scheduling_times[k] = 0
        else:
            avg_job_sizes[k] = node_resources[k] / node_sizes[k]
            avg_job_sizes[k] = float(f"{avg_job_sizes[k]:.2f}")

            avg_scheduling_times[k] = (scheduling_times[k] / node_sizes[k]) / float(avg_job_sizes[k])
            avg_scheduling_times[k] = float(f"{avg_scheduling_times[k]:.4f}")

            global_size += node_resources[k] * node_sizes[k]

        if node_costs[k] == {}:
            avg_node_costs[k] = 0
        else:
            a = (node_costs[k] / node_sizes[k]) / float(avg_job_sizes[k])
            avg_node_costs[k] = (node_costs[k] / node_sizes[k]) / float(avg_job_sizes[k])
            avg_node_costs[k] = float(f"{avg_node_costs[k]:.3f}")
            node_costs[k] = node_costs[k] / 1000

        if edge_costs[k] == {}:
            avg_link_costs[k] = 0
        else:
            avg_link_costs[k] = edge_costs[k] / edge_sizes[k]
            avg_link_costs[k] = float(f"{avg_link_costs[k]:.3f}")

    if i == 1:
        avg_total_node_cost_sorted = global_size / total_cost_sorted
    else:
        avg_total_node_cost = global_size / total_cost

    names = sorted(names)
    node_sizes = collections.OrderedDict(sorted(node_sizes.items()))
    node_costs = collections.OrderedDict(sorted(node_costs.items()))
    edge_sizes = collections.OrderedDict(sorted(edge_sizes.items()))
    edge_costs = collections.OrderedDict(sorted(edge_costs.items()))
    avg_node_costs = collections.OrderedDict(sorted(avg_node_costs.items()))
    avg_link_costs = collections.OrderedDict(sorted(avg_link_costs.items()))
    avg_job_sizes = collections.OrderedDict(sorted(avg_job_sizes.items()))
    scheduling_times = collections.OrderedDict(sorted(scheduling_times.items()))
    avg_scheduling_times = collections.OrderedDict(sorted(avg_scheduling_times.items()))

    for k, v in node_sizes.items():
        job_size_messages[k] = str(v) + " jobs<br>" + str(avg_job_sizes[k]) + " units/job"

    for k, v in edge_sizes.items():
        edge_size_messages[k] = str(v) + " links<br>"

    for k, v in job_size_messages.items():
        cumulative_size_messages[k] = job_size_messages[k] + "<br>" + edge_size_messages[k]

    if i == 1:
        fig1.add_trace(
            go.Bar(name='deployment_cost',
                   x=names,
                   y=list(node_costs.values()),
                   text=list(job_size_messages.values()),
                   textposition='auto')
        )

        fig1.add_trace(
            go.Bar(name='edge_cost',
                   x=names,
                   y=list(edge_costs.values()),
                   text=list(edge_size_messages.values()),
                   textposition='auto')
        )

        fig1.add_trace(
            go.Scatter(name="avg_job_cost",
                       x=names,
                       y=list(avg_node_costs.values()),
                       marker=dict(size=10,
                                   color="mediumseagreen")),
            secondary_y=True
        )

        fig1.add_trace(
            go.Scatter(name="avg_link_cost",
                       x=names,
                       y=list(avg_link_costs.values()),
                       marker=dict(size=10,
                                   color="silver")),
            secondary_y=True
        )

        fig2.add_trace(
            go.Bar(name='scheduling_time',
                   x=names,
                   y=list(scheduling_times.values()),
                   text=list(cumulative_size_messages.values()),
                   textposition='auto')
        )

        fig2.add_trace(
            go.Scatter(name="avg_scheduling_time",
                       x=names,
                       y=list(avg_scheduling_times.values()),
                       marker=dict(size=10,
                                   color="red")),
            secondary_y=True
        )
    else:
        fig3.add_trace(
            go.Bar(name='deployment_cost',
                   x=names,
                   y=list(node_costs.values()),
                   text=list(job_size_messages.values()),
                   textposition='auto')
        )

        fig3.add_trace(
            go.Bar(name='edge_cost',
                   x=names,
                   y=list(edge_costs.values()),
                   text=list(edge_size_messages.values()),
                   textposition='auto')
        )

        fig3.add_trace(
            go.Scatter(name="avg_job_cost",
                       x=names,
                       y=list(avg_node_costs.values()),
                       marker=dict(size=10,
                                   color="mediumseagreen")),
            secondary_y=True
        )

        fig3.add_trace(
            go.Scatter(name="avg_link_cost",
                       x=names,
                       y=list(avg_link_costs.values()),
                       marker=dict(size=10,
                                   color="silver")),
            secondary_y=True
        )

        fig4.add_trace(
            go.Bar(name='scheduling_time',
                   x=names,
                   y=list(scheduling_times.values()),
                   text=list(cumulative_size_messages.values()),
                   textposition='auto')
        )

        fig4.add_trace(
            go.Scatter(name="avg_scheduling_time",
                       x=names,
                       y=list(avg_scheduling_times.values()),
                       marker=dict(size=10,
                                   color="red")),
            secondary_y=True
        )


title = 'Federation size: ' + str(fed_size)
title += ' - Total cost heuristic: ' + f"{total_cost_sorted:.2f}" + ' k'
title += ' - Total cost brute: ' + f"{total_cost:.2f}" + ' k'

fig1.update_xaxes(title_text="Deployments")
fig1.update_yaxes(title_text="<b>Cost (k)</b>", secondary_y=False)
fig1.update_yaxes(title_text="<b>Avg cost</b>", secondary_y=True)

fig2.update_xaxes(title_text="Deployments")
fig2.update_yaxes(title_text="<b>Time (ms)</b>", secondary_y=False)
fig2.update_yaxes(title_text="<b>Avg time (ms)</b>", secondary_y=True)

fig3.update_xaxes(title_text="Deployments")
fig3.update_yaxes(title_text="<b>Cost (k)</b>", secondary_y=False)
fig3.update_yaxes(title_text="<b>Avg cost</b>", secondary_y=True)

fig4.update_xaxes(row=2, col=2, title_text="Deployments")
fig4.update_yaxes(row=2, col=2, title_text="<b>Time (ms)</b>", secondary_y=False)
fig4.update_yaxes(row=2, col=2, title_text="<b>Avg time (ms)</b>", secondary_y=True)

pio.write_image(fig1, 'images/' + str(s+1) + '/fig1.pdf')
pio.write_image(fig2, 'images/' + str(s+1) + '/fig2.pdf')
pio.write_image(fig3, 'images/' + str(s+1) + '/fig3.pdf')
pio.write_image(fig4, 'images/' + str(s+1) + '/fig4.pdf')
