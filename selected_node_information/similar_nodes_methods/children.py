from dash import html, Output, Input, State
import dash_bootstrap_components as dbc
from utility import callback_manager, similarity, store_data, attributes, data_preprocessing
import pandas as pd

manager = callback_manager.CallbackManager()

###############################################
# Layout
###############################################
children_action_similarity_function = dbc.Select(
    id='children_action_similarity_function',
    options=[{'label': method, 'value': method} for method in similarity.set_similarity_function_dict],
    value=list(similarity.set_similarity_function_dict.keys())[0]
)

children_action_similarity_textbox = dbc.Input(type='number', id='children_action_similarity_threshold',
                                               value=1, min=0, max=1)

similar_nodes_children_action_accordion = html.Div([
    dbc.Accordion([
        dbc.AccordionItem([
            "Similarity Function", children_action_similarity_function,
            "Similarity Threshold", children_action_similarity_textbox
        ], id='similar_children_action_configuration', title='Configuration'),
        dbc.AccordionItem(id='similar_children_action_content', title='Nodes'),
    ], always_open=True, active_item=['item-0', 'item-1'], id='similar_children_action_accordion')
], id='similar_nodes_children_action_accordion', hidden=False)

similar_nodes_children_action_warning = html.Div(dbc.Alert("Not Available. Required Action_Name column.", color="info"),
                                                 hidden=True, id="similar_nodes_children_action_warning")

similar_nodes_children_action_div = html.Div([
    similar_nodes_children_action_accordion, similar_nodes_children_action_warning
], className='my-3')


###############################################
# Callbacks
###############################################
@manager.callback(
    Output('similar_nodes_children_action_accordion', 'hidden'),
    Output('similar_nodes_children_action_warning', 'hidden'),
    Input(store_data.selected_node.store_id, 'data'),
    State(store_data.df.store_id, 'data')
)
def children_layout_update(selected_node, df):
    if not selected_node:
        return True, True

    df = pd.read_json(df['file'])

    if 'Action_Name' not in attributes.get_attributes(df):
        return True, False

    return False, True


@manager.callback(
    Output('children_action_similarity_function', 'value'),
    Input(store_data.df.store_id, 'data')
)
def children_function_name_reset(_):
    return list(similarity.set_similarity_function_dict.keys())[0]


@manager.callback(
    Output('children_action_similarity_threshold', 'value'),
    Input(store_data.df.store_id, 'data')
)
def children_threshold_reset(_):
    return 1


@manager.callback(
    Output('similar_children_action_accordion', 'active_item'),
    Input(store_data.df.store_id, 'data')
)
def children_accordion_reset(_):
    return ['item-0', 'item-1']


@manager.callback(
    Output('similar_children_action_content', 'children'),
    Input('children_action_similarity_function', 'value'),
    Input('children_action_similarity_threshold', 'value'),
    Input('similar_nodes_game_features_accordion', 'hidden'),
    State(store_data.selected_node.store_id, 'data'),
    State(store_data.df.store_id, 'data'),
    State('visit_threshold', 'value')
)
def update_node_similar_game_feature_content(similarity_method, similarity_threshold, is_hidden,
                                             selected_node, data, visit_threshold):
    if is_hidden:
        return None

    if similarity_method is None or similarity_threshold is None:
        return None

    df = pd.read_json(data['file'])

    if not visit_threshold:
        visit_threshold = 1

    similar_nodes_by_children_action = data_preprocessing.search_similar_node_by_children_action(df, visit_threshold,
                                                                                                 selected_node['Name'],
                                                                                                 similarity_method,
                                                                                                 similarity_threshold)

    similar_nodes = []
    for children in similar_nodes_by_children_action:
        button_id = {'type': 'children_action_button', 'index': children}
        similar_nodes.append(dbc.Col(dbc.Button(children, size="sm", id=button_id), className="m-2"))

    return dbc.Row(similar_nodes, class_name='row-cols-auto g-1', justify='center')
