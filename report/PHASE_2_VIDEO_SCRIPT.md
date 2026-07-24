# Phase 2 Video Script

Target length: 4-6 minutes.

## 0:00-0:45 - Same problem as an MDP

"Phase 2 uses the same warehouse as reinforcement learning. The state remains row, column, and package status. The four actions remain up, down, left, and right. Delivery after pickup is terminal. Illegal moves remain in place and receive a penalty."

Show: Q-Learning page and shared warehouse.

## 0:45-1:40 - Q-learning design

"The update moves Q of state-action toward immediate reward plus discounted best future value. Alpha is 0.24 and gamma is 0.96. Epsilon-greedy exploration decays from 1.00 to 0.04, so training begins broadly and becomes increasingly exploitative."

Show: parameter panel and Bellman update card.

## 1:40-2:25 - Reward design

"The agent receives a delivery bonus, a pickup bonus, negative terrain cost, collision and timeout penalties, and a small progress signal toward the active subgoal. This supports learning while preserving the actual pickup-before-delivery objective."

Show: reward design panel after training.

## 2:25-3:20 - Learning evidence

"Training runs for 1,400 episodes. The curve records average reward, steps, success, and epsilon. The implementation saves the complete Q-table at episode 700 and again at episode 1,400. This initial-state view shows action preferences changing between the midpoint and final snapshot."

Show: click Train, then learning chart and Q-value cards.

## 3:20-4:10 - Final policy

"Evaluation turns exploration off and follows the greedy learned policy. The route must collect the package before delivery and respect walls and terrain. The map overlays that path on a value field. The policy is empirically successful; unlike A*, it is not presented as a proof of minimum cost."

Show: policy path/map and metric cards.

## 4:10-4:55 - Repeated results

"Across seeds 7, 11, and 19, the last 100 training episodes were 100 percent successful and every evaluation policy completed the mission. The project exports full midpoint and final Q-value CSV files, per-seed summaries, a learning curve, and a policy map."

Show: results files and static figures.

## 4:55-5:20 - Close

"Phase 2 therefore includes the MDP definition, reward and hyperparameter choices, exploration strategy, observable learning progress, midpoint and final Q-values, final policy analysis, visualization, and reproducible code."

Show: Overview with both phases operational.
