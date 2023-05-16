def str_idx_to_tuple_idx(index):
    def helper(idx):
        idx = idx[1:-1].replace("'", '').replace(' ', '')
        split_idx = idx.rfind(",")
        idx_1, idx_2 = idx[:split_idx], idx[split_idx + 1:]
        return idx_1, idx_2

    return [helper(idx) for idx in index]