import json
from utility import similarity

BASIC_ATTRIBUTE = ["Name", "Parent_Name", "Depth", "Value", "Visits"]


def check_df_validity(df):
    """
    Check if the dataframe have all the compulsory attributes
    :param df: MCTS data file
    :return: True or False
    """
    for attribute in BASIC_ATTRIBUTE:
        if attribute not in df.columns:
            return False
    return True


def get_node(df, node_name):
    """
    Get the specific node column from MCTS data file
    :param df: MCTS data file
    :param node_name: the name of node
    :return: Series
    """
    return df[df['Name'] == node_name].iloc[0]


def get_root_node(df):
    """
    Get the root node column from MCTS data file
    :param df: MCTS data file
    :return: Root node Series
    """
    return df[df['Parent_Name'] == 'None'].iloc[0]


def get_root_node_name(df):
    """
    Get the root node name from MCTS data file
    :param df: MCTS data file
    :return: Tree root name
    """
    return get_root_node(df)['Name']


def get_node_available_actions(df, node_name, exclude_actions=None, ref_col='Name'):
    """
    Return the list of available actions from certain node. It will exclude actions provided in excluded_actions
    if provided.
    :param df: MCTS data file
    :param node_name: the node name (need to matched its children Parent Name column)
    :param exclude_actions: the list of actions will be ignored
    :param ref_col: the column name used for getting available actions (It needs to be unique for different nodes)
    :return: the list of actions
    """
    actions = df[df['Parent_Name'] == node_name]

    if exclude_actions:
        actions = actions[~actions[ref_col].isin(exclude_actions)]

    return list(actions[ref_col].values)


def get_root_available_actions(df, exclude_actions=None, ref_col='Name'):
    """
    Return the list of available actions from root node. It will exclude actions provided in excluded_actions
    if provided.
    :param df: MCTS data file
    :param exclude_actions: the list of actions will be ignored
    :param ref_col: the column name used for getting available actions (It needs to be unique for different nodes)
    :return: the list of root actions
    """
    root_name = get_root_node_name(df)

    return get_node_available_actions(df, root_name, exclude_actions, ref_col)


def get_root_best_action(df):
    """
    Return the best action name from root node
    :param df: MCTS data file
    :return: the list of root actions
    """
    root_node = get_root_node(df)

    return root_node['Best_Action']


def get_features(df, node_name, exclude_features=None, feature_col='Game_Features'):
    """
    Return the feature dictionary of a particular node
    :param df: MCTS data file
    :param node_name: the name of node
    :param exclude_features: the list of features that will be ignored
    :param feature_col: the name of feature column
    :return: features dictionary
    """
    node = get_node(df, node_name)
    game_features = json.loads(node[feature_col])

    if exclude_features:
        for exclude_feature in exclude_features:
            if exclude_feature in game_features:
                game_features.pop(exclude_feature)

    return game_features


def node_name_to_action_name(df, node_name):
    """
    Transfer the node name to action name
    :param df: MCTS data file
    :param node_name: the name of node
    :return: the action name
    """
    return df[df['Name'] == node_name].iloc[0]['Action_Name']


def search_children_by_node_name(df, visit_threshold, node_name):
    """
    Get the children list of particular node that its visit time more than visit threshold
    :param df: MCTS data file
    :param visit_threshold: visit threshold
    :param node_name: the name of node
    :return: children list
    """
    df = df[df['Visits'] >= visit_threshold]
    return df[df['Parent_Name'] == node_name]['Name'].tolist()


def search_similar_node_by_features(df, visit_threshold, node_name, similarity_method, threshold, exclude_features):
    """
    Get the list of similar nodes of node name.
    The similarity between two nodes are calculated based on game features difference.
    The node's similarity value must less than threshold
    under selected similarity evaluation method
    :param df: MCTS data file
    :param visit_threshold: visit threshold
    :param node_name: the name of node
    :param similarity_method: similarity method name
    :param threshold: similarity threshold
    :param exclude_features: exclude feature list
    :return: similar node list
    """
    if 'Game_Features' not in df.columns:
        return []

    df = df[df['Visits'] >= visit_threshold]
    feature1 = get_features(df, node_name, exclude_features).values()

    similarities = {}

    for _, row in df.iterrows():
        if row['Name'] == node_name:
            continue
        feature2 = get_features(df, row['Name'], exclude_features).values()
        value = similarity.distance_similarity_function_dict[similarity_method](feature1, feature2)
        if value <= threshold:
            similarities[row['Name']] = value

    similarities = sorted(similarities.items(), key=lambda x: x[1])
    similarities = [children[0] for children in similarities]

    return list(similarities)


def search_similar_node_by_children_action(df, visit_threshold, node_name, similarity_method, threshold):
    """
    Get the list of similar nodes of node name.
    The similarity between two nodes are calculated based on children action difference.
    The node's similarity value must larger than threshold
    :param df: MCTS data file
    :param visit_threshold: visit threshold
    :param node_name: the name of node
    :param similarity_method: similarity method name
    :param threshold: similarity threshold
    :return: similar node list
    """

    if 'Action_Name' not in df.columns:
        return []

    df = df[df['Visits'] >= visit_threshold]
    children_dict = {name: [] for name in df['Name']}
    action_dict = {name: idx for idx, name in enumerate(df['Action_Name'].unique())}

    for _, row in df.iterrows():
        if row['Parent_Name'] not in children_dict:
            children_dict[row['Parent_Name']] = []
        children_dict[row['Parent_Name']].append(action_dict[row['Action_Name']])

    similarities = {}

    for node, children_list in children_dict.items():
        if node == node_name:
            continue

        value = similarity.set_similarity_function_dict[similarity_method](children_dict[node_name],
                                                                           children_dict[node])
        if value >= threshold:
            similarities[node] = value

    similarities = sorted(similarities.items(), key=lambda x: x[1])
    similarities = [children[0] for children in similarities]

    return list(similarities)
