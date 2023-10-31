from dash import html, Output, Input, ALL, ctx, State
import dash_bootstrap_components as dbc
from utility import callback_manager, store_data, tree_graph_generator
from selected_node_information import detail, children_node, similar_nodes_panel, image
from dash._utils import AttributeDict

manager = callback_manager.CallbackManager()
manager += detail.manager
manager += children_node.manager
manager += similar_nodes_panel.manager
manager += image.manager

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
            dbc.Col(image.node_image_card, id='select_node_img_col', lg='4', md='12', style={'display': 'none'}),
            dbc.Col(detail.node_detail_card, id='select_node_detail_col', lg='4', md='12'),
            dbc.Col(html.Div([children_node.children_nodes_card, similar_nodes_panel.similar_nodes_card]),
                    id='select_node_related_node_col', lg='4', md='12'),
        ], class_name='g-3')
    ], className='p-0 m-0'))
]), className='my-2 shadow')

selected_node_info_row = html.Div(dbc.Row([
    dbc.Col(selected_node_info_card, lg='12', md='12',
            class_name='h-100'),
], class_name='g-3 mb-4 px-3', style={'height': '900px'}), id='selected_node_info_div',
    hidden=True, style={'height': '900px', 'overflow-x': 'hidden'})


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
    Output('select_node_img_col', 'style'),
    Input(store_data.selected_node.store_id, 'data')
)
def img_col_style_change(data):
    if not data or 'Image' not in data:
        return {'display': 'none'}

    return {'display': 'block'}


@manager.callback(
    Output('select_node_related_node_col', 'lg'),
    Output('select_node_detail_col', 'lg'),
    Input(store_data.selected_node.store_id, 'data')
)
def col_size_change(data):
    if data and 'Image' in data:
        return 4, 4

    return 6, 6


@manager.callback(
    Output(store_data.selected_node.store_id, 'data'),
    Input('tree_visualisation_graph', 'clickData'),
    Input({'type': 'children_button', 'index': ALL}, 'n_clicks'),
    Input({'type': 'game_feature_button', 'index': ALL}, 'n_clicks'),
    Input({'type': 'children_action_button', 'index': ALL}, 'n_clicks'),
    State(store_data.selected_node.store_id, 'data'),
    State('tree_visualisation_graph', 'figure')
)
def selected_node_store_update(click_data, children_buttons, feature_buttons,
                               children_action_buttons, selected_node, fig):
    if ctx.triggered_id == "tree_visualisation_graph":
        if not click_data:
            return None

        if 'customdata' not in click_data['points'][0]:
            return None

        return click_data['points'][0]['customdata']

    if type(ctx.triggered_id) == AttributeDict:
        if ctx.triggered_id['type'] == 'children_button' and 1 in children_buttons:
            return tree_graph_generator.get_figure_custom_data_by_node_name(fig, ctx.triggered_id['index'])
        elif ctx.triggered_id['type'] == 'game_feature_button' and 1 in feature_buttons:
            return tree_graph_generator.get_figure_custom_data_by_node_name(fig, ctx.triggered_id['index'])
        elif ctx.triggered_id['type'] == 'children_action_button' and 1 in children_action_buttons:
            return tree_graph_generator.get_figure_custom_data_by_node_name(fig, ctx.triggered_id['index'])

    return selected_node


@manager.callback(
    Output('select_node_badge', 'children'),
    Input(store_data.selected_node.store_id, 'data'),
)
def selected_node_badge_update(select_node):
    if select_node:
        return html.Span(dbc.Badge(select_node['Name'], color='primary', className="ms-2", pill=True))

    return None
