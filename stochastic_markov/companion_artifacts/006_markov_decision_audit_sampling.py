from __future__ import annotations

import warnings

import numpy as np


STATES = [
    "high_risk_untested",
    "moderate_risk_partially_tested",
    "low_risk_substantively_tested",
]
ACTIONS = ["test_now", "defer", "rely_on_controls"]
P_II = {0: 0.30, 1: 0.10, 2: 0.01}
ETA = 2.0


def value_iteration(
    states: list[str],
    actions: list[str],
    transitions: np.ndarray,
    rewards: np.ndarray,
    gamma: float = 0.95,
    theta: float = 1e-6,
    max_iter: int = 1000,
) -> tuple[np.ndarray, np.ndarray]:
    """Solve a finite-state discounted MDP via value iteration."""
    n_states, n_actions = len(states), len(actions)
    assert transitions.shape == (n_states, n_actions, n_states)
    assert rewards.shape == (n_states, n_actions)
    assert np.allclose(transitions.sum(axis=2), 1.0), "Transitions not row-stochastic"

    V = np.zeros(n_states)
    converged_at = None
    for iteration in range(max_iter):
        V_prev = V.copy()
        Q = rewards + gamma * np.tensordot(transitions, V_prev, axes=([2], [0]))
        V = Q.max(axis=1)
        if np.abs(V - V_prev).max() < theta:
            converged_at = iteration + 1
            break

    if converged_at is None:
        warnings.warn(
            f"value_iteration: max_iter={max_iter} reached without converging to "
            f"theta={theta}; returned policy may be sub-optimal.",
            RuntimeWarning,
        )

    Q_final = rewards + gamma * np.tensordot(transitions, V, axes=([2], [0]))
    policy = Q_final.argmax(axis=1)
    return V, policy


def policy_value(
    policy_idx: np.ndarray,
    transitions: np.ndarray,
    rewards: np.ndarray,
    gamma: float,
    n_iter: int = 1000,
    theta: float = 1e-6,
) -> np.ndarray:
    """Evaluate a fixed policy via iterative policy evaluation."""
    n = len(policy_idx)
    V = np.zeros(n)
    converged_at = None
    for it in range(n_iter):
        V_new = np.zeros(n)
        for s in range(n):
            a = policy_idx[s]
            V_new[s] = rewards[s, a] + gamma * np.dot(transitions[s, a], V)
        if np.abs(V_new - V).max() < theta:
            V = V_new
            converged_at = it + 1
            break
        V = V_new

    if converged_at is None:
        warnings.warn(
            f"policy_value: n_iter={n_iter} reached without converging to "
            f"theta={theta}; returned V may be biased.",
            RuntimeWarning,
        )
    return V


def synthesize_transitions(seed: int = 42) -> np.ndarray:
    """Sample transitions from Dirichlet priors centered on stylized audit outcomes."""
    rng = np.random.default_rng(seed)
    n_states, n_actions = len(STATES), len(ACTIONS)
    base_transitions = np.zeros((n_states, n_actions, n_states))
    base_transitions[0, 0] = [0.10, 0.40, 0.50]
    base_transitions[0, 1] = [0.95, 0.05, 0.00]
    base_transitions[0, 2] = [1.00, 0.00, 0.00]
    base_transitions[1, 0] = [0.05, 0.20, 0.75]
    base_transitions[1, 1] = [0.00, 0.95, 0.05]
    base_transitions[1, 2] = [0.00, 0.50, 0.50]
    base_transitions[2, :, 2] = 1.0

    transitions = np.zeros_like(base_transitions)
    for s in range(n_states):
        for a in range(n_actions):
            alpha = 100.0 * base_transitions[s, a] + 0.01
            transitions[s, a] = rng.dirichlet(alpha)
    return transitions


def build_rewards(lambda_ratio: float, c_i: float = 1.0, eta: float = ETA) -> np.ndarray:
    rewards = np.zeros((len(STATES), len(ACTIONS)))
    for s in range(len(STATES)):
        rewards[s, 0] = -c_i
        rewards[s, 1] = -eta * P_II[s] * c_i
        rewards[s, 2] = -lambda_ratio * P_II[s] * c_i
    return rewards


def main() -> None:
    transitions = synthesize_transitions(seed=42)

    rewards = build_rewards(lambda_ratio=1000.0)
    V_star, policy = value_iteration(STATES, ACTIONS, transitions, rewards, gamma=0.95)
    naive_policy = np.array([0, 0, 0])
    naive_V = policy_value(naive_policy, transitions, rewards, gamma=0.95)

    print("MDP-Optimal Policy for Risk-Based Audit Sampling")
    print("Optimal policy array:", policy.tolist())
    print("Optimal state-value function:", np.round(V_star, 3).tolist())
    print("Naive always-test-now values:", np.round(naive_V, 3).tolist())

    lambda_grid = [100.0, 1000.0, 10000.0]
    print("\nPolicy sensitivity by lambda")
    for lam in lambda_grid:
        _, pol = value_iteration(STATES, ACTIONS, transitions, build_rewards(lam), gamma=0.95)
        print(f"lambda={lam:.0f}: {pol.tolist()}")


if __name__ == "__main__":
    main()
