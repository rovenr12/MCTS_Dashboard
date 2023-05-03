from dash import html, Input, Output
import dash_bootstrap_components as dbc
from utility import callback_manager, store_data, attributes
import pandas as pd
from explanation.feature_explaination import feature_configuration, feature_explaination

manager = callback_manager.CallbackManager()
manager += feature_configuration.manager
manager += feature_explaination.manager

###############################################
# Layout
###############################################
feature_explanation_contents_warning = html.Div(
    dbc.Alert("Not Available. Required At least one of json-format type column that contains only numerical values.",
              color="info"), hidden=True, id="feature_explanation_contents_warning")

feature_explanation_contents = html.Div([
    html.Div([
        dbc.Row([
            dbc.Col(feature_configuration.feature_configuration_card, lg='4', md='12'),
            dbc.Col(feature_explaination.feature_explanation_card, lg='8', md='12')
        ], class_name='g-3 mb-4 px-3 h-100'),
    ], id='feature_explanation', className='h-100'),
    feature_explanation_contents_warning
], className='my-2', style={"height": "750px"})


###############################################
# Callbacks
###############################################
@manager.callback(
    Output('feature_explanation', 'hidden'),
    Output('feature_explanation_contents_warning', 'hidden'),
    Input(store_data.df.store_id, 'data')
)
def panel_control(data):
    if not data['file']:
        return True, True

    df = pd.read_json(data['file'])

    path_attributes = attributes.get_numerical_json_type_attributes(df)

    is_available = len(path_attributes) != 0

    return not is_available, is_available
