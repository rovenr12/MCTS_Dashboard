from dash import html, Input, Output
import dash_bootstrap_components as dbc
from utility import callback_manager, store_data


manager = callback_manager.CallbackManager()

###############################################
# Layout
###############################################
explanation_tabs = dbc.Tabs([
    dbc.Tab("Game Features", label='Game Features'),
    dbc.Tab("Path", label='Path')
])

explanation_card = html.Div(dbc.Card([
    dbc.CardHeader(html.H4("Root Action Explanation", className='m-0 fw-bold text-center text-primary'),
                   class_name='py-3'),
    dbc.CardBody([
        explanation_tabs
    ], style={'overflow-x': 'hidden', 'overflow-y': 'auto'})
]), className='my-2 shadow')

explanation_row = html.Div(dbc.Row([
    dbc.Col(explanation_card, lg='12', md='12', class_name='h-100'),
], class_name='g-3 mt-1 mb-4 px-3', style={'height': '700px'}), id='root_action_explanation_div', hidden=True)


###############################################
# Callbacks
###############################################
@manager.callback(
    Output('root_action_explanation_div', 'hidden'),
    Input(store_data.df.store_id, 'data')
)
def panel_control(data):
    return not data['file']

