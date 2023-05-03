from dash import html, Input, Output
import dash_bootstrap_components as dbc
from utility import callback_manager, store_data, attributes
from explanation.path_explaination import path_configuration, path_explaination
import pandas as pd

manager = callback_manager.CallbackManager()
manager += path_configuration.manager
manager += path_explaination.manager

###############################################
# Layout
###############################################
path_explanation_contents_warning = html.Div(dbc.Alert([
    "Not Available.", html.Br(),
    "Requirements:", html.Br(),
    "1). At least one of json-format type column that contains only numerical values", html.Br(),
    "2). The data need to have 'Best_Action' column that identify the best action of each node (Best_Action need to "
    "match the 'Action_Name')", html.Br(),
    "3). The data need to have 'Action_Name' column that identify the action name of each node"
], color="info"), hidden=True, id="path_explanation_contents_warning")

path_explanation_contents = html.Div([
    html.Div([
        dbc.Row([
            dbc.Col(path_configuration.path_configuration_card, lg='4', md='12'),
            dbc.Col(path_explaination.path_explanation_card, lg='8', md='12')
        ], class_name='g-3 mb-4 px-3 h-100'),
    ], id='path_explanation', className='h-100'),
    path_explanation_contents_warning
], className='my-2', style={"height": "750px"})


###############################################
# Callbacks
###############################################
@manager.callback(
    Output('path_explanation', 'hidden'),
    Output('path_explanation_contents_warning', 'hidden'),
    Input(store_data.df.store_id, 'data')
)
def panel_control(data):
    if not data['file']:
        return True, True

    df = pd.read_json(data['file'])

    path_attributes = attributes.get_numerical_json_type_attributes(df)

    is_available = len(path_attributes) != 0 and 'Best_Action' in df.columns and 'Action_Name' in df.columns

    return not is_available, is_available
