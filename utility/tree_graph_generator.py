import plotly
import json
import plotly.graph_objects as go
import networkx as nx
import plotly.express as px
from utility.attributes import get_attributes, get_legend_attributes
from utility import data_preprocessing
import numpy as np


def get_figure_object(fig):
    """
    Generate Plotly Figure object by json-format plotly figure or original figure
    :param fig: Dictionary or Figure Object
    :return: Figure
    """
    if type(fig) == dict:
        # fig = plotly.io.from_json(json.dumps(fig))
        fig['data'][1]['marker']['color'] = [color if color is not None else np.nan for color in fig['data'][1]['marker']['color']]
        return plotly.graph_objects.Figure(fig)
    return fig


def get_figure_custom_data_by_node_name(fig, node_name):
    fig = get_figure_object(fig)
    custom_data = fig.data[1]['customdata']

    for data in custom_data:
        if data['Name'] == node_name:
            return data
    return None


def highlight_selected_node(fig, df, node_name, visit_threshold):
    fig = get_figure_object(fig)
    custom_data = fig.data[1]['customdata']
    opacity = []
    sizes = []
    child_node_name = None

    children_list = data_preprocessing.get_node_available_actions(df, node_name)
    best_action_name = data_preprocessing.get_node(df, node_name)['Best_Action']

    for child in children_list:
        if best_action_name == data_preprocessing.get_node(df, child)['Action_Name']:
            child_node_name = child
            break

    for data in custom_data:
        if data['Name'] == node_name:
            opacity.append(1)
            sizes.append(20)
        else:
            if child_node_name is not None and data['Name'] == child_node_name:
                sizes.append(15)
            else:
                sizes.append(10)

            if data['Visits'] >= visit_threshold:
                opacity.append(0.6)
            else:
                opacity.append(0.2)

    fig.data[1].update(
        marker={"opacity": opacity,
                "size": sizes})
    return fig


def update_opacity(fig, threshold):
    fig = get_figure_object(fig)
    custom_data = fig.data[1]['customdata']
    fig.data[1].update(
        marker={"opacity": [1 if i['Visits'] >= threshold else 0.2 for i in custom_data], "size": [10 for _ in custom_data]})
    return fig


def generate_network(df):
    dag = nx.from_pandas_edgelist(df, source='Name', target='Parent_Name')
    dag.remove_node("None")

    # Change the position of node and edge
    pos = nx.nx_agraph.graphviz_layout(dag, prog='twopi')
    for n, p in pos.items():
        dag.nodes[n]['pos'] = p

    # Put the attributes of node into network
    attributes = get_attributes(df)
    for x in df["Name"]:
        dag.nodes[x]["Name"] = x
        if attributes:
            for attribute in attributes:
                dag.nodes[x][attribute] = df[df["Name"] == x][attribute].values[0]

    return dag


def get_edge_pos(graph):
    edge_x = []
    edge_y = []

    for edge in graph.edges():
        x0, y0 = graph.nodes[edge[0]]['pos']
        x1, y1 = graph.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    return edge_x, edge_y


def get_node_data(graph, df):
    node_x = []
    node_y = []
    custom_data = []
    attributes = get_attributes(df)

    for node in graph.nodes():
        x, y = graph.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

        data = {"Name": graph.nodes[node]['Name']}
        if attributes:
            for attribute in attributes:
                data[attribute] = graph.nodes[node][attribute]
        custom_data.append(data)

    return node_x, node_y, custom_data


def get_custom_data_by_node_name(fig, node_name):
    fig = get_figure_object(fig)
    custom_data = fig.data[1]['customdata']

    for data in custom_data:
        if data['Name'] == node_name:
            return data
    return None


def generate_fig(graph, df):
    edge_x, edge_y = get_edge_pos(graph)
    node_x, node_y, custom_data = get_node_data(graph, df)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_trace = go.Scatter(
        x=node_x, y=node_y, customdata=custom_data,
        mode='markers',
        marker=dict(
            showscale=True,
            colorscale='bluered',
            color=[],
            size=10,
            opacity=1,
            colorbar=dict(
                thickness=15,
                xanchor='left',
                titleside='right'
            ),
            line_width=1))

    node_trace.marker.color = [i['Depth'] for i in custom_data]

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )

    fig.update_traces(hoverinfo="none", hovertemplate=None)

    return fig


def generate_visit_threshold_network(df, threshold, legend=None, custom_symbols=None, min_visit_threshold=0):
    df = df[df['Visits'] >= min_visit_threshold]

    fig = generate_fig(generate_network(df), df)

    if legend:
        fig = update_legend(fig, df, legend, threshold)

    fig = update_marker_symbols(fig, custom_symbols)
    fig = update_opacity(fig, threshold)

    return fig


def update_legend(fig, df, legend_name, visit_threshold=None):
    fig = get_figure_object(fig)
    custom_data = fig.data[1]['customdata']

    _, object_type_legend_attributes = get_legend_attributes(df)

    if legend_name in object_type_legend_attributes:
        if visit_threshold:
            df = df[df['Visits'] >= visit_threshold]
        name_dict = {name: idx for idx, name in enumerate(df[legend_name].unique())}
        colorbar = dict(
            thickness=15,
            xanchor='left',
            titleside='right',
            tickvals=[i for i in list(name_dict.values())],
            ticktext=list(name_dict.keys())
        )
        color = [name_dict[i[legend_name]] if i['Visits'] >= visit_threshold else np.nan for i in custom_data]
        colorscale = []
        for val, template_color in zip(list(name_dict.values()), px.colors.qualitative.Light24):
            colorscale.append([float(val) / len(name_dict), f"rgb{plotly.colors.hex_to_rgb(template_color)}"])
            colorscale.append([float(val + 1) / len(name_dict), f"rgb{plotly.colors.hex_to_rgb(template_color)}"])
    else:
        colorbar = dict(
            thickness=15,
            xanchor='left',
            titleside='right',
            tickvals=None,
            ticktext=None
        )
        color = [i[legend_name] if i['Visits'] >= visit_threshold else np.nan for i in custom_data]
        colorscale = "bluered"

    fig.data[1].update(marker={"color": color, "colorscale": colorscale, "colorbar": colorbar})
    return fig


def update_marker_symbols(fig, markers_list=None):
    # update root node
    fig = get_figure_object(fig)
    custom_data = fig.data[1]['customdata']

    symbols = []

    for data in custom_data:
        if data['Parent_Name'] == "None":
            symbols.append("circle-x")
            continue

        if markers_list:
            has_find = False
            for feature, symbol in markers_list[::-1]:
                if data[feature] == 1:
                    symbols.append(symbol)
                    has_find = True
                    break
            if has_find:
                continue

        symbols.append("circle")

    fig.data[1].update(marker={"symbol": symbols})
    return fig
