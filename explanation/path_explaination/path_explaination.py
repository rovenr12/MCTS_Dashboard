from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from utility import callback_manager, store_data, path_explanation_generator
import pandas as pd

manager = callback_manager.CallbackManager()

###############################################
# Layout
###############################################
path_explanation_card = dbc.Card([
    dbc.CardHeader(html.P("Explanation", className='m-0 fw-bold text-center text-primary'), class_name='py-3'),
    dbc.CardBody(id='path_explanation_card')
], class_name='my-2 h-100')


###############################################
# Callbacks
###############################################
@manager.callback(
    Output('path_explanation_card', 'children'),
    Input('path_feature_column', 'value'),
    Input('path_type', 'value'),
    Input('path_action_name', 'value'),
    Input('path_exclude_features', 'value'),
    State(store_data.df.store_id, 'data')
)
def path_explanation_update(feature_col, path_type, action_name, exclude_features, data):
    if feature_col is None or path_type is None or data['file'] is None:
        return None

    df = pd.read_json(data['file'])

    explanations = []

    if path_type == 'Best path vs Worse path':
        explanations = path_explanation_generator.explanation_by_paths(df, feature_col, exclude_features)
    elif path_type == 'Best action vs Second best action':
        explanations = path_explanation_generator.counterfactual_explanation_by_paths(df, None, exclude_features,
                                                                                      feature_col)
    elif path_type == 'Best action vs another action':
        explanations = path_explanation_generator.counterfactual_explanation_by_paths(df, action_name, exclude_features,
                                                                                      feature_col)

    return explanations
