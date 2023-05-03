from dash import html, Input, Output, State
import dash_bootstrap_components as dbc
from utility import callback_manager, store_data, data_preprocessing, feature_explanation_generator
import pandas as pd

manager = callback_manager.CallbackManager()

###############################################
# Layout
###############################################
feature_explanation_card = dbc.Card([
    dbc.CardHeader(html.P("Explanation", className='m-0 fw-bold text-center text-primary'), class_name='py-3'),
    dbc.CardBody(id='feature_explanation_card')
], class_name='my-2 h-100')


###############################################
# Callbacks
###############################################
@manager.callback(
    Output('feature_explanation_card', 'children'),
    Input('feature_feature_column', 'value'),
    Input('feature_depth', 'value'),
    Input('feature_exclude_actions', 'value'),
    Input('feature_exclude_features', 'value'),
    State(store_data.df.store_id, 'data')
)
def path_explanation_update(feature_col, feature_depth, exclude_actions, exclude_features, data):
    if feature_col is None or feature_depth is None or data['file'] is None:
        return None

    df = pd.read_json(data['file'])

    root_action_list = data_preprocessing.get_root_available_actions(df, exclude_actions)

    if root_action_list:
        table_df, maximum_depth = feature_explanation_generator.generate_feature_explanation_df(df, feature_depth,
                                                                                                exclude_actions,
                                                                                                exclude_features,
                                                                                                feature_col)
        maximum_depth += 1
        table = dbc.Table.from_dataframe(table_df, bordered=True, hover=True, index=True,
                                         responsive=True, class_name='align-middle text-center')

        thead = table.children[0]
        first_tr = thead.children[0]
        first_tr.children[0].rowSpan = 2
        first_tr.children[0].className = "align-middle"
        first_tr.children[1].rowSpan = 2
        first_tr.children[1].className = "align-middle"
        second_tr = thead.children[1]
        second_tr.children.pop(0)
        second_tr.children.pop(0)

        tbody = table.children[1]
        tbody.className = " table-group-divider"

        visited_feature_name = []

        for idx, tr in enumerate(tbody.children):
            if tr.children[0].children not in visited_feature_name:
                visited_feature_name.append(tr.children[0].children)
                tr.children[0].rowSpan = maximum_depth
            else:
                tr.children.pop(0)
        return table

    return []
