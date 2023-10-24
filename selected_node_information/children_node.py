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
    Output('children_buttons', 'children'),
    Input(store_data.selected_node.store_id, 'data'),
    State('dataframe', 'data'),
    State('visit_threshold', 'value')
)
def update_children_button_list(selected_node, data, visit_threshold):
    if not selected_node:
        return ""

    children_buttons = []
    df = pd.read_json(data['file'])

    if not visit_threshold:
        visit_threshold = 1

    children = data_preprocessing.search_children_by_node_name(df, visit_threshold, selected_node['Name'])

    if not children:
        return dbc.Row("No children from this node", class_name='h-100 align-items-center justify-content-center')

    best_children = None
    worst_children = None

    children_df = df[df['Name'].isin(children)]
    children_df.sort_values("Visits")

    if len(children) > 1:
        children_df = df[df['Name'].isin(children)]
        max_children_val = children_df['Value'].max()
        min_children_val = children_df['Value'].min()

        if abs(max_children_val - min_children_val) >= 0.001:
            best_children = children_df[children_df['Value'] == max_children_val]['Name'].tolist()
            worst_children = children_df[children_df['Value'] == min_children_val]['Name'].tolist()

    for child in children:
        children_id = {'type': 'children_button', 'index': child}
        if best_children is None:
            children_buttons.append(dbc.Col(dbc.Button(child, size="sm", id=children_id), className="m-2"))
        else:
            if child in best_children:
                children_buttons.append(dbc.Col(dbc.Button(child, size="sm", id=children_id, color='success'),
                                                className="m-2"))
            elif child in worst_children:
                children_buttons.append(dbc.Col(dbc.Button(child, size="sm", id=children_id, color='danger'),
                                                className="m-2"))
            else:
                children_buttons.append(dbc.Col(dbc.Button(child, size="sm", id=children_id), className="m-2"))

    children_df['Name'] = children_buttons
    children_df = children_df[['Name', 'Visits', 'Value']]
    table = dbc.Table.from_dataframe(children_df, striped=True, bordered=True, hover=True)

    return dbc.Row(table, class_name='row-cols-auto g-1', justify='center')
