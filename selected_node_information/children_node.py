import dash_bootstrap_components as dbc
from dash import html, Output, Input, State
from utility import callback_manager, store_data, data_preprocessing
import pandas as pd


manager = callback_manager.CallbackManager()


###############################################
# Layout
###############################################
children_nodes_card = dbc.Card([
    dbc.CardHeader(html.H6("Children", className='m-0 fw-bold text-center text-primary'), class_name='py-3'),
    dbc.CardBody(id='children_buttons', style={'overflow-y': 'auto', 'height': '200px'})
], class_name='my-2')


###############################################
# Callbacks
###############################################
@manager.callback(
    Output(component_id='children_buttons', component_property='children'),
    Input(store_data.selected_node.store_id, 'data'),
    State(component_id='dataframe', component_property='data'),
    State(component_id='visit_threshold', component_property='value')
)
def update_children_button_list(selected_node, data, visit_threshold):
    if not selected_node:
        return ""

    children_buttons = []
    df = pd.read_json(data['file'])

    if not visit_threshold:
        visit_threshold = 1

    for children in data_preprocessing.search_children_by_node_name(df, visit_threshold, selected_node['Name']):
        children_id = {'type': 'children_button', 'index': children}
        children_buttons.append(dbc.Col(dbc.Button(children, size="sm", id=children_id), className="m-2"))

    if not children_buttons:
        return dbc.Row("No children from this node", class_name='h-100 align-items-center justify-content-center')

    return dbc.Row(children_buttons, class_name='row-cols-auto g-1', justify='center')
