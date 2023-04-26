from dash import html, Output, Input, ALL, ctx, State
import dash_bootstrap_components as dbc
from utility import callback_manager, store_data, tree_graph_generator
from selected_node_information import detail, children_node
from dash._utils import AttributeDict

manager = callback_manager.CallbackManager()
manager += detail.manager
manager += children_node.manager

###############################################
# Layout
###############################################
selected_node_info_card = html.Div(dbc.Card([
    dbc.CardHeader([
        html.H4(["Selected Node Information", html.Span(id='select_node_badge')],
                className='m-0 fw-bold text-center text-primary'),
    ], class_name='py-3'),
    dbc.CardBody(html.Div([
        dbc.Row([
            dbc.Col(detail.node_detail_card, lg='6', md='12'),
            dbc.Col(html.Div([children_node.children_nodes_card, "Similar Nodes"]), lg='6', md='12'),
        ], class_name='g-3')
    ], className='p-0 m-0', style={'overflow-x': 'hidden', 'overflow-y': 'auto'}))
]), className='my-2 shadow')

selected_node_info_row = html.Div(dbc.Row([
    dbc.Col(selected_node_info_card, lg='12', md='12',
            class_name='h-100'),
], class_name='g-3 mb-4 px-3', style={'height': '800px'}), id='selected_node_info_div', hidden=True)


###############################################
# Callbacks
###############################################
@manager.callback(
    Output('selected_node_info_div', 'hidden'),
    Input(store_data.selected_node.store_id, 'data')
)
def panel_control(data):
    return not data


@manager.callback(
    Output(store_data.selected_node.store_id, 'data'),
    Input('tree_visualisation_graph', 'clickData'),
    Input({'type': 'children_button', 'index': ALL}, 'n_clicks'),
    State('tree_visualisation_graph', 'figure')
)
def selected_node_store_update(click_data, _, fig):
    if ctx.triggered_id == "tree_visualisation_graph":
        if not click_data:
            return None

        if 'customdata' not in click_data['points'][0]:
            return None

        return click_data['points'][0]['customdata']

    if type(ctx.triggered_id) == AttributeDict:
        if ctx.triggered_id['type'] == "children_button":
            return tree_graph_generator.get_figure_custom_data_by_node_name(fig, ctx.triggered_id['index'])

    return None


@manager.callback(
    Output('select_node_badge', 'children'),
    Input(store_data.selected_node.store_id, 'data'),
)
def selected_node_badge_update(select_node):
    if select_node:
        return html.Span(dbc.Badge(select_node['Name'], color='primary', className="ms-2", pill=True))

    return None
