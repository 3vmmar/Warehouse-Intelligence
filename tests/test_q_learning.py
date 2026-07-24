from environment import generate_environment
from q_learning import QLearningConfig, train_q_learning


def test_q_learning_converges_and_exposes_both_snapshots():
    environment = generate_environment(
        10, 10, obstacle_ratio=0.10, seed=31, require_assignment_size=False
    )
    result = train_q_learning(
        environment,
        QLearningConfig(
            episodes=500,
            max_steps_per_episode=180,
            seed=31,
            curve_interval=10,
        ),
    )
    assert result.evaluation_success
    assert result.final_100_success_rate >= 0.90
    assert result.policy_path and result.policy_actions
    assert len(result.q_values_midpoint) == environment.state_space_size
    assert len(result.q_values_final) == environment.state_space_size
    assert result.q_values_midpoint != result.q_values_final
