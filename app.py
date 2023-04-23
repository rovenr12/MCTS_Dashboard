from dash import Dash, html
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
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
            dbc.Col('1', lg='9', md='12')
        ], class_name='g-3 mb-4 px-3', style={'height': '550px'}),
        dbc.Row([
            dbc.Col('1', lg='12', md='12'),
        ], class_name='g-3 mb-4 px-3', style={'height': '550px'}),
        dbc.Row([
            dbc.Col('1', lg='12', md='12')
        ], class_name='g-3 mb-4 px-3', style={'height': '550px'})
    ], fluid=True),
    store_data.df.store,
    store_data.custom_symbols.store,
], style={'overflow-x': 'hidden', 'min-height': '100vh'}, className='bg-light')

###############################################
# Callbacks
###############################################
visualisation.configuration.manager.attach_to_app(app)

if __name__ == '__main__':
    app.run(debug=True)
