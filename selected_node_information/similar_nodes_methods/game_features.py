from dash import html, Output, Input, State, dcc
import dash_bootstrap_components as dbc
from utility import callback_manager, similarity, store_data, attributes, data_preprocessing
import pandas as pd

manager = callback_manager.CallbackManager()

###############################################
# Layout
###############################################
game_feature_similarity_function = dbc.Select(
    id='game_feature_similarity_function',
    options=[{'label': method, 'value': method} for method in similarity.distance_similarity_function_dict],
    value=list(similarity.distance_similarity_function_dict.keys())[0]
)

game_feature_similarity_textbox = dbc.Input(type='number', id='game_feature_similarity_threshold', value=0, min=0)

similar_nodes_game_features_accordion = html.Div([
    dbc.Accordion([
        dbc.AccordionItem([
            "Similarity Function", game_feature_similarity_function,
            "Similarity Threshold", game_feature_similarity_textbox,
            "Exclude Features", dcc.Dropdown(id='similar_game_features_exclude', options=[], multi=True)
        ], id='similar_game_features_configuration', title='Configuration'),
        dbc.AccordionItem(id='similar_game_features_content', title='Nodes'),
    ], always_open=True, active_item=['item-0', 'item-1'], id='similar_game_features_accordion')
], id="similar_nodes_game_features_accordion", hidden=True)

similar_nodes_game_features_warning = html.Div(id="similar_nodes_game_features_warning")

similar_nodes_game_features_div = html.Div([
    similar_nodes_game_features_accordion, similar_nodes_game_features_warning
], className='my-2')


###############################################
# Callbacks
###############################################
@manager.callback(
    Output('similar_nodes_game_features_accordion', 'hidden'),
    Output('similar_nodes_game_features_warning', 'children'),
    Input(store_data.selected_node.store_id, 'data'),
    State(store_data.df.store_id, 'data')
)
def game_feature_layout_update(selected_node, df):
    if not selected_node:
        return True, None

    df = pd.read_json(df['file'])

    if 'Game_Features' not in attributes.get_attributes(df):
        return True, dbc.Alert("Not Available. Required Game_Features column", color="info")

    if 'Game_Features' not in attributes.get_numerical_json_type_attributes(df):
        return True, dbc.Alert("Not Available. Game_Features column only can contain numerical value", color="info")

    return False, None


@manager.callback(
    Output('game_feature_similarity_function', 'value'),
    Input(store_data.df.store_id, 'data')
)
def game_feature_function_name_reset(_):
    return list(similarity.distance_similarity_function_dict.keys())[0]


@manager.callback(
    Output('game_feature_similarity_threshold', 'value'),
    Input(store_data.df.store_id, 'data')
)
def game_feature_threshold_reset(_):
    return 0


@manager.callback(
    Output('similar_game_features_accordion', 'active_item'),
    Input(store_data.df.store_id, 'data')
)
def game_feature_accordion_reset(_):
    return ['item-0', 'item-1']


@manager.callback(
    Output('similar_game_features_exclude', 'options'),
    Output('similar_game_features_exclude', 'value'),
    Input(store_data.df.store_id, 'data')
)
def game_feature_exclude_reset(data):
    if not data['file']:
        return [], []

    df = pd.read_json(data['file'])

    if 'Game_Features' not in attributes.get_attributes(df):
        return [], []

    root_name = data_preprocessing.get_root_node_name(df)

    return list(data_preprocessing.get_features(df, root_name).keys()), []


@manager.callback(
    Output('similar_game_features_content', 'children'),
    Input('game_feature_similarity_function', 'value'),
    Input('game_feature_similarity_threshold', 'value'),
    Input('similar_game_features_exclude', 'value'),
    Input('similar_nodes_game_features_accordion', 'hidden'),
    State(store_data.selected_node.store_id, 'data'),
    State(store_data.df.store_id, 'data'),
    State('visit_threshold', 'value')
)
def update_node_similar_game_feature_content(similarity_method, similarity_threshold, exclude_features, is_hidden,
                                             selected_node, data, visit_threshold):
    if is_hidden:
        return None

    df = pd.read_json(data['file'])

    if not visit_threshold:
        visit_threshold = 1

    similar_nodes_by_features = data_preprocessing.search_similar_node_by_features(df, visit_threshold,
                                                                                   selected_node['Name'],
                                                                                   similarity_method,
                                                                                   similarity_threshold,
                                                                                   exclude_features)

    similar_nodes = []
    for children in similar_nodes_by_features:
        button_id = {'type': 'game_feature_button', 'index': children}
        similar_nodes.append(dbc.Col(dbc.Button(children, size="sm", id=button_id), className="m-2"))

    return dbc.Row(similar_nodes, class_name='row-cols-auto g-1', justify='center')
