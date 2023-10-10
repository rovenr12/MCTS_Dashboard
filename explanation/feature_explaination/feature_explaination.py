from dash import html, Input, Output, State, dcc
import dash_bootstrap_components as dbc
from utility import callback_manager, store_data, data_preprocessing, feature_explanation_generator
import pandas as pd
from utility import feature_explaination_helper_function
import plotly.express as px
import plotly.graph_objects as go
from base64 import b64encode

manager = callback_manager.CallbackManager()

###############################################
# Layout
###############################################
feature_explanation_card = dbc.Card([
    dbc.CardHeader(html.P("Explanation", className='m-0 fw-bold text-center text-primary'), class_name='py-3'),
    dbc.CardBody(dbc.Tabs([
        dbc.Tab(html.Div(id='feature_explanation_table', className='my-2'), label='Table'),
        dbc.Tab(html.Div(id='feature_explanation_heatmap', className='my-2'), label='HeatMap'),
        dbc.Tab(html.Div(id='feature_explanation_text', className='my-2'), label='Text'),
    ]))
], class_name='my-2 h-100')


###############################################
# Callbacks
###############################################
@manager.callback(
    Output(store_data.feature_explanation_df.store_id, 'data'),
    Input('feature_feature_column', 'value'),
    Input('feature_depth', 'value'),
    Input('feature_include_actions', 'value'),
    Input('feature_exclude_features', 'value'),
    Input('feature_change_ratio', 'value'),
    State(store_data.df.store_id, 'data')
)
def feature_explanation_data_update(feature_col, feature_depth, include_actions, exclude_features, change_ratio, data):
    if feature_col is None or feature_depth is None or data['file'] is None or change_ratio is None:
        return {"df": None, "max_depth": 0}

    df = pd.read_json(data['file'])

    root_action_list = data_preprocessing.get_root_available_actions(df)
    exclude_actions = []

    if not change_ratio:
        change_ratio = 0

    if not exclude_features:
        exclude_features = []

    for root_action in root_action_list:
        if root_action in include_actions:
            continue
        exclude_actions.append(root_action)

    if include_actions:
        table_df, maximum_depth = feature_explanation_generator.generate_feature_explanation_df(df, feature_depth,
                                                                                                exclude_actions,
                                                                                                exclude_features,
                                                                                                feature_col,
                                                                                                change_ratio)

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

    table_df = feature_explaination_helper_function.json_feature_table_to_df(table_df)

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


@manager.callback(
    Output('feature_explanation_heatmap', 'children'),
    Input(store_data.feature_explanation_df.store_id, 'data'),
)
def feature_explanation_heatmap_update(feature_explanation_df_dict):
    table_df = feature_explanation_df_dict['df']
    maximum_depth = feature_explanation_df_dict['max_depth'] + 1

    if table_df is None:
        return []

    table_df = feature_explaination_helper_function.json_feature_table_to_df(table_df)

    action_names = table_df.columns.get_level_values(0)
    actions_dict = {}

    for action in action_names:
        if action in actions_dict:
            continue

        actions_dict[action] = {}
        action_features_df = table_df[action].T
        action_features_df = action_features_df.applymap(lambda x: float(x.split("%")[0]) if x else None)

        for i in range(maximum_depth):
            if i == 0:
                depth_df = action_features_df.iloc[:, action_features_df.columns.get_level_values(1) == 'Immediate']
            else:
                depth_df = action_features_df.iloc[:, action_features_df.columns.get_level_values(1) == str(i)]

            if depth_df.isnull().values.any():
                actions_dict[action][i] = None
            else:
                fig = px.imshow(depth_df.values, x=depth_df.columns.get_level_values(0), y=depth_df.index.to_list(),
                                text_auto='.2f', aspect="auto", color_continuous_scale="blues")
                fig.update_xaxes(tickangle=90)
                fig.update(layout_coloraxis_showscale=False)
                fig.update_xaxes(title='Feature')
                fig.update_yaxes(title='Root Relative Change')

                actions_dict[action][i] = dcc.Graph(figure=fig, style={'width': '700px', 'margin': 'auto'})


    actions_df = pd.DataFrame.from_dict(actions_dict)
    actions_df.rename(index={0: 'Immediate'}, inplace=True)

    table = dbc.Table.from_dataframe(actions_df, bordered=True, hover=True, index=True,
                                     responsive=True, class_name='align-middle text-center')

    table.children[0].children[0].children[0].children = 'Depth'

    return table


@manager.callback(
    Output('feature_explanation_text', 'children'),
    Input(store_data.feature_explanation_df.store_id, 'data'),
)
def feature_explanation_text_update(feature_explanation_df_dict):
    feature_df = feature_explanation_df_dict['df']

    if feature_df is None:
        return []

    feature_df = feature_explaination_helper_function.json_feature_table_to_df(feature_df)

    return feature_explanation_generator.generate_text_explanation(feature_df)
