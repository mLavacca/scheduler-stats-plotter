#!/usr/bin/python3.7

import collections

import plotly
import plotly.graph_objects as go
import json

from plotly.subplots import make_subplots

plotly.io.orca.config.executable = '/home/mattia/anaconda3/bin/orca'

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

fig = make_subplots(
    rows=2, cols=2,
    vertical_spacing=0.2,
    horizontal_spacing=0.1,
    specs=[[{"secondary_y": True}, {"secondary_y": True}], [{"secondary_y": True}, {"secondary_y": True}]])

s = 49

for i in range(1, 2, 1):

    with open('/Users/mattialavacca/Desktop/trace' + str(i), 'r') as file:
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
        avg_total_node_cost_sorted = global_size/total_cost_sorted
    else:
        avg_total_node_cost = global_size/total_cost

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

    fig.add_trace(
        go.Bar(name='deployment_cost',
               x=names,
               y=list(node_costs.values()),
               text=list(job_size_messages.values()),
               textposition='auto'),
        row=1,
        col=i
    )

    fig.add_trace(
        go.Bar(name='edge_cost',
               x=names,
               y=list(edge_costs.values()),
               text=list(edge_size_messages.values()),
               textposition='auto'),
        row=1,
        col=i
    )

    fig.add_trace(
        go.Scatter(name="avg_job_cost",
                   x=names,
                   y=list(avg_node_costs.values()),
                   marker=dict(size=10,
                               color="mediumseagreen")),
        secondary_y=True,
        row=1,
        col=i
    )

    fig.add_trace(
        go.Scatter(name="avg_link_cost",
                   x=names,
                   y=list(avg_link_costs.values()),
                   marker=dict(size=10,
                               color="silver")),
        secondary_y=True,
        row=1,
        col=i
    )

    fig.add_trace(
        go.Bar(name='scheduling_time',
               x=names,
               y=list(scheduling_times.values()),
               text=list(cumulative_size_messages.values()),
               textposition='auto'),
        row=2,
        col=i
    )

    fig.add_trace(
        go.Scatter(name="avg_scheduling_time",
                   x=names,
                   y=list(avg_scheduling_times.values()),
                   marker=dict(size=10,
                               color="red")),
        row=2,
        col=i,
        secondary_y=True
    )

title = 'Federation size: ' + str(fed_size)
title += ' - Total cost heuristic: ' + f"{total_cost_sorted:.2f}" + ' k'
title += ' - Total cost brute: ' + f"{total_cost:.2f}" + ' k'

fig.update_layout(title_text="<b>DRONE SCHEDULER</b><br>" + title, barmode='group', hovermode='x')
fig.update_xaxes(row=1, col=1, title_text="Deployments")
fig.update_yaxes(row=1, col=1, type="log", title_text="<b>Cost (k)</b>", secondary_y=False)
fig.update_yaxes(row=1, col=1, title_text="<b>Avg cost</b>", secondary_y=True)

fig.update_xaxes(row=2, col=1, title_text="Deployments")
fig.update_yaxes(row=2, col=1, type="log", title_text="<b>Time (ms)</b>", secondary_y=False)
fig.update_yaxes(row=2, col=1, title_text="<b>Avg time (ms)</b>", secondary_y=True)

fig.update_xaxes(row=1, col=2, title_text="Deployments")
fig.update_yaxes(row=1, col=2, type="log", title_text="<b>Cost (k)</b>", secondary_y=False)
fig.update_yaxes(row=1, col=2, title_text="<b>Avg cost</b>", secondary_y=True)

fig.update_xaxes(row=2, col=2, title_text="Deployments")
fig.update_yaxes(row=2, col=2, type="log", title_text="<b>Time (ms)</b>", secondary_y=False)
fig.update_yaxes(row=2, col=2, title_text="<b>Avg time (ms)</b>", secondary_y=True)

fig.show()
