import pandas as pd


def str_idx_to_tuple_idx(index):
    def helper(idx):
        idx = idx[1:-1].replace("'", '')
        split_idx = idx.rfind(",")
        idx_1, idx_2 = idx[:split_idx].strip(), idx[split_idx + 1:].strip()

        return idx_1, idx_2

    return [helper(idx) for idx in index]


def json_feature_table_to_df(json_df):
    table_df = pd.read_json(json_df)

    table_df.index = pd.MultiIndex.from_tuples(str_idx_to_tuple_idx(table_df.index), names=('Feature', 'Depth'))
    table_df.columns = pd.MultiIndex.from_tuples(str_idx_to_tuple_idx(table_df.columns))

    return table_df


def str_percentage_to_float(feature_str_vals):
    feature_vals = []
    for str_val in feature_str_vals:
        if type(str_val) != str:
            continue
        feature_vals.append(float(str_val.split("%")[0]))

    return feature_vals
