#!/usr/bin/env python3
import numpy as np
import pandas as pd
from scipy.linalg import expm
from scipy.stats import expon, kstest, binomtest

print('versions: numpy>=2, pandas>=2, scipy>=1.11')

STATE_NAMES = ['routine', 'estimate', 'override']
Q = np.array([
    [-0.45, 0.35, 0.10],
    [0.30, -0.50, 0.20],
    [0.25, 0.35, -0.60],
])
assert np.allclose(Q.sum(axis=1), 0.0)


def fit_homogeneous_poisson(timestamps: np.ndarray) -> dict:
    sorted_t = np.sort(timestamps)
    inter_arrivals = np.diff(sorted_t)
    if inter_arrivals.size < 2:
        return {'warning': 'insufficient_data', 'n_observations': int(sorted_t.size)}
    lambda_hat = float(1.0 / inter_arrivals.mean())
    ks_stat, ks_p = kstest(inter_arrivals, 'expon', args=(0, 1.0 / lambda_hat))
    return {
        'lambda_hat': lambda_hat,
        'n_arrivals': int(sorted_t.size),
        'mean_inter_arrival': float(inter_arrivals.mean()),
        'ks_statistic': float(ks_stat),
        'ks_p_value': float(ks_p),
        'reject_homogeneous_poisson': bool(ks_p < 0.05),
    }


def fit_piecewise_constant_intensity(timestamps: np.ndarray, breakpoints: list[float]) -> dict:
    segments = []
    for i in range(len(breakpoints) - 1):
        start, end = breakpoints[i], breakpoints[i + 1]
        if i == len(breakpoints) - 2:
            in_segment = timestamps[(timestamps >= start) & (timestamps <= end)]
        else:
            in_segment = timestamps[(timestamps >= start) & (timestamps < end)]
        duration = end - start
        rate = float(in_segment.size / duration) if duration > 0 else 0.0
        segments.append({
            'segment': (start, end),
            'duration': float(duration),
            'n_arrivals': int(in_segment.size),
            'rate_per_unit_time': rate,
        })
    return {'segments': segments, 'n_segments': len(segments)}


def end_of_period_spike_diagnostic(timestamps: np.ndarray, period_start: float,
                                   period_end: float, spike_window: float = 3.0,
                                   alpha: float = 0.05) -> dict:
    period_length = period_end - period_start
    if period_length <= 0 or spike_window > period_length:
        return {'warning': 'invalid_window', 'period_length': period_length}
    in_window = int(((timestamps >= period_end - spike_window) & (timestamps <= period_end)).sum())
    total = int(((timestamps >= period_start) & (timestamps <= period_end)).sum())
    if total == 0:
        return {'warning': 'no_transactions_in_period', 'n_transactions': 0}
    expected_fraction = spike_window / period_length
    observed_fraction = in_window / total
    test_result = binomtest(in_window, total, expected_fraction, alternative='greater')
    return {
        'n_transactions_total': total,
        'n_transactions_in_spike_window': in_window,
        'expected_fraction': expected_fraction,
        'observed_fraction': observed_fraction,
        'binomial_test_p_value': float(test_result.pvalue),
        'spike_detected': bool(test_result.pvalue < alpha),
    }


def historical_close_cycle_baseline(historical_period_data: list[dict]) -> dict:
    fractions = []
    dropped = 0
    for period in historical_period_data:
        diag = end_of_period_spike_diagnostic(
            period['timestamps'], period['period_start'], period['period_end'], period['spike_window']
        )
        if 'observed_fraction' in diag:
            fractions.append(diag['observed_fraction'])
        else:
            dropped += 1
    fractions = np.array(fractions)
    return {
        'n_historical_periods': len(fractions),
        'n_periods_dropped': dropped,
        'mean_close_cycle_fraction': float(fractions.mean()) if len(fractions) else 0.0,
        'std_close_cycle_fraction': float(fractions.std(ddof=1)) if len(fractions) > 1 else 0.0,
        'stderr': float(fractions.std(ddof=1) / np.sqrt(len(fractions))) if len(fractions) > 1 else 0.0,
    }


def generate_transaction_stream_with_spike(period_length: float, baseline_rate: float,
                                           spike_window: float, spike_multiplier: float,
                                           seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    baseline_duration = period_length - spike_window
    n_baseline = int(rng.poisson(baseline_rate * baseline_duration))
    baseline_arrivals = rng.uniform(0, baseline_duration, size=n_baseline)
    spike_rate = baseline_rate * spike_multiplier
    n_spike = int(rng.poisson(spike_rate * spike_window))
    spike_arrivals = rng.uniform(period_length - spike_window, period_length, size=n_spike)
    return np.sort(np.concatenate([baseline_arrivals, spike_arrivals]))


def main() -> None:
    print('Multi-state CTMC example')
    P_1day = expm(Q * 1.0)
    print(pd.DataFrame(np.round(P_1day, 3), index=STATE_NAMES, columns=STATE_NAMES))

    PERIOD_LENGTH_DAYS = 90
    BASELINE_RATE_PER_DAY = 30.0
    SPIKE_WINDOW_DAYS = 3
    SPIKE_RATE_MULTIPLIER = 4.0
    timestamps = generate_transaction_stream_with_spike(
        PERIOD_LENGTH_DAYS, BASELINE_RATE_PER_DAY, SPIKE_WINDOW_DAYS, SPIKE_RATE_MULTIPLIER
    )
    print('\nGenerated transactions:', len(timestamps))

    hpp_result = fit_homogeneous_poisson(timestamps)
    print('Homogeneous lambda:', round(hpp_result['lambda_hat'], 3))
    print('KS p-value:', round(hpp_result['ks_p_value'], 6))

    nhpp_result = fit_piecewise_constant_intensity(
        timestamps, breakpoints=[0, PERIOD_LENGTH_DAYS - SPIKE_WINDOW_DAYS, PERIOD_LENGTH_DAYS]
    )
    print('Segment rates:', [round(seg['rate_per_unit_time'], 3) for seg in nhpp_result['segments']])

    spike_result = end_of_period_spike_diagnostic(
        timestamps, period_start=0.0, period_end=PERIOD_LENGTH_DAYS,
        spike_window=SPIKE_WINDOW_DAYS, alpha=0.05
    )
    print('Spike detected:', spike_result['spike_detected'])
    print('Spike p-value:', spike_result['binomial_test_p_value'])

    hist = []
    for seed in range(100, 106):
        hist_ts = generate_transaction_stream_with_spike(PERIOD_LENGTH_DAYS, BASELINE_RATE_PER_DAY, SPIKE_WINDOW_DAYS, 1.0, seed=seed)
        hist.append({'timestamps': hist_ts, 'period_start': 0.0, 'period_end': PERIOD_LENGTH_DAYS, 'spike_window': SPIKE_WINDOW_DAYS})
    baseline = historical_close_cycle_baseline(hist)
    print('Historical baseline:', baseline)


if __name__ == '__main__':
    main()
