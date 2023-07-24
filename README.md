# MCTS_Dashboard

## Introduction
MCTS Dashboard is a web-based application that offers visualizations and explanations about MCTS. The visualization gives the user a comprehensive view of the tree's structure. It is also an interactive tool that allows to customize the tree's size, legends, and information displayed when placing the cursor over particular nodes. The explanations furnish elucidations on MCTS determinations based on the results of simulations. By default, it generates explanations for suggested actions, but the user can also request explanations for any other accessible moves. Additionally, it has the capability of producing counterfactual explanations for two actions. The explanations generated are intended to provide users with insights into the MCTS tree's reasoning and promote trust in its decisions. Additionally, it enables users to debug the decision-making process and evaluate the game-playing strategy.

## MCTS Dashboard Components
### Tree Configuration panel
The tree configuration panel, includes five settings, allowing users to send data and personalize the information displayed on the tree visualization panel. This feature enables users to prioritize the data that is most important to them and to dismiss information that lacks significance. Moreover, it enhances the readability and navigability of the tree by exhibiting solely the key information. The following list shows the setting and its description:
1. **Node Hover Text**: It is used for changes in the information shown when the cursor is placed on a particular node. 
2. **Legend**: It allows changing a node's colour. It can take categorical and numerical node attributes. However, the legend only accepts categorical attributes with less than 24 unique values.
3. **Visit Threshold**: It focuses on nodes that visit the most during the simulation. Any nodes that visit less than the visit threshold will fade out and change to grey. 
4. **Custom Node Symbols**: It is used for altering the symbols of nodes on the tree visualisation panel based on binary attributes. Users can set multiple constraints for symbols, but if one node matches various rules, it will show the symbols set up first.
5. **extbf{Upload File**: It allows users to upload the MCTS data they want to explore. It will then examine the data and ensure it fulfils the format requirements.

### Tree Visualisation panel
Tree visualization provides the user with a comprehensive overview of the tree's formation in a single glance. Nevertheless, the only constraint of tree visualization is the graph's capacity, which can only incorporate up to a maximum of 500 nodes. If the number of nodes exceeds this threshold value, the graph is pruned based on the visit value of each node. This pruning mechanism eliminates the node with the lowest visit value until the residual nodes are fewer than 500. Furthermore, the minimum visit threshold number in the configuration panel is adjusted accordingly. This measure is necessitated by the computational constraints and the crucial to avoid the accumulation of numerous, densely-packed nodes. Furthermore, it is also advantageous for the user as they can focus on the vital nodes within the tree.

### Selected Node Information panel
The Selected Node panel provides information regarding a specific node, allowing the user to examine it. This panel becomes visable when the user clicks on any available nodes in the tree visualization. The remaining nodes in the visualization will become translucent upon selecting a node, and the selected node panel will appear. The details include all attributes of the node and similar nodes by their available action and game features, which represent the statistics of the game state. If the Image attribute is provided, the image will also be displayed in the detail panel. The similarity assessment among nodes can be adjusted, and the comparable nodes are organized according to their similarity. The node with the highest similarity will be ranked first. Moreover, the user can click on any similar node button to view its details and position in the tree visualization.

### Explanation panel
% The explanation panel provides insights into the explanations of MCTS's suggested action and the other available actions for the root. It equips the user with information on the rationale behind MCTS's decision-making process based on an analysis of its simulation results. Two categories of explanation exist: feature-based and path-based, which will be further deliberated in the explanation generation procedure in the following section. Both explanations empower the user to tailor the features and actions to explain. Feature-based explanations have three varieties of representation - tabular, heatmap, and textual. The tabular representation offers a comprehensive version of the feature changes at varying depths, and the number of nodes that fall in this change. The heatmap provides a bird's-eye view of the changes, enabling the user to distinguish the differences at glance. Finally, the text summarizes significant modifications at different depths. If two actions are selected, the text will also furnish a counterfactual explanation based on the comparison of the feature changes at different depths for two actions. Path-based explanations only possess text-format explanations and compare the path difference between the optimal and the worst situation on the simulation for the recommended node by default. The user can also compare the optimal situation between the recommended node and the second-best node or any two nodes.

## Install
To run the project in a conda environment, follow these steps after cloning the project onto your PC. Navigate to the directory where you cloned the project and input the following commands to enable the game to run on your computer:
1. conda create -n <chosen environment name> python=3.8
2. conda activate <chosen environment name>
3. pip install -r requirements.txt

## Usage
To access the application, execute the app.py file and open your browser. Then, use the following link: http://127.0.0.1:8050.


## Example Data
You can find the example data in the "data" folder.

