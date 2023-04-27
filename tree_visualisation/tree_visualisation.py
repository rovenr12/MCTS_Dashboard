from utility import callback_manager, store_data, tree_graph_generator
from dash import html, dcc, Input, Output, State, ctx
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd


manager = callback_manager.CallbackManager()

###############################################
# Layout
###############################################
tree_visualisation_div = html.Div(dbc.Card([
    dbc.CardHeader(html.H4("Tree Visualisation", className='m-0 fw-bold text-center text-primary'), class_name='py-3'),
    dbc.CardBody([
        html.Div(dbc.Alert("Updating graph..."), hidden=True, id='graph_alert',
                 className='text-center position-absolute top-50 start-50 translate-middle w-75'),
        html.Div(dcc.Graph(id='tree_visualisation_graph', figure=go.Figure()), id='graph_holder', hidden=True)
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
    Output('graph_alert', 'hidden'),
    Output('graph_holder', 'hidden'),
    Input(store_data.df.store_id, 'data'),
    Input('tree_visualisation_graph', 'figure')
)
def graph_content_control(_, figure):
    # Updating the data, show the graph alert and hide the graph
    if ctx.triggered_id == 'dataframe':
        return False, True

    # There is no figure available, hide everything
    if not figure or not figure['data']:
        return True, True

    # There is figure available, hide the graph alert and show the graph
    return True, False


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
    Input('hover_text', 'value'),
    Input('legend', 'value'),
    Input(store_data.custom_symbols.store_id, 'data'),
    Input(store_data.selected_node.store_id, 'data'),
    State('visit_threshold', 'value'),
    State('tree_visualisation_graph', 'figure'),
    State(store_data.df.store_id, 'data'),
    State(store_data.fig_filename.store_id, 'data')
)
def tree_visualisation_update(hover_text, legend, custom_symbols, selected_node, visit_threshold, fig, data, fig_filename):
    # If there is no file, return empty figure and set fig_filename to None
    if not data['file']:
        return go.Figure(), None

    df = pd.read_json(data['file'])

    # If it is new data, change visit threshold or reset selected node because of visit threshold change,
    # regenerate the graph
    if data['file_id'] != fig_filename or (ctx.triggered_id == store_data.selected_node.store_id and not selected_node):
        if not visit_threshold:
            visit_threshold = 1
        return tree_graph_generator.generate_visit_threshold_network(df, visit_threshold, hover_text,
                                                                     legend, custom_symbols), data['file_id']

    # Update the selected_node
    if ctx.triggered_id == store_data.selected_node.store_id and selected_node:
        return tree_graph_generator.highlight_selected_node(fig, selected_node['Name']), fig_filename

    # Update the hover text
    if ctx.triggered_id == "hover_text":
        return tree_graph_generator.update_hover_text(fig, df, hover_text), fig_filename

    # Update the legend
    if ctx.triggered_id == "legend":
        return tree_graph_generator.update_legend(fig, df, legend, visit_threshold), fig_filename

    # Update the custom symbols
    if ctx.triggered_id == store_data.custom_symbols.store_id:
        return tree_graph_generator.update_marker_symbols(fig, custom_symbols), fig_filename

    return fig, fig_filename
