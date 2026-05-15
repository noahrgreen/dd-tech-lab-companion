#!/usr/bin/env python3
import numpy as np


def transition_counts(sequence: list[int], n_states: int) -> np.ndarray:
    N = np.zeros((n_states, n_states), dtype=int)
    for prev, curr in zip(sequence[:-1], sequence[1:]):
        N[prev, curr] += 1
    return N


def log_likelihood_under_P(N: np.ndarray, P: np.ndarray) -> float:
    with np.errstate(divide='ignore'):
        log_P = np.where(P > 0, np.log(P), -np.inf)
    return float((N * log_P).sum())


def fit_markov_mixture_vectorized(sequences: list[list[int]], n_states: int, K: int,
                                  max_iter: int = 100, tol: float = 1e-5,
                                  n_restarts: int = 10, seed: int = 42) -> dict:
    rng = np.random.default_rng(seed)
    counts = np.stack([transition_counts(s, n_states) for s in sequences])
    N_seq = counts.shape[0]

    best_ll, best_params = -np.inf, None
    for _ in range(n_restarts):
        pi = np.ones(K) / K
        P = rng.dirichlet(np.ones(n_states), size=(K, n_states))
        prev_ll = -np.inf

        for it in range(max_iter):
            with np.errstate(divide='ignore'):
                log_P = np.where(P > 0, np.log(P), -np.inf)
            log_resp = np.log(pi + 1e-300)[None, :] + np.einsum('nab,kab->nk', counts, log_P)
            row_max = np.max(log_resp, axis=1, keepdims=True)
            row_max = np.where(np.isfinite(row_max), row_max, 0.0)
            log_norm = row_max + np.log(np.exp(log_resp - row_max).sum(axis=1, keepdims=True))
            resp = np.exp(log_resp - log_norm)
            ll = float(log_norm.sum())
            if abs(ll - prev_ll) < tol:
                break
            prev_ll = ll

            pi = resp.mean(axis=0)
            weighted_counts = np.einsum('nk,nab->kab', resp, counts)
            row_sums = weighted_counts.sum(axis=2, keepdims=True)
            P = np.where(row_sums > 0, weighted_counts / row_sums, 1.0 / n_states)

        if ll > best_ll:
            best_ll, best_params = ll, {
                'pi': pi,
                'P': P,
                'responsibilities': resp,
                'log_likelihood': ll,
                'n_iterations': it + 1,
            }

    return best_params


def select_K(sequences: list[list[int]], n_states: int, K_candidates=(2, 3, 4, 5)) -> tuple[int, dict]:
    N_seq = len(sequences)
    best_K, best_bic, best_fit = None, np.inf, None
    for K in K_candidates:
        fit = fit_markov_mixture_vectorized(sequences, n_states, K)
        p_K = K * (n_states ** 2 - n_states) + (K - 1)
        bic = -2 * fit['log_likelihood'] + p_K * np.log(N_seq)
        if bic < best_bic:
            best_K, best_bic, best_fit = K, bic, fit
    return best_K, best_fit


def cycle_dominance_score(P: np.ndarray) -> float:
    eigenvalues = np.linalg.eigvals(P)
    sorted_mag = np.sort(np.abs(eigenvalues))[::-1]
    return float(sorted_mag[1])


def transition_entropy_score(P: np.ndarray) -> float:
    with np.errstate(divide='ignore', invalid='ignore'):
        row_entropy = -(P * np.where(P > 0, np.log(P), 0.0)).sum(axis=1)
    return float(row_entropy.mean())


def sample_sequence(P: np.ndarray, length: int, rng, n_states: int) -> list[int]:
    seq = [int(rng.integers(n_states))]
    for _ in range(length - 1):
        seq.append(int(rng.choice(n_states, p=P[seq[-1]])))
    return seq


def run_round_tripping_example() -> None:
    N_STATES = 5
    N_CLEAN = 480
    N_DIRTY = 20
    SEQ_LENGTH = 100
    P_clean = np.array([
        [0.10, 0.10, 0.05, 0.05, 0.70],
        [0.60, 0.05, 0.30, 0.03, 0.02],
        [0.10, 0.70, 0.05, 0.10, 0.05],
        [0.05, 0.02, 0.03, 0.15, 0.75],
        [0.20, 0.05, 0.10, 0.55, 0.10],
    ])
    P_dirty = np.array([
        [0.05, 0.05, 0.05, 0.80, 0.05],
        [0.85, 0.02, 0.10, 0.02, 0.01],
        [0.05, 0.85, 0.05, 0.03, 0.02],
        [0.05, 0.05, 0.80, 0.05, 0.05],
        [0.20, 0.20, 0.20, 0.20, 0.20],
    ])
    rng = np.random.default_rng(42)
    sequences = [sample_sequence(P_clean, SEQ_LENGTH, rng, N_STATES) for _ in range(N_CLEAN)] + [sample_sequence(P_dirty, SEQ_LENGTH, rng, N_STATES) for _ in range(N_DIRTY)]
    truth = [0] * N_CLEAN + [1] * N_DIRTY

    selected_K, fit = select_K(sequences, N_STATES, K_candidates=(2, 3))
    cycle_scores = np.array([cycle_dominance_score(P) for P in fit['P']])
    dirty_component = int(np.argmax(cycle_scores))
    posterior_dirty = fit['responsibilities'][:, dirty_component]
    top_25 = np.argsort(posterior_dirty)[::-1][:25]
    true_dirty_in_top_25 = sum(1 for idx in top_25 if truth[idx] == 1)

    print('Round-tripping example')
    print('BIC-selected K:', selected_K)
    print('Cycle-dominance scores:', np.round(cycle_scores, 3).tolist())
    print('True round-trippers in top 25:', true_dirty_in_top_25)


def run_lapping_example() -> None:
    N_L_STATES = 4
    P_lap_clean = np.array([
        [0.20, 0.35, 0.05, 0.40],
        [0.05, 0.20, 0.30, 0.45],
        [0.02, 0.05, 0.18, 0.75],
        [0.60, 0.10, 0.05, 0.25],
    ])
    P_lap_dirty = np.array([
        [0.02, 0.90, 0.05, 0.03],
        [0.02, 0.02, 0.90, 0.06],
        [0.02, 0.02, 0.02, 0.94],
        [0.94, 0.02, 0.02, 0.02],
    ])
    rng = np.random.default_rng(43)
    lap_sequences = [sample_sequence(P_lap_clean, 60, rng, N_L_STATES) for _ in range(270)] + [sample_sequence(P_lap_dirty, 60, rng, N_L_STATES) for _ in range(30)]
    truth_lap = [0] * 270 + [1] * 30

    selected_K_lap, fit_lap = select_K(lap_sequences, N_L_STATES, K_candidates=(2, 3))
    entropy_scores = np.array([transition_entropy_score(P) for P in fit_lap['P']])
    lapping_component = int(np.argmin(entropy_scores))
    posterior_lap = fit_lap['responsibilities'][:, lapping_component]
    ranked_lap = np.argsort(posterior_lap)[::-1][:35]
    true_lappers = sum(1 for idx in ranked_lap if truth_lap[idx] == 1)

    print('\nLapping example')
    print('BIC-selected K:', selected_K_lap)
    print('Transition-entropy scores:', np.round(entropy_scores, 3).tolist())
    print('True lappers in top 35:', true_lappers)


if __name__ == '__main__':
    np.set_printoptions(suppress=True)
    run_round_tripping_example()
    run_lapping_example()
