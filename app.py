from dash import Dash, html
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

import selected_node_information.selected_node_panel
from utility import store_data
import visualisation


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title='MCTS Dashboard')
load_figure_template('BOOTSTRAP')

###############################################
# Layout
###############################################
app.layout = html.Div([
    dbc.Row(dbc.Col(html.H1('MCTS Dashboard')), class_name='text-center py-2 bg-primary mb-3'),
    dbc.Container([
        dbc.Row([
            dbc.Col(visualisation.configuration.configuration_card, lg='3', md='12'),
            dbc.Col(visualisation.tree_visualisation.tree_visualisation_div, lg='9', md='12')
        ], class_name='g-3 mb-2 px-3'),
        selected_node_information.selected_node_panel.selected_node_info_row,
        dbc.Row([
            dbc.Col('1', lg='12', md='12', class_name='h-100')
        ], class_name='g-3 mb-4 px-3', style={'height': '550px'})
    ], fluid=True),
    store_data.df.store,
    store_data.fig_filename.store,
    store_data.custom_symbols.store,
    store_data.selected_node.store,
], style={'overflow-x': 'hidden', 'min-height': '100vh'}, className='bg-light')

###############################################
# Callbacks
###############################################
visualisation.configuration.manager.attach_to_app(app)
visualisation.tree_visualisation.manager.attach_to_app(app)
selected_node_information.selected_node_panel.manager.attach_to_app(app)


if __name__ == '__main__':
    app.run(debug=True)
