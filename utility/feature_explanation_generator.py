from utility import data_preprocessing, feature_explaination_helper_function
import math
import pandas as pd
from dash import html

DIFFERENCE_TYPE = ['Higher', 'Same', 'Lower']


def get_children_in_depth(df, exclude_action_names=None):
    """
    Generate the dictionary about the related nodes in different depths for each root available actions
    :param df: MCTS data file
    :param exclude_action_names: the list of root action names that will be ignored
    :return: dictionary about the related nodes in different depths for each root available actions,
             minimum depth of available actions, maximum depth of available actions
    """

    def helper(current_depth, root_action):
        """
        Recursive function that helps to generate the list of children node for particular
        root action in different depth
        :param current_depth: current depth of root action
        :param root_action: the name of root action
        """
        if current_depth not in root_actions_depth_dict[root_action]:
            return

        # Generate the list of all available node's name from current depth
        children_actions_from_current_depth_list = []
        for children_action in root_actions_depth_dict[root_action][current_depth]:
            children_actions_from_current_depth_list += data_preprocessing.get_node_available_actions(df,
                                                                                                      children_action)

        # Add to dictionary if the list is not empty
        if len(children_actions_from_current_depth_list) != 0:
            root_actions_depth_dict[root_action][current_depth + 1] = children_actions_from_current_depth_list

        # Go to next depth level
        return helper(current_depth + 1, root_action)

    root_actions = data_preprocessing.get_root_available_actions(df, exclude_action_names)
    root_actions_depth_dict = {action: {0: [action]} for action in root_actions}

    max_depth = float('-inf')
    min_depth = float('inf')

    # Generate the depth dictionary for different root actions and
    # record the minimum and maximum depth for the MCTS tree
    for action in root_actions:
        helper(0, action)
        action_max_depth = max(root_actions_depth_dict[action])
        max_depth = max(max_depth, action_max_depth)
        min_depth = min(min_depth, action_max_depth)

    return root_actions_depth_dict, min_depth, max_depth


def get_feature_counts(df, root_features, node_list, exclude_features=None, feature_col='Game_Features', rel_tol=0.001):
    """
    Return the game feature summary about feature changes between root features and other features in node_list
    :param df: MCTS data file
    :param root_features: the root node features
    :param node_list: the list of node names
    :param exclude_features: the list of features will be ignored
    :param feature_col: the column name of features
    :param rel_tol: the column name used for getting available actions (It needs to be unique for different nodes)
    :return: game feature summary dictionary
    """
    # Init the game feature summary dictionary
    game_feature_summary = {feature: {difference_type: 0 for difference_type in DIFFERENCE_TYPE} for feature in
                            root_features}

    # count the features changes for every feature in every node
    for node_name in node_list:
        node_features = data_preprocessing.get_features(df, node_name, exclude_features, feature_col)
        for feature in root_features:
            root_val = root_features[feature]
            node_val = node_features[feature]

            if math.isclose(root_val, node_val, rel_tol=rel_tol):
                game_feature_summary[feature]['Same'] += 1
            elif node_val > root_val:
                game_feature_summary[feature]['Higher'] += 1
            else:
                game_feature_summary[feature]['Lower'] += 1

    return game_feature_summary


def generate_feature_explanation_df(df, depth_type='max', exclude_action_nodes=None, exclude_features=None,
                                    feature_col='Game_Features', change_ratio=0, rel_tol=0.001):
    """
    Return the dataframe of explanations based on game features changes in different depth
    :param df: MCTS data file
    :param depth_type: can be ['max', 'min', 'average']. It will decide the depth of each feature. Max means using the
                        maximum depth of root actions. Min means using the minimum depth of root actions. Average means
                        taking the average of maximum depth and minimum depth
    :param exclude_action_nodes: the list of root actions will be ignored
    :param exclude_features: the list of features will be ignored
    :param feature_col: the column name of features
    :param change_ratio: the change threshold that will use to estimate the features that does not change much
    :param rel_tol: the column name used for getting available actions (It needs to be unique for different nodes)
    :return: the game features explanation dataframe
    """
    # Generate the dictionary about the related nodes in different depths for each root available actions
    root_actions_depth_dict, min_depth, max_depth = get_children_in_depth(df, exclude_action_nodes)

    # Decide the maximum depth for the dataframe
    if depth_type == 'max':
        maximum_depth = max_depth
    elif depth_type == 'min':
        maximum_depth = min_depth
    else:
        maximum_depth = (max_depth + min_depth) // 2

    # Reformat the change ratio from number to percentage
    change_ratio = change_ratio / 100

    # Get the root node features
    root_name = data_preprocessing.get_root_node_name(df)
    root_features = data_preprocessing.get_features(df, root_name, exclude_features, feature_col)

    features_differences = {}

    # Loop for each available root action and do to feature change statistics
    for root_action, action_depth_dict in root_actions_depth_dict.items():
        root_action_name = data_preprocessing.node_name_to_action_name(df, root_action)
        # Create dictionaries for each different type
        for difference_type in DIFFERENCE_TYPE:
            features_differences[(root_action_name, difference_type)] = dict()

        # Loop through the different depth and summary the feature difference
        for depth, node_list in action_depth_dict.items():
            if depth > maximum_depth:
                break

            if depth == 0:
                depth = "Immediate"

            game_feature_summary = get_feature_counts(df, root_features, node_list, exclude_features, feature_col,
                                                      rel_tol)

            for feature, summary in game_feature_summary.items():
                for difference_type, count in summary.items():
                    features_differences[(root_action_name, difference_type)][
                        (feature, depth)] = f"{count / len(node_list) * 100:.1f}%({count})"

    # Change dictionary to Dataframe and reorder the index
    feature_order_dict = {name: idx for idx, name in enumerate(list(root_features))}
    feature_df = pd.DataFrame.from_dict(features_differences)
    feature_df.sort_index(inplace=True, key=lambda x: [i if type(i) == int else 0 for i in x], level=1)
    feature_df.sort_index(inplace=True, key=lambda x: [feature_order_dict[i] for i in x], level=0, sort_remaining=False)
    feature_df.index.names = ['Feature', 'Depth']

    best_action = data_preprocessing.get_root_best_action(df)
    feature_df = reorder_explanation_df_by_best_action(feature_df, best_action)
    feature_df = drop_feature_by_change_ratio(feature_df, change_ratio)

    return feature_df, maximum_depth


def reorder_explanation_df_by_best_action(feature_df, best_action):
    """
    Reorder the columns to put the best action in the front
    :param best_action: the action name of best action from root
    :param feature_df: the feature summary dataframe
    :return: the reorder explanation df
    """
    actions = list(set(feature_df.columns.get_level_values(0)))

    if best_action not in actions:
        return feature_df

    best_action_idx = actions.index(best_action) + 1

    if best_action_idx > 0:
        actions = [best_action] + actions
        actions.pop(best_action_idx)

    new_cols, _ = feature_df.columns.reindex(actions, level=0)
    return feature_df[new_cols]


def drop_feature_by_change_ratio(feature_df, change_ratio=0.1):
    """
    Drop the feature from dataframe if it does not change much
    :param feature_df: the feature summary dataframe
    :param change_ratio: the change threshold that will use to estimate the features that does not change much
    :return: feature summary dataframe
    """
    change_threshold = 1 - change_ratio
    drop_feature_list = []
    for feature in feature_df.index.get_level_values(0).unique():
        feature_same_str_vals = feature_df.loc[(feature, slice(None)), (slice(None), "Same")].values.reshape(-1)
        feature_same_vals = feature_explaination_helper_function.str_percentage_to_float(feature_same_str_vals)

        same_rate = sum(feature_same_vals) / len(feature_same_vals) / 100
        if same_rate > change_threshold:
            drop_feature_list.append(feature)

    return feature_df.drop(index=drop_feature_list, level=0)


def get_feature_average_val(feature_df, feature_name, action_name, direction, depth=None):
    if depth:
        feature_str_val = feature_df.loc[(feature_name, depth), (action_name, direction)]
        return feature_explaination_helper_function.str_percentage_to_float([feature_str_val])[0]
    else:
        feature_str_vals = feature_df.loc[(feature_name, slice(None)), (action_name, direction)].values.reshape(-1)
    feature_vals = feature_explaination_helper_function.str_percentage_to_float(feature_str_vals)
    feature_average_val = sum(feature_vals) / len(feature_vals)
    return feature_average_val


def get_feature_average_change_summary(feature_df, action_name, rel_tol=0.001):
    feature_higher_dict = {}
    feature_lower_dict = {}
    feature_list = feature_df.index.get_level_values(0).unique().to_list()

    for feature in feature_list:
        higher_average_val = get_feature_average_val(feature_df, feature, action_name, 'Higher')
        lower_average_val = get_feature_average_val(feature_df, feature, action_name, 'Lower')

        if higher_average_val > lower_average_val:
            if higher_average_val > rel_tol:
                feature_higher_dict[feature] = higher_average_val
        else:
            if lower_average_val > rel_tol:
                feature_lower_dict[feature] = lower_average_val

    return feature_higher_dict, feature_lower_dict


def get_feature_change_summary(feature_df, action_name, depth, rel_tol=0.001):
    feature_higher_dict = {}
    feature_lower_dict = {}
    feature_list = feature_df.index.get_level_values(0).unique().to_list()

    for feature in feature_list:
        higher_val = get_feature_average_val(feature_df, feature, action_name, 'Higher', depth)
        lower_val = get_feature_average_val(feature_df, feature, action_name, 'Lower', depth)

        if higher_val > lower_val:
            if higher_val > rel_tol:
                feature_higher_dict[feature] = higher_val
        else:
            if lower_val > rel_tol:
                feature_lower_dict[feature] = lower_val

    return feature_higher_dict, feature_lower_dict


def get_top_n_summary_sentence(feature_dict, direction_name, n=3, rel_tol=0.001):
    feature_tuple = sorted(feature_dict.items(), key=lambda x: x[1], reverse=True)
    top_n = [feature for feature, change in feature_tuple[:n]]

    for i in range(n, len(feature_tuple)):
        if abs(feature_tuple[i][1] - feature_tuple[n - 1][1]) > rel_tol:
            break
        top_n.append(feature_tuple[i][0])

    if len(top_n) == 0:
        return f"None of features will become {direction_name} during the simulation."

    if len(top_n) == 1:
        return f"Only {top_n[0]} will become {direction_name} during the simulation."

    if len(top_n) < n:
        return f"Only {len(top_n)} features, namely being {', '.join(top_n[:-1])} and {top_n[-1]}, are expected to {direction_name} during the simulation."

    return f"The top {min(len(top_n), n)} features are anticipated to {direction_name} during the simulation are {', '.join(top_n[:-1])} and {top_n[-1]}."


def generate_action_feature_change_dict(feature_df):
    action_feature_change_dict = {}
    for action in feature_df.columns.get_level_values(0).unique().to_list():
        action_feature_change_dict[action] = {}
        depths = feature_df.loc[:, (action, "Same")].dropna().index.get_level_values(1).unique()

        if len(depths) > 1:
            action_feature_change_dict[action]['average'] = {}
            feature_average_higher_dict, feature_average_lower_dict = get_feature_average_change_summary(feature_df, action)
            action_feature_change_dict[action]['average']['higher'] = feature_average_higher_dict
            action_feature_change_dict[action]['average']['lower'] = feature_average_lower_dict

        for depth in depths:
            action_feature_change_dict[action][depth] = {}
            depth_higher_dict, depth_lower_dict = get_feature_change_summary(feature_df, action, depth)
            action_feature_change_dict[action][depth]['higher'] = depth_higher_dict
            action_feature_change_dict[action][depth]['lower'] = depth_lower_dict

    return action_feature_change_dict


def generate_feature_based_action_generation(action_dict):
    explanations = []
    depth_length = len(action_dict.keys())
    if depth_length == 1:
        explanations.append("The agent simulates the potential outcome of a given action based on its immediate consequences.")
        explanations.append("The agent's focus on immediate result of given action can be attributed to several factors, including determining whether the action leads to a victory or defeat in the game, constraints on computation time, and limited potential for success of certain actions.")
        explanations.append("As the simulation progresses, certain features are expected to undergo changes.")
        explanations.append(get_top_n_summary_sentence(action_dict['Immediate']['higher'], 'higher'))
        explanations.append(get_top_n_summary_sentence(action_dict['Immediate']['lower'], 'lower'))
    else:
        length = depth_length - 1
        explanations.append(f"The agent employs a simulation process to evaluate the potential outcome of a given action along with {length - 1} other actions.")
        explanations.append(f"On average, several features are expected to change during the simulation.")
        explanations.append(get_top_n_summary_sentence(action_dict['average']['higher'], 'higher'))
        explanations.append(get_top_n_summary_sentence(action_dict['average']['lower'], 'lower'))
        explanations.append(html.Br())
        explanations.append(html.Br())

        for i in range(length):
            if i == 0:
                explanations.append("When focusing on the immediate consequences of executing the given action, certain features are projected to undergo the most significant changes.")
                explanations.append(get_top_n_summary_sentence(action_dict['Immediate']['higher'], 'higher'))
                explanations.append(get_top_n_summary_sentence(action_dict['Immediate']['lower'], 'lower'))
                explanations.append(html.Br())
                explanations.append(html.Br())
            else:
                if i == (depth_length - 1):
                    explanations.append(f"Lastly, when considering executing the given action and {i} action(s), the following features are predicted to undergo the most substantial changes.")
                    explanations.append(get_top_n_summary_sentence(action_dict[f'{i}']['higher'], 'higher'))
                    explanations.append(get_top_n_summary_sentence(action_dict[f'{i}']['lower'], 'lower'))
                else:
                    explanations.append(f"When considering executing the given action and {i} action(s), the following features are predicted to undergo the most substantial changes.")
                    explanations.append(get_top_n_summary_sentence(action_dict[f'{i}']['higher'], 'higher'))
                    explanations.append(get_top_n_summary_sentence(action_dict[f'{i}']['lower'], 'lower'))
                    explanations.append(html.Br())
                    explanations.append(html.Br())

    return explanations


def get_feature_change(action_dict, feature):
    for change in action_dict.keys():
        if feature in action_dict[change]:
            return change, action_dict[change][feature]
    return None, 0


def get_counterfactual_feature_change_summary(action_feature_change_dict, depth, action_a, action_b):
    feature_change_a = action_feature_change_dict[action_a][depth]
    feature_change_b = action_feature_change_dict[action_b][depth]
    feature_a_set = set(feature_change_a['higher'].keys()).union(set(feature_change_a['lower'].keys()))
    feature_b_set = set(feature_change_b['higher'].keys()).union(set(feature_change_b['lower'].keys()))
    features = feature_a_set.union(feature_b_set)

    counterfactual_feature_change_summary = {"higher": {}, "lower": {},
                                             "higher_lower": {}, "lower_higher": {},
                                             f"{action_a}_higher": {}, f"{action_a}_lower": {},
                                             f"{action_b}_higher": {}, f"{action_b}_lower": {}, }
    for feature in features:
        feature_a_change_name, feature_a_change_rate = get_feature_change(feature_change_a, feature)
        feature_b_change_name, feature_b_change_rate = get_feature_change(feature_change_b, feature)
        if feature_a_change_name is None:
            counterfactual_feature_change_summary[f"{action_b}_{feature_b_change_name}"][
                feature] = feature_b_change_rate
        elif feature_b_change_name is None:
            counterfactual_feature_change_summary[f"{action_a}_{feature_a_change_name}"][
                feature] = feature_a_change_rate
        else:
            if feature_a_change_name == feature_b_change_name:
                counterfactual_feature_change_summary[feature_a_change_name][feature] = [feature_a_change_rate,
                                                                                         feature_b_change_rate]
            else:
                counterfactual_feature_change_summary[f'{feature_a_change_name}_{feature_b_change_name}'][feature] = [
                    feature_a_change_rate, feature_b_change_rate]

    return counterfactual_feature_change_summary


def get_counterfactual_feature_explanation(counterfactual_summary, action_a, action_b):
    explanations = []
    common_change_same = ['higher', 'lower']
    common_change_diff = ['higher_lower', 'lower_higher']

    common_change_same_len = sum([len(counterfactual_summary[change]) for change in common_change_same])
    common_change_diff_len = sum([len(counterfactual_summary[change]) for change in common_change_diff])
    common_len = common_change_same_len + common_change_diff_len

    if common_len == 0:
        explanations.append(
            f"{action_a} and {action_b} don't have any common features. The exectuion result of given actions are totally different.")
    else:
        explanations.append(f"{action_a} and {action_b} have some common features.")
        if common_change_same_len:
            explanations.append(f"There are some features will change in to same direction.")
            for change in common_change_same:
                feature_len = len(counterfactual_summary[change])
                feature_names = list(counterfactual_summary[change].keys())

                if feature_len == 0:
                    continue
                if feature_len == 1:
                    explanations.append(f"{feature_names[0]} will become {change} during the simulation.")
                else:
                    explanations.append(
                        f"The features are anticipated to become {change} during the simulation are {', '.join(feature_names[:-1])} and {feature_names[-1]}.")

        if common_change_diff_len:
            explanations.append(f"Some features will change in given actions but they change in different direction.")
            for change in common_change_diff:
                change_a, change_b = change.split("_")
                feature_len = len(counterfactual_summary[change])
                feature_names = list(counterfactual_summary[change].keys())

                if feature_len == 0:
                    continue
                if feature_len == 1:
                    explanations.append(
                        f"{feature_names[0]} will become {change_a} for {action_a} while {change_b} for {action_b} during the simulation.")
                else:
                    explanations.append(
                        f"The features are anticipated to become {change_a} for {action_a} while {change_b} for {action_b} during the simulation are {', '.join(feature_names[:-1])} and {feature_names[-1]}.")
    explanations.append(html.Br())
    explanations.append(html.Br())

    action_a_exclude = [f'{action_a}_higher', f"{action_a}_lower"]
    action_b_exclude = [f'{action_b}_higher', f"{action_b}_lower"]
    action_a_exclude_len = sum([len(counterfactual_summary[change]) for change in action_a_exclude])
    action_b_exclude_len = sum([len(counterfactual_summary[change]) for change in action_b_exclude])
    exclude_len = action_a_exclude_len + action_b_exclude_len

    if exclude_len == 0:
        explanations.append(f"There are no features will only change in either {action_a} or {action_b}.")
    else:
        explanations.append(f"There are some features will only change in either one of given actions.")

        if action_a_exclude_len:
            explanations.append(f"It is expected some features will only change in {action_a}.")
            for change_name in action_a_exclude:
                change = change_name[change_name.rfind("_") + 1:]
                feature_len = len(counterfactual_summary[change_name])
                feature_names = list(counterfactual_summary[change_name].keys())

                if feature_len == 0:
                    continue
                if feature_len == 1:
                    explanations.append(f"{feature_names[0]} will become {change} during the simulation.")
                else:
                    explanations.append(
                        f"The features are anticipated to become {change} during the simulation are {', '.join(feature_names[:-1])} and {feature_names[-1]}.")

        if action_b_exclude_len:
            explanations.append(f"It is expected some features will only change in {action_b}.")
            for change_name in action_b_exclude:
                change = change_name[change_name.rfind("_") + 1:]
                feature_len = len(counterfactual_summary[change_name])
                feature_names = list(counterfactual_summary[change_name].keys())

                if feature_len == 0:
                    continue
                if feature_len == 1:
                    explanations.append(f"{feature_names[0]} will become {change} during the simulation.")
                else:
                    explanations.append(
                        f"The features are anticipated to become {change} during the simulation are {', '.join(feature_names[:-1])} and {feature_names[-1]}.")
    explanations.append(html.Br())
    explanations.append(html.Br())
    return explanations


def generate_counterfactual_feature_explanation(action_feature_change_dict):
    # Only generate counterfactual explanation if there are two actions
    action_a, action_b = list(action_feature_change_dict.keys())

    # Compare two actions based on simulation length
    action_a_additional_actions = (lambda x: x - 1 if x != 1 else 1)(len(action_feature_change_dict[action_a])) - 1
    action_b_additional_actions = (lambda x: x - 1 if x != 1 else 1)(len(action_feature_change_dict[action_b])) - 1
    action_a_additional_actions, action_b_additional_actions
    min_additional_num = min(action_a_additional_actions, action_b_additional_actions)

    explanations = []

    if action_a_additional_actions == action_b_additional_actions:
        if action_a_additional_actions == 0:
            explanations.append(f"Both actions have simulation result based on given action.")
            explanations.append("The agent's focus on immediate result of given action can be attributed to several factors, including determining whether the action leads to a victory or defeat in the game, constraints on computation time, and limited potential for success of certain actions.")
        else:
            explanations.append(f"Both actions have simulation result based on given action and {action_a_additional_actions} action(s).")
    else:
        explanations.append(f"Two actions have simulation result in different length.")
        if action_a_additional_actions == 0 or action_b_additional_actions == 0:
            if action_a_additional_actions == 0:
                a = action_a
                b = action_b
                b_num = action_b_additional_actions
            elif action_b_additional_actions == 0:
                a = action_b
                b = action_a
                b_num = action_a_additional_actions
            explanations.append(f"{a} only have simulation result based on given action's immediate consequence.")
            explanations.append("It can be attributed to several factors, including determining whether the action leads to a victory or defeat in the game, constraints on computation time, and limited potential for success of certain actions.")
            explanations.append(f"In contrast, {b} have simulation result based on given action and {b_num} action(s).")
        else:
            explanations.append(f"{action_a} have simulation result based on given action and {action_a_additional_actions} action(s).")
            explanations.append(f"In contrast, {action_b} have simulation result based on given action and {action_b_additional_actions} action(s).")
        if min_additional_num == 0:
            explanations.append(f"Therefore, the counterfactual explaination will based on immediate consequence of given actions.")
        else:
             explanations.append(f"Therefore, the counterfactual explaination will based on the result of given actions and {min_additional_num} following actions.")

    explanations.append(html.Br())
    explanations.append(html.Br())

    # If min_addition_num != 0, we need to compare to average
    if min_additional_num != 0:
        counterfactual_summary = get_counterfactual_feature_change_summary(action_feature_change_dict, 'average', action_a, action_b)
        explanations += get_counterfactual_feature_explanation(counterfactual_summary, action_a, action_b)

    for i in range(min_additional_num + 1):
        i_str = 'Immediate' if i == 0 else str(i)
        counterfactual_summary = get_counterfactual_feature_change_summary(action_feature_change_dict, i_str, action_a, action_b)
        explanations += get_counterfactual_feature_explanation(counterfactual_summary, action_a, action_b)

    return explanations


def generate_text_explanation(feature_df):
    action_feature_change_dict = generate_action_feature_change_dict(feature_df)
    action_names = list(action_feature_change_dict.keys())

    explanations = []

    for action in action_names:
        explanations.append(html.H5(action))
        explanations += generate_feature_based_action_generation(action_feature_change_dict[action])

    if len(action_names) == 2:
        explanations.append(html.H5(f"Counterfactual Explanation"))
        explanations += generate_counterfactual_feature_explanation(action_feature_change_dict)

    return explanations