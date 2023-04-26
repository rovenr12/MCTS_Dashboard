from dash import dcc


class StoreData:
    def __init__(self, store_id, data=None):
        self.store = dcc.Store(data=data, id=store_id)
        self.store_id = store_id


df = StoreData('dataframe', {"file_id": None, "file": None})
fig_filename = StoreData("fig_filename", None)
custom_symbols = StoreData('custom_symbols', [])
selected_node = StoreData('selected_node', None)
