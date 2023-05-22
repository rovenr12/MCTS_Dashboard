import json
from utility import data_preprocessing
from utility.state import State
from dash import html


def get_action_path(df, node_name=None, action_name=None, is_max=True,
                    state_col='Game_Features', exclude_features=None):

    action_sequences = []
    root_node = data_preprocessing.get_root_node(df)
    root_name = data_preprocessing.get_root_node_name(df)
    root_state = State(json.loads(root_node[state_col]), exclude_features)

    action_sequences.append(root_state)
    if node_name:
        filter_df = df[(df['Parent_Name'] == root_name) & (df['Name'] == node_name)]
    elif action_name:
        filter_df = df[(df['Parent_Name'] == root_name) & (df['Action_Name'] == action_name)]
    else:
        filter_df = df[df['Parent_Name'] == root_name]

    while filter_df.size:
        if is_max:
            current_row = filter_df.iloc[filter_df['Value'].argmax()]
        else:
            current_row = filter_df.iloc[filter_df['Value'].argmin()]
        current_state = State(json.loads(current_row[state_col]), exclude_features)
        current_name = current_row['Name']
        action_sequences.append(current_state)
        filter_df = df[df['Parent_Name'] == current_name]

    return action_sequences


def get_path_feature_difference(path, rel_tol=0.0001):
    feature_difference = path[-1].feature_difference(path[0])
    percentage_difference = path[-1].percentage_difference(path[0])
    feature_differences = {}
    percentage_differences = {}

    for name, difference in feature_difference.items():
        if abs(difference) > rel_tol:
            feature_differences[name] = difference
            percentage_differences[name] = percentage_difference[name]

    return feature_differences, percentage_differences


def generate_explanation(feature_tuple, direction):
    if len(feature_tuple) == 0:
        return []

    max_val = feature_tuple[0][1]
    if type(max_val) == str:
        feature_names = [feature for feature, change in feature_tuple]
        if len(feature_names) > 1:
            return [f'an initial {direction} in {", ".join(feature_names[:-1])} and {feature_names[-1]}']
        else:
            return [f'an initial {direction} in {feature_names[0]}']

    explanations = []
    initial_list = []

    for feature, change in feature_tuple:
        if type(change) == str:
            initial_list.append(feature)
            continue

        if change > 100:
            explanations.append(f'a substantial {change / 100:.1f}-fold {direction} in {feature}')
        elif change >= 80:
            explanations.append(f'a significant {direction} in {feature}')
        elif change >= 60:
            explanations.append(f'a moderate {direction} in {feature}')
        elif change >= 40:
            explanations.append(f'a modest {direction} in {feature}')
        elif change >= 20:
            explanations.append(f'a slight {direction} in {feature}')
        else:
            explanations.append(f'a minimal {direction} in {feature}')

    if initial_list:
        if len(initial_list) > 1:
            explanations.append(f'an initial {direction} in {", ".join(initial_list[:-1])} and {initial_list[-1]}')
        else:
            explanations.append(f'an initial {direction} in {initial_list[0]}')

    return explanations


def generate_explanation_list(features_differences, percentage_differences,
                              features=None, percentage_differences_B=None):
    if features is None:
        features = features_differences.keys()

    increase_dict = {}
    decrease_dict = {}

    for feature in features:
        special_case = ['increase', 'decrease']
        feature_difference = features_differences[feature]
        percentage_diff = percentage_differences[feature]
        if percentage_diff in special_case or not percentage_differences_B:
            percentage_diff = percentage_diff
        else:
            percentage_diff = (percentage_diff + percentage_differences_B[feature]) / 2

        if feature_difference > 0:
            increase_dict[feature] = percentage_diff if percentage_diff in special_case else abs(percentage_diff)
        else:
            decrease_dict[feature] = percentage_diff if percentage_diff in special_case else abs(percentage_diff)

    increase_sorted_tuple = sorted(increase_dict.items(), key=lambda x: x[1] if type(x[1]) != str else -1, reverse=True)
    decrease_sorted_tuple = sorted(decrease_dict.items(), key=lambda x: x[1] if type(x[1]) != str else -1, reverse=True)

    explanation_list = []
    increase_explanation = generate_explanation(increase_sorted_tuple, 'increase')
    decrease_explanation = generate_explanation(decrease_sorted_tuple, 'decrease')

    if len(increase_explanation):
        explanation_list.append(f"Some features are expected to increase in the future state. ")
        if len(increase_explanation) == 1:
            explanation_list.append(f"It is expected {increase_explanation[0]}. ")
        else:
            explanation_list.append(f"It is expected {', '.join(increase_explanation[:-1])}, "
                                    f"and {increase_explanation[-1]}. ")

    if len(decrease_explanation):
        if len(increase_explanation):
            explanation_list.append(f"On the other hand, some features are expected to decrease, including ")
        else:
            explanation_list.append(f"Some features are expected to decrease, including ")
        if len(decrease_explanation) == 1:
            explanation_list.append(f"{decrease_explanation[0]}. ")
        else:
            explanation_list.append(f"{', '.join(decrease_explanation[:-1])}, "
                                    f"and {decrease_explanation[-1]}. ")

    return explanation_list


def classify_features(features_A, features_B):
    common_features = set()
    for feature in features_A.keys() & features_B.keys():
        ba_differences = features_A[feature]
        wa_differences = features_B[feature]
        if ba_differences == 'infinite' or wa_differences == 'infinite':
            if ba_differences == wa_differences:
                common_features.add(feature)
        elif (ba_differences > 0 and wa_differences > 0) or (ba_differences < 0 and wa_differences < 0):
            common_features.add(feature)
    features_A_exclude_list = features_A.keys() - common_features
    features_B_exclude_list = features_B.keys() - common_features
    return common_features, features_A_exclude_list, features_B_exclude_list


def explanation_by_paths(df, state_col='Game_Features', exclude_features=None):
    explanations = []
    # Get the root node name and action space
    root_node_name = data_preprocessing.get_root_node_name(df)
    action_space = df[df.Parent_Name == root_node_name].shape[0]

    if len(df[df.Parent_Name == root_node_name]['Value'].unique()) != 1:
        explanations.append(f"There are {action_space} actions available for this state. ")
    else:
        # Check the value of all possible action, if the value is the same, it is just a random decision
        explanations.append(f"There are {action_space} actions available for this state, all with equal value. "
                            f"Therefore, there is no significant difference in selecting any of the actions. ")

    # Get Best action name
    best_action_name = data_preprocessing.get_root_best_action(df)

    # Get the path that will result in the highest reward and state difference between root node and last node
    best_action_paths = get_action_path(df, state_col=state_col, action_name=best_action_name,
                                        exclude_features=exclude_features)
    ba_feature_differences, ba_percentage_differences = get_path_feature_difference(best_action_paths)

    explanations.append(f'The agent has selected {best_action_name} as the preferred action. ')

    # Get the number of executed actions in the path
    actions_number = len(best_action_paths) - 1
    if actions_number == 1:
        explanations.append(f'The following explanation is based on the simulation results obtained from executing '
                            f'this chosen action. ')
    else:
        explanations.append(f'The following explanation is based on the simulation results obtained from executing '
                            f'this chosen action along with {actions_number - 1} additional action(s). ')

    explanations.append(html.Br())
    explanations.append(html.Br())

    # Get the path that will result in the lowest reward and state difference between root node and last node
    worse_action_paths = get_action_path(df, action_name=best_action_name, is_max=False,
                                         exclude_features=exclude_features, state_col=state_col)
    worse_action_paths = worse_action_paths[:len(best_action_paths)]
    wa_feature_differences, wa_percentage_differences = get_path_feature_difference(worse_action_paths)

    # Generate the explanation
    # Situation 1: No difference between the best value path and the worst value path
    if ba_feature_differences == wa_feature_differences:
        explanations.append("Interestingly, consistently choosing the best or worst action starting from the selected "
                            "action leads to the same outcome. ")

        feature_explanation = generate_explanation_list(ba_feature_differences, ba_percentage_differences)

        if len(feature_explanation) == 0:
            explanations.append(f"It is expected that all features will remain unchanged in the future state. ")
            return explanations

        explanations += feature_explanation

        return explanations

    # Situation 2: Difference between the best value path and the worst value path
    explanations.append("Consistently choosing either the best or worst action from the selected action produces "
                        "different outcomes.")

    # Classify the features
    common_features, ba_exclude_features, wa_exclude_features = classify_features(ba_feature_differences,
                                                                                  wa_feature_differences)

    feature_explanation = generate_explanation_list(ba_feature_differences, ba_percentage_differences, common_features,
                                                    wa_percentage_differences)
    best_feature_explanation = generate_explanation_list(ba_feature_differences, ba_percentage_differences,
                                                         ba_exclude_features)
    worse_feature_explanation = generate_explanation_list(wa_feature_differences, wa_percentage_differences,
                                                          wa_exclude_features)

    # Combine explanations based on different situations
    if len(feature_explanation):
        explanations.append(f"In both the best and worst scenarios, various features undergo changes. ")
        explanations += feature_explanation
        explanations.append(html.Br())
        explanations.append(html.Br())

    if len(best_feature_explanation):
        explanations.append(f"In the best situation, several features undergo changes. ")
        explanations += best_feature_explanation
        explanations.append(html.Br())
        explanations.append(html.Br())

    if len(worse_feature_explanation):
        explanations.append(f"In contrast, in the worst situation, there are changes observed in various features. ")
        explanations += worse_feature_explanation

    return explanations


def counterfactual_explanation_by_paths(df, action_name=None, exclude_features=None, state_col='Game_Features'):
    explanations = []
    # Get the root node name and action space
    root_node_name = data_preprocessing.get_root_node_name(df)

    # Get children list
    children_df = df[df['Parent_Name'] == root_node_name]
    children_list = children_df['Action_Name'].values
    if len(children_list) == 1:
        return []

    if len(df[df.Parent_Name == root_node_name]['Value'].unique()) != 1:
        explanations.append(f"There are {len(children_list)} actions available for this state.")
    else:
        # Check the value of all possible action, if the value is the same, it is just a random decision
        explanations.append(f"There are {len(children_list)} actions available for this state, all with equal value. "
                            f"Therefore, there is no significant difference in selecting any of the actions.")

    # Get Best action name
    best_action_name = df[df['Parent_Name'] == 'None']['Best_Action'].values[0]

    # Get second action name
    if action_name:
        # If action_name is provided and it does not meet the requirement, print message and return
        if action_name not in children_list or action_name == best_action_name:
            if action_name not in children_list:
                return [f"The selected action {action_name} is not available for this state."]
            if action_name == best_action_name:
                return [f"The selected action {action_name} is the best action."]
            return []
    else:
        # Get the second-highest action name if action_name is not provided
        if not action_name:
            orders = children_df['Value'].argsort().values[::-1]
            action_name = children_df.iloc[orders[1]].Action_Name
            # Exception case (all value is the same and current selection is the best action)
            if action_name == best_action_name:
                action_name = children_df.iloc[orders[1]].Action_Name

    explanations.append(f"The following counterfactual explanation is based on {best_action_name} and {action_name}.")

    # Get the best value path of best action
    best_action_paths = get_action_path(df, action_name=best_action_name,
                                        exclude_features=exclude_features, state_col=state_col)

    # Get the best value path of selected action (or second-highest value action)
    comparison_action_paths = get_action_path(df, action_name=action_name,
                                              exclude_features=exclude_features, state_col=state_col)

    # Get path length and shorten the path
    path_len = min(len(best_action_paths), len(comparison_action_paths))
    best_action_paths = best_action_paths[:path_len]
    comparison_action_paths = comparison_action_paths[:path_len]

    ba_feature_differences, ba_percentage_differences = get_path_feature_difference(best_action_paths)
    ca_feature_differences, ca_percentage_differences = get_path_feature_difference(comparison_action_paths)

    # Get the number of executed actions in the path
    if path_len == 1:
        explanations.append(f'The explanation provided is derived from simulating the chosen actions.')
    else:
        explanations.append(f'The explanation provided is derived from simulating the chosen actions,'
                            f' along with {path_len - 1} additional action(s).')
    explanations.append(html.Br())
    explanations.append(html.Br())

    # Generate the explanation
    # Situation 1: No difference between two paths
    if ba_feature_differences == ca_feature_differences:
        explanations.append("Interestingly, when consistently selecting the best action starting from either of the "
                            "given actions, the outcomes remain the same.")
        feature_explanation = generate_explanation_list(ba_feature_differences, ba_percentage_differences)

        if len(feature_explanation) == 0:
            explanations.append(f"It is expected that all features will remain unchanged in the future state. ")
            return explanations

        explanations += feature_explanation

        return explanations

    # Situation 2: Difference between two paths
    explanations.append("Consistently choosing best action from one of selected actions produces "
                        "different outcomes.")

    # Classify the features
    common_features, ba_exclude_features, ca_exclude_features = classify_features(ba_feature_differences,
                                                                                  ca_feature_differences)

    if len(common_features):
        feature_explanation = generate_explanation_list(ba_feature_differences, ba_percentage_differences,
                                                        common_features, ca_percentage_differences)

        explanations.append(f"In the simulation results of the selected actions, "
                            f"various features undergo changes will happen in both actions. ")
        explanations += feature_explanation
        explanations.append(html.Br())
        explanations.append(html.Br())

    if len(ba_exclude_features):
        best_feature_explanation = generate_explanation_list(ba_feature_differences, ba_percentage_differences,
                                                             ba_exclude_features)
        explanations.append(f"When executing the {best_action_name} action, several features undergo different changes "
                            f"compared to the other action. ")
        explanations += best_feature_explanation
        explanations.append(html.Br())
        explanations.append(html.Br())

    if len(ca_exclude_features):
        comparison_feature_explanation = generate_explanation_list(ca_feature_differences, ca_percentage_differences,
                                                                   ca_exclude_features)

        if len(ba_exclude_features):
            explanations.append(f"On the other hand, executing the {action_name} action leads to changes in various "
                                f"features different from the other action. ")
        else:
            explanations.append(f"Executing the {action_name} action leads to changes in various features "
                                f"different from the other action. ")
        explanations += comparison_feature_explanation

    return explanations

