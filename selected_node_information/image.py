import dash_bootstrap_components as dbc
from dash import html, Output, Input
from utility import callback_manager, store_data
from PIL import Image
import base64
import io

manager = callback_manager.CallbackManager()

###############################################
# Layout
###############################################
node_image_card = dbc.Card([
    dbc.CardHeader(html.H6("Image", className='m-0 fw-bold text-center text-primary'), class_name='py-3'),
    dbc.CardBody(id='selected_node_img', style={'overflow-y': 'auto', 'height': '730px'})
], class_name='my-2')


###############################################
# Callbacks
###############################################
@manager.callback(
    Output('selected_node_img', 'children'),
    Input(store_data.selected_node.store_id, 'data'),
)
def update_select_node_img(data):
    if not data or 'Image' not in data:
        return None

    try:
        byte_str = data['Image']
        decode_byte = base64.b64decode(byte_str)
        return html.Img(src=Image.open(io.BytesIO(decode_byte)), width='100%')
    except:
        return dbc.Alert('Unable to generate image.', color="danger")

