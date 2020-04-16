import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

names = ['50 nodes', '100 nodes', '200 nodes', '500 nodes']
costs_heu = [83.49, 175.64, 269.51, 238.29]
costs_ran = [90.72, 190.23, 304.91, 307.40]

costs_diff = []

for i in range(0, 4, 1):
    costs_diff.append(costs_ran[i] - costs_heu[i])


fig = make_subplots(
    specs=[[{"secondary_y": True}]])

fig.add_trace(
        go.Scatter(name="total_heuristic_cost",
                   x=names,
                   y=costs_heu,
                   marker=dict(size=10,
                               color="blue")
                   )
)

fig.add_trace(
        go.Scatter(name="total_random_cost",
                   x=names,
                   y=costs_ran,
                   marker=dict(size=10,
                               color="red")
                   )
)

fig.add_trace(
    go.Scatter(name="cost_delta",
               x=names,
               y=costs_diff,
               marker=dict(size=10, color="silver"),
               line=dict(dash='dot')),
    secondary_y=True
)

fig.update_xaxes(title_text="Federation sizes")
fig.update_yaxes(title_text="<b>Cost (K)</b>")

pio.write_image(fig, 'images/total_costs.pdf')

