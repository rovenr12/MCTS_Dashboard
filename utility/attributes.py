import json
import numpy as np


def json_validator(text):
    """
    Check if the text is json format and contains more than one element
    :param text: the test case
    :return: True or False
    """
    # Check if the datatype of text is string
    if type(text) != str:
        return False

    # Check if it is not just contain a single element
    if not text.startswith("{") or not text.startswith("["):
        return False

    # Try to transfer text to json and see if it is valid
    try:
        json.loads(text)
    except ValueError:
        return False

    return True


def get_attributes(df):
    """
    Return the attributes the dataframe order by ascii
    :param df: MCTS data file
    :return: the list of column names
    """
    return sorted(df.columns.tolist())


def get_binary_attributes(df):
    """
    Return the column name that only contains 0 and 1
    :param df: MCTS data file
    :return: the list of column names
    """
    return [attribute for attribute in get_attributes(df) if set(df[attribute].unique()) == {0, 1}]


def get_json_type_attributes(df):
    """
    Return the list of json-formatted attributes
    :param df: MCTS data file
    :return: the list of column names
    """
    return [attribute for attribute in get_attributes(df) if json_validator(df[attribute].iloc[0])]


def get_numerical_json_type_attributes(df):
    """
    Return the list of numerical json-formatted attributes
    :param df: MCTS data file
    :return: the list of column names
    """
    # Get the json-format list
    json_type_attributes = get_json_type_attributes(df)
    numerical_json_type_attributes = []

    # Loop through every json-format column and check if there is only numerical value
    for json_type_attribute in json_type_attributes:
        test_case = df[json_type_attribute].iloc[0]
        test_case = json.loads(test_case)

        is_numerical = True

        for data in test_case.values():
            if type(data) not in [int, float]:
                is_numerical = False
                break

        if is_numerical:
            numerical_json_type_attributes.append(json_type_attribute)

    return numerical_json_type_attributes


def get_legend_attributes(df):
    """
    Return the list of available legend attributes. The legend attribute is either the column with all
    the numerical data or the column that has less than 24 categorical data
    :param df:
    :return: (legend list, object type legend list)
    """
    legend_list = df.select_dtypes([np.number]).columns.tolist()
    object_type_legend_list = []
    json_attributes = get_json_type_attributes(df)
    for i in df.select_dtypes(exclude=[np.number]).columns:
        if i not in json_attributes and i not in ["Name", "Parent_Name"]:
            if len(df[i].unique()) < 24:
                legend_list.append(i)
                object_type_legend_list.append(i)
    return sorted(legend_list), sorted(object_type_legend_list)

