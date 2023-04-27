import dash_bootstrap_components as dbc
from dash import html
from utility import callback_manager
from selected_node_information.similar_nodes_methods import game_features

manager = callback_manager.CallbackManager()
manager += game_features.manager

###############################################
# Layout
###############################################
similar_nodes_card = dbc.Card([
    dbc.CardHeader(html.H6("Similar Nodes", className='m-0 fw-bold text-center text-primary'), class_name='py-3'),
    dbc.CardBody(dbc.Tabs([
        dbc.Tab(game_features.similar_nodes_game_features_div, label='Game Features'),
        dbc.Tab("Children", label='Path')
    ]), style={'overflow-y': 'auto', 'height': '500px'})
], class_name='mt-3')
