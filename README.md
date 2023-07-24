# MCTS_Dashboard

## Introduction
MCTS Dashboard is a web-based application that offers visualizations and explanations about MCTS. The visualization gives the user a comprehensive view of the tree's structure. It is also an interactive tool that allows to customize the tree's size, legends, and information displayed when placing the cursor over particular nodes. The explanations furnish elucidations on MCTS determinations based on the results of simulations. By default, it generates explanations for suggested actions, but the user can also request explanations for any other accessible moves. Additionally, it has the capability of producing counterfactual explanations for two actions. The explanations generated are intended to provide users with insights into the MCTS tree's reasoning and promote trust in its decisions. Additionally, it enables users to debug the decision-making process and evaluate the game-playing strategy.

## Install
To run the project in a conda environment, follow these steps after cloning the project onto your PC. Navigate to the directory where you cloned the project and input the following commands to enable the game to run on your computer:
1. conda create -n <chosen environment name> python=3.8
2. conda activate <chosen environment name>
3. pip install -r requirements.txt

## Usage
To access the application, execute the app.py file and open your browser. Then, use the following link: http://127.0.0.1:8050.


## Example Data
You can find the example data in the "data" folder.

