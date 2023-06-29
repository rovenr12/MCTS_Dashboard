from utility import callback_manager, store_data, tree_graph_generator
from dash import html, dcc, Input, Output, State, ctx, no_update
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
from PIL import Image
import base64
import io

manager = callback_manager.CallbackManager()

###############################################
# Layout
###############################################
tree_visualisation_div = html.Div(dbc.Card([
    dbc.CardHeader(html.H4("Tree Visualisation", className='m-0 fw-bold text-center text-primary'), class_name='py-3'),
    dbc.CardBody([
        html.Div([dcc.Graph(id='tree_visualisation_graph', figure=go.Figure(), clear_on_unhover=True),
                  dcc.Tooltip(id='tree_node_hover_text')
                  ])
    ], id='output-graph')
], class_name='h-100'), id='tree_visualisation', hidden=True, className='my-2 shadow', style={'height': '550px'})


###############################################
# Callbacks
###############################################
@manager.callback(
    Output('tree_visualisation', 'hidden'),
    Input(store_data.df.store_id, 'data')
)
def panel_control(data):
    return not (data and data['file'] is not None)


@manager.callback(
    Output('tree_visualisation_graph', 'clickData'),
    Input(store_data.df.store_id, 'data'),
    Input('visit_threshold', 'value')
)
def graph_click_data_reset(*args):
    return None


# graph generation
@manager.callback(
    Output('tree_visualisation_graph', 'figure'),
    Output('fig_filename', 'data'),
    Input('legend', 'value'),
    Input(store_data.custom_symbols.store_id, 'data'),
    Input(store_data.selected_node.store_id, 'data'),
    State('visit_threshold', 'value'),
    State('tree_visualisation_graph', 'figure'),
    State(store_data.df.store_id, 'data'),
    State(store_data.fig_filename.store_id, 'data')
)
def tree_visualisation_update(legend, custom_symbols, selected_node, visit_threshold, fig, data,
                              fig_filename):
    # If there is no file, return empty figure and set fig_filename to None
    if not data['file']:
        return go.Figure(), None

    df = pd.read_json(data['file'])

    # If it is new data, change visit threshold or reset selected node because of visit threshold change,
    # regenerate the graph
    if data['file_id'] != fig_filename or (ctx.triggered_id == store_data.selected_node.store_id and not selected_node):
        if not visit_threshold:
            visit_threshold = 1
        return tree_graph_generator.generate_visit_threshold_network(df, visit_threshold, legend, custom_symbols), data['file_id']

    # Update the selected_node
    if ctx.triggered_id == store_data.selected_node.store_id and selected_node:
        return tree_graph_generator.highlight_selected_node(fig, selected_node['Name']), fig_filename

    # Update the legend
    if ctx.triggered_id == "legend":
        return tree_graph_generator.update_legend(fig, df, legend, visit_threshold), fig_filename

    # Update the custom symbols
    if ctx.triggered_id == store_data.custom_symbols.store_id:
        return tree_graph_generator.update_marker_symbols(fig, custom_symbols), fig_filename

    return fig, fig_filename


@manager.callback(
    Output("tree_node_hover_text", "show"),
    Output("tree_node_hover_text", "bbox"),
    Output("tree_node_hover_text", "children"),
    Output("tree_node_hover_text", "direction"),
    Input("tree_visualisation_graph", "hoverData"),
    State('hover_text', 'value'),
)
def graph_click_data_reset(hoverData, hover_text):
    if not hoverData:
        return False, no_update, no_update, no_update

    pt = hoverData["points"][0]
    bbox = pt["bbox"]

    if 'customdata' not in pt:
        return False, no_update, no_update, no_update

    data = pt['customdata']

    elements = [html.H4(f"{data['Name']}", style={"color": "darkblue", "overflow-wrap": "break-word"})]

    if hover_text:
        for hover_attribute in hover_text:
            if hover_attribute == 'Image':
                byte_str = data['Image']
                decode_byte = base64.b64decode(byte_str)
                elements.insert(1, html.Div(html.Img(src=Image.open(io.BytesIO(decode_byte)), width='50%', style={'margin': 'auto'}),
                                            style={'display': 'flex', 'width': '100%'}))
            else:
                elements.append(html.P(f'{hover_attribute}: {data[hover_attribute]}',
                                       style={'overflow': 'hidden', 'white-space': 'nowrap', 'text-overflow': 'ellipsis'},
                                       className='m-0'))

    children = [html.Div(elements, style={'width': '60vh'})]

    direction = 'top' if bbox['y0'] > 400 else 'right'

    return True, bbox, children, direction

