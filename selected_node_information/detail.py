import dash_bootstrap_components as dbc
from dash import html, Output, Input, State
from utility import callback_manager, store_data
from utility.attributes import get_attributes, get_json_type_attributes
import pandas as pd
import json

manager = callback_manager.CallbackManager()


####################################################
# Helper functions
####################################################
def json_content_builder(json_obj, container):
    for key, value in json_obj.items():
        if type(value) == list and type(value[0]) == dict:
            sub_list_group = dbc.ListGroup(children=[])
            for idx, child in enumerate(value, start=1):
                child_list_group = dbc.ListGroup(children=[])
                json_content_builder(child, child_list_group)
                sub_list_group.children.append(dbc.ListGroupItem([html.P(f"{key} {idx}", className='m-0 fw-bold'),
                                                                  child_list_group]))
            container.children.append(dbc.ListGroupItem([html.P(key, className='m-0 fw-bold'), sub_list_group]))
        else:
            if type(value) == list:
                item_list = html.Ul([])
                for v in value:
                    item_list.children.append(html.Li(html.Small(str(v))))
                container.children.append(dbc.ListGroupItem([html.P(key, className='m-0 fw-bold'), item_list]))
            else:
                container.children.append(
                    dbc.ListGroupItem([html.P(key, className='m-0 fw-bold'), html.Small(str(value))]))


###############################################
# Layout
###############################################
node_detail_card = dbc.Card([
    dbc.CardHeader(html.H6("Detail", className='m-0 fw-bold text-center text-primary'), class_name='py-3'),
    dbc.CardBody(id='node_information', style={'overflow-y': 'auto', 'height': '730px'})
], class_name='my-2')


###############################################
# Callbacks
###############################################
@manager.callback(
    Output(component_id='node_information', component_property='children'),
    Input(store_data.selected_node.store_id, 'data'),
    State(component_id='dataframe', component_property='data')
)
def update_node_information(selected_node, data):
    if not selected_node:
        return ""

    accordion = dbc.Accordion([], always_open=True, active_item=[])
    df = pd.read_json(data['file'])
    attributes = get_attributes(df)

    for attribute in attributes:
        if attribute == 'Name':
            continue
        elif attribute in get_json_type_attributes(df):
            game_state_json = json.loads(selected_node[attribute])
            list_group = dbc.ListGroup(children=[])
            json_content_builder(game_state_json, list_group)
            accordion.children.append(dbc.AccordionItem(list_group, title=attribute))
        else:
            accordion.children.append(dbc.AccordionItem(selected_node[attribute], title=attribute))

    return accordion
