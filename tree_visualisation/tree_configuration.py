import io
import base64
import os
import random
import pandas as pd
from utility import store_data, callback_manager, data_preprocessing, attributes
from dash import html, dcc, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc

manager = callback_manager.CallbackManager()

CUSTOM_SYMBOL_LIST = ['circle-open', 'circle-dot', 'circle-open-dot',
                      'square', 'square-open', 'square-dot', 'square-open-dot',
                      'diamond', 'diamond-open', 'diamond-dot', 'diamond-open-dot',
                      'x', 'x-open', 'x-dot', 'x-open-dot',
                      'star', 'star-open', 'star-dot', 'star-open-dot']

###############################################
# Layout
###############################################
upload_file_layout = html.Div([
    dbc.Label('MCTS file', html_for='upload_file_upload', class_name='mb-1'),
    dcc.Upload([
        dbc.Button('Upload File', outline=True, color='primary', className='mb-2', id='upload_file_button'),
        dbc.Popover([
            dbc.PopoverHeader('MCTS File Requirement', class_name='bg-info'),
            dbc.PopoverBody('The MCTS file needs to be a csv file and seperated by "\\t". The file also needs to ' +
                            'have following columns at least: Name, Parent_Name, Depth, Value, Visit, Action_Name and '
                            'Best_Action')
        ], target='upload_data_button', trigger='hover')
    ], id='upload_file_upload'),
    html.Div(id='upload_file_output'),
], className='py-1')

hover_text_layout = html.Div([
    dbc.Label('Node Hover Text', html_for='hover_text', class_name='mb-1'),
    dcc.Dropdown(id='hover_text', options=[], multi=True)
], className='py-1')

legend_layout = html.Div([
    dbc.Label('Legend', html_for='legend', class_name='mb-1'),
    dbc.Select(id='legend', options=['Depth'], value='Depth'),
    dbc.Popover([
        dbc.PopoverHeader('Categorical Legend Limitation', class_name='bg-info'),
        dbc.PopoverBody('Only available to set the categorical data as a legend if it contains less than 24 unique '
                        'values')
    ], target='legend', trigger='hover')
], className='py-1')

visit_threshold_layout = html.Div([
    dbc.Label('Visit Threshold', html_for='visit_threshold', class_name='mb-1'),
    dbc.Input(id='visit_threshold', min=1, max=20, value=1, step=1, type='number'),
    dbc.FormText('Type number between 1 to 20', id='visit_threshold_form_text')
], className='py-1')

add_symbol_layout = dbc.Row([
    dbc.Col(dbc.Select(id='custom_symbol_attribute'), width=5, class_name='pe-1'),
    dbc.Col(dbc.Select(id='custom_symbol_selection'), width=5, class_name='ps-1'),
    dbc.Col(dbc.Button('+', id='custom_symbol_button', size='sm'), width=2,
            class_name='d-flex align-items-center justify-content-end')
], class_name='py-1')

custom_symbols_layout = html.Div([
    html.P('Custom Node Symbols', className='mb-0'),
    html.Div(add_symbol_layout, id='custom_symbol_add_div'),
    html.Div(id='selected_custom_symbols_div')
], id='custom_symbols_div')

node_configuration = html.Div([
    hover_text_layout,
    legend_layout,
    visit_threshold_layout,
    custom_symbols_layout
], id='node_config', hidden=True, className='py-1')

configuration_card = dbc.Card([
    dbc.CardHeader(html.H4('Configurations', className='m-0 fw-bold text-center text-primary'), class_name='py-3'),
    dbc.CardBody([
        node_configuration,
        upload_file_layout
    ], style={'overflow-y': 'auto'})
], class_name='my-2 shadow', style={'height': '550px'})


###############################################
# Callbacks
###############################################
@manager.callback(
    Output('node_config', 'hidden'),
    Input(store_data.df.store_id, 'data'),
)
def hide_node_config(data):
    return data['file_id'] is None


@manager.callback(
    Output('upload_file_output', 'children'),
    Output(store_data.df.store_id, 'data'),
    Input('url', 'pathname'),
    Input('upload_file_upload', 'contents'),
    State('upload_file_upload', 'filename'),
    State(store_data.df.store_id, 'data'),
    prevent_initial_call=True
)
def upload_file(pathname, contents, filename, original_data):
    if ctx.triggered_id == "upload_file_upload":
        if not contents:
            return '', original_data

        # Get data
        decoded = base64.b64decode(contents.split(',')[1])
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep='\t')

    else:
        pathname = pathname[1:]
        pathname.replace("\\", "/")
        filepath = f"data/{pathname}"
        if not pathname:
            return '', original_data

        if not os.path.exists(filepath):
            alert = dbc.Alert(f'{pathname} is not existed!!', color='danger', dismissable=True)
            return alert, {'file_id': None, 'file': None}

        # Get data
        df = pd.read_csv(filepath, sep='\t')
        filename = pathname

    # Check the data validity.
    if not data_preprocessing.check_df_validity(df):
        alert = dbc.Alert(f'{filename} is invalid!!', color='danger', dismissable=True)
        return alert, {'file_id': None, 'file': None}

    # Create a unique filename
    file_id = f'{filename}_{random.randint(0, 999999):06d}'

    alert = dbc.Alert(f'{filename} has uploaded successfully!!', color='success', dismissable=True)
    return alert, {'file_id': file_id, 'file': df.to_json()}


@manager.callback(
    Output('hover_text', 'options'),
    Output('hover_text', 'value'),
    Input('node_config', 'hidden'),
    State(store_data.df.store_id, 'data')
)
def hover_text_update(is_hidden, data):
    # If the configuration is hidden or there is no data, set the options and value to None
    if is_hidden or not data['file']:
        return [], None

    # Load the dataframe
    df = pd.read_json(data['file'])

    # Get the attribute list and add it to hover_options
    attribute_list = attributes.get_attributes(df)
    hover_options = [{'label': attribute, 'value': attribute} for attribute in attribute_list if attribute != 'Name']

    return hover_options, None


@manager.callback(
    Output('legend', 'options'),
    Output('legend', 'value'),
    Input('node_config', 'hidden'),
    State(store_data.df.store_id, 'data')
)
def legend_select_update(is_hidden, data):
    # If the configuration is hidden or there is no data, set the options and value to None
    if is_hidden or not data['file']:
        return [], None

    # Load the dataframe
    df = pd.read_json(data['file'])

    # Get the legend attribute list and add it to legend options
    legend_attributes, _ = attributes.get_legend_attributes(df)
    legend_options = [{'label': attribute, 'value': attribute} for attribute in legend_attributes if attribute != 'Name']

    return legend_options, 'Depth'


@manager.callback(
    Output('visit_threshold', 'min'),
    Output('visit_threshold', 'max'),
    Output('visit_threshold', 'value'),
    Input('node_config', 'hidden'),
    State(store_data.df.store_id, 'data')
)
def visit_threshold_input_update(is_hidden, data):
    # If the configuration is hidden or there is no data, set the options and value to None
    if is_hidden or not data['file']:
        return 1, 1, 1

    # Load the dataframe
    df = pd.read_json(data['file'])

    visit_minimum = 1

    while df.shape[0] > 500:
        visit_minimum += 1
        df = df[df['Visits'] >= visit_minimum]

    # Find the maximum value
    visit_maximum = df['Visits'].max()

    return visit_minimum, visit_maximum, visit_minimum


@manager.callback(
    Output('visit_threshold_form_text', 'children'),
    Input('visit_threshold', 'min'),
    Input('visit_threshold', 'max')
)
def set_visit_threshold_placeholder(min_val, max_val):
    return f'Type number between {min_val} and {max_val}. The maximum number of nodes is 500.'


@manager.callback(
    Output('custom_symbol_button', 'n_clicks'),
    Input('node_config', 'hidden')
)
def reset_custom_symbol_button_update(_):
    return 0


@manager.callback(
    Output('custom_symbols_div', 'hidden'),
    Input('custom_symbol_add_div', 'hidden'),
    Input(store_data.custom_symbols.store_id, 'data'),
)
def hide_custom_symbols_div(add_custom_symbol_is_hidden, custom_symbols):
    # If there is any custom symbol can be added, don't need to hide the custom symbols div
    if not add_custom_symbol_is_hidden:
        return False

    # If there is no custom symbol can be added and there is nothing in custom symbols, hide the custom symbols div
    if custom_symbols is None or len(custom_symbols) == 0:
        return True

    return False


@manager.callback(
    Output('custom_symbol_attribute', 'options'),
    Output('custom_symbol_attribute', 'value'),
    Output('custom_symbol_selection', 'options'),
    Output('custom_symbol_selection', 'value'),
    Output('custom_symbol_add_div', 'hidden'),
    Input(store_data.custom_symbols.store_id, 'data'),
    State(store_data.df.store_id, 'data')
)
def set_add_custom_symbol_configuration(custom_symbols, data):
    # If there is no data available, set everything to None and don't show the custom symbols div
    if not data['file']:
        return [], None, [], None, True

    df = pd.read_json(data['file'])

    # Get the list of attributes can be used as symbol
    available_attributes = attributes.get_binary_attributes(df)
    available_symbols = CUSTOM_SYMBOL_LIST.copy()

    # If there is any selected symbols and attributes, remove it from the add options
    if custom_symbols:
        for selected_attribute, symbol in custom_symbols:
            available_attributes.remove(selected_attribute)
            available_symbols.remove(symbol)

    # If there is nothing can be added, set everything to None and don't show the custom symbols div
    if len(available_attributes) == 0:
        return [], None, [], None, True

    available_attributes = [{'label': attribute, 'value': attribute} for attribute in available_attributes]
    available_symbols = [{'label': attribute, 'value': attribute} for attribute in available_symbols]

    return available_attributes, None, available_symbols, None, False


@manager.callback(
    Output(store_data.custom_symbols.store_id, 'data'),
    Input('custom_symbol_button', 'n_clicks'),
    Input({'type': 'remove_custom_symbol_button', 'index': ALL}, 'n_clicks'),
    State(store_data.custom_symbols.store_id, 'data'),
    State('custom_symbol_attribute', 'value'),
    State('custom_symbol_selection', 'value'),
)
def update_custom_symbol_dict(n_clicks, _, custom_symbols, attribute, symbol):
    # Add Custom Symbols
    if ctx.triggered_id == 'custom_symbol_button':
        # Reset custom symbol list
        if not n_clicks:
            return []

        # Missing information, return original list
        if not attribute or not symbol:
            return custom_symbols

        # Add new custom symbol data
        custom_symbols.append((attribute, symbol))
        return custom_symbols

    # Remove Custom Symbols
    else:
        custom_symbols.pop(ctx.triggered_id['index'])
        return custom_symbols


@manager.callback(
    Output('selected_custom_symbols_div', "children"),
    Input(store_data.custom_symbols.store_id, 'data'),
)
def update_custom_symbols_configuration(custom_symbols):
    # If there is no custom symbols, return empty list
    if not custom_symbols:
        return []

    # Render the new custom symbol list (show current list and add remove button for each data)
    children = []
    for idx, (attribute, symbol) in enumerate(custom_symbols):
        children.append(dbc.Row([
            dbc.Col(f"{attribute}: {symbol}", width=10),
            dbc.Col(dbc.Button("-", id={'type': 'remove_custom_symbol_button', 'index': idx}, size="sm"), width=2,
                    class_name='d-flex align-items-center justify-content-end'),
        ], class_name='py-1'))

    return children

