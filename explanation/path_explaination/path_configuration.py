from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from utility import callback_manager, store_data, attributes, data_preprocessing
import pandas as pd

manager = callback_manager.CallbackManager()

###############################################
# Layout
###############################################
# feature column config
path_feature_col_config = html.Div([
    dbc.Label("Features Column Name", html_for='path_feature_column', class_name='mb-1'),
    dbc.Select(id='path_feature_column')
], className='py-1')

# type config
path_type_config = html.Div([
    dbc.Label("Type", html_for='path_type', class_name='mb-1'),
    dbc.Select(id='path_type',
               options=[{"label": "Best path vs Worse path", "value": "Best path vs Worse path"},
                        {"label": "Best action vs Second best action", "value": "Best action vs Second best action"},
                        {"label": "Best action vs another action", "value": "Best action vs another action"}],
               value='Best path vs Worse path')
], className='py-1')

# action name config
path_action_name_config = html.Div([
    dbc.Label("Compare Action Name", html_for='path_action_name', class_name='mb-1'),
    dbc.Select(id='path_action_name', options=[])
], className='py-1', hidden=True, id='path_action_name_div')

# exclude features config
exclude_features_config = html.Div([
    dbc.Label("Exclude Features", html_for='path_exclude_features', class_name='mb-1'),
    dcc.Dropdown(id='path_exclude_features', options=[], multi=True)
], className='py-1')

path_configuration_card = dbc.Card([
    dbc.CardHeader(html.P("Configuration", className='m-0 fw-bold text-center text-primary'), class_name='py-3'),
    dbc.CardBody([
        path_feature_col_config,
        path_type_config,
        path_action_name_config,
        exclude_features_config
    ], id='path_configuration_card')
], class_name='my-2 h-100')


###############################################
# Callbacks
###############################################
@manager.callback(
    Output('path_feature_column', 'options'),
    Output('path_feature_column', 'value'),
    Input('path_explanation', 'hidden'),
    State(store_data.df.store_id, 'data')
)
def feature_column_name_reset(is_hidden, data):
    if is_hidden:
        return [], None

    df = pd.read_json(data['file'])

    path_attributes = attributes.get_numerical_json_type_attributes(df)
    path_value = path_attributes[0]

    if 'Game_Features' in path_attributes:
        path_value = 'Game_Features'

    path_options = [{"label": str(option), "value": option} for option in path_attributes]

    return path_options, path_value


@manager.callback(
    Output('path_type', 'value'),
    Input('path_explanation', 'hidden')
)
def path_type_reset(is_hidden):
    if is_hidden:
        return None

    return 'Best path vs Worse path'


@manager.callback(
    Output('path_action_name_div', 'hidden'),
    Input('path_type', 'value')
)
def hidden_action_name_config(path_type):
    return path_type != 'Best action vs another action'


@manager.callback(
    Output('path_action_name', 'options'),
    Output('path_action_name', 'value'),
    Input('path_action_name_div', 'hidden'),
    State('dataframe', 'data')
)
def update_action_name_config(is_hidden, data):
    if is_hidden:
        return [], None

    df = pd.read_json(data['file'])
    best_action = data_preprocessing.get_root_best_action(df)

    children = data_preprocessing.get_root_available_actions(df, [best_action], 'Action_Name')

    options = [{"label": str(child), "value": child} for child in children]

    return options, children[0]


@manager.callback(
    Output(component_id='path_exclude_features', component_property='options'),
    Output(component_id='path_exclude_features', component_property='value'),
    Input(component_id='path_feature_column', component_property='value'),
    State(component_id='dataframe', component_property='data')
)
def path_exclude_features_reset(feature_col, data):
    if feature_col is None:
        return [], None

    df = pd.read_json(data['file'])
    root_node_name = data_preprocessing.get_root_node_name(df)

    features = data_preprocessing.get_features(df, root_node_name, feature_col=feature_col)
    features = [{"label": str(feature), "value": feature} for feature in features]
    return features, []

