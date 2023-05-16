from dash import html, Input, Output, State
import dash_bootstrap_components as dbc
from utility import callback_manager, store_data, data_preprocessing, feature_explanation_generator
import pandas as pd
from utility import feature_explaination_helper_function

manager = callback_manager.CallbackManager()

###############################################
# Layout
###############################################
feature_explanation_card = dbc.Card([
    dbc.CardHeader(html.P("Explanation", className='m-0 fw-bold text-center text-primary'), class_name='py-3'),
    dbc.CardBody(dbc.Tabs([
        dbc.Tab(html.Div(id='feature_explanation_table'), label='Table'),
        dbc.Tab(html.Div(id='feature_explanation_heatmap'), label='HeatMap')
    ]))
], class_name='my-2 h-100')


###############################################
# Callbacks
###############################################
@manager.callback(
    Output(store_data.feature_explanation_df.store_id, 'data'),
    Input('feature_feature_column', 'value'),
    Input('feature_depth', 'value'),
    Input('feature_exclude_actions', 'value'),
    Input('feature_exclude_features', 'value'),
    State(store_data.df.store_id, 'data')
)
def feature_explanation_data_update(feature_col, feature_depth, exclude_actions, exclude_features, data):
    if feature_col is None or feature_depth is None or data['file'] is None:
        return {"df": None, "max_depth": 0}

    df = pd.read_json(data['file'])

    root_action_list = data_preprocessing.get_root_available_actions(df, exclude_actions)

    if root_action_list:
        table_df, maximum_depth = feature_explanation_generator.generate_feature_explanation_df(df, feature_depth,
                                                                                                exclude_actions,
                                                                                                exclude_features,
                                                                                                feature_col)

        return {"df": table_df.to_json(), "max_depth": maximum_depth}

    return {"df": None, "max_depth": 0}


@manager.callback(
    Output('feature_explanation_table', 'children'),
    Input(store_data.feature_explanation_df.store_id, 'data'),
)
def feature_explanation_table_update(feature_explanation_df_dict):
    table_df = feature_explanation_df_dict['df']
    maximum_depth = feature_explanation_df_dict['max_depth'] + 1

    if table_df is None:
        return []

    table_df = pd.read_json(feature_explanation_df_dict['df'])

    table_df.index = pd.MultiIndex.from_tuples(
        feature_explaination_helper_function.str_idx_to_tuple_idx(table_df.index), names=('Feature', 'Depth'))
    table_df.columns = pd.MultiIndex.from_tuples(
        feature_explaination_helper_function.str_idx_to_tuple_idx(table_df.columns))

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
