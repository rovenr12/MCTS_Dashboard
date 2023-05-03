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
    dbc.Label("Features Column Name", html_for='feature_feature_column', class_name='mb-1'),
    dbc.Select(id='feature_feature_column')
], className='py-1')

# type config
path_type_config = html.Div([
    dbc.Label("Depth Length", html_for='feature_depth', class_name='mb-1'),
    dbc.Select(id='feature_depth',
               options=[{"label": "Max", "value": "max"},
                        {"label": "Min", "value": "min"},
                        {"label": "Average", "value": "average"}],
               value='max')
], className='py-1')

# exclude action config
exclude_action_config = html.Div([
    dbc.Label("Exclude Features", html_for='feature_exclude_actions', class_name='mb-1'),
    dcc.Dropdown(id='feature_exclude_actions', options=[], multi=True)
], className='py-1')

# exclude features config
exclude_features_config = html.Div([
    dbc.Label("Exclude Features", html_for='feature_exclude_features', class_name='mb-1'),
    dcc.Dropdown(id='feature_exclude_features', options=[], multi=True)
], className='py-1')

feature_configuration_card = dbc.Card([
    dbc.CardHeader(html.P("Configuration", className='m-0 fw-bold text-center text-primary'), class_name='py-3'),
    dbc.CardBody([
        path_feature_col_config,
        path_type_config,
        exclude_action_config,
        exclude_features_config
    ], id='feature_configuration_card')
], class_name='my-2 h-100')


###############################################
# Callbacks
###############################################
@manager.callback(
    Output('feature_feature_column', 'options'),
    Output('feature_feature_column', 'value'),
    Input('feature_explanation', 'hidden'),
    State(store_data.df.store_id, 'data')
)
def feature_column_name_reset(is_hidden, data):
    if is_hidden:
        return [], None

    df = pd.read_json(data['file'])

    feature_attributes = attributes.get_numerical_json_type_attributes(df)
    feature_value = feature_attributes[0]

    if 'Game_Features' in feature_attributes:
        feature_value = 'Game_Features'

    feature_options = [{"label": str(option), "value": option} for option in feature_attributes]

    return feature_options, feature_value


@manager.callback(
    Output('feature_depth', 'value'),
    Input('feature_explanation', 'hidden')
)
def feature_depth_reset(is_hidden):
    if is_hidden:
        return None

    return 'max'


@manager.callback(
    Output('feature_exclude_actions', 'options'),
    Output('feature_exclude_actions', 'value'),
    Input('feature_explanation', 'hidden'),
    State('dataframe', 'data')
)
def exclude_action_config_update(is_hidden, data):
    if is_hidden:
        return [], None

    df = pd.read_json(data['file'])

    children = data_preprocessing.get_root_available_actions(df)

    options = [{"label": data_preprocessing.node_name_to_action_name(df, child), "value": child} for child in children]

    return options, None


@manager.callback(
    Output(component_id='feature_exclude_features', component_property='options'),
    Output(component_id='feature_exclude_features', component_property='value'),
    Input(component_id='feature_feature_column', component_property='value'),
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

