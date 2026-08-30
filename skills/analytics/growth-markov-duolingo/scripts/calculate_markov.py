#!/usr/bin/env python3
"""
Duolingo 7-State Markov Growth Engine & DAU Forecasting Script.
Pure Python Standard Library (Zero external dependencies).

States:
0: N (New Users)
1: C (Current Users)
2: R (Reactivated Users)
3: Res (Resurrected Users)
4: sWAU (At-Risk WAU)
5: sMAU (At-Risk MAU)
6: Dead (Dormant / Churned Users)
"""

import sys
import json

STATES = ["N", "C", "R", "Res", "sWAU", "sMAU", "Dead"]
STATE_MAP = {s: i for i, s in enumerate(STATES)}

def compute_transition_matrix(transitions_data):
    """
    Given a list of transition counts: [{"from_state": "C", "to_state": "C", "count": 850}, ...]
    Computes and returns a 7x7 row-stochastic transition matrix P (as list of lists).
    """
    matrix = [[0.0 for _ in range(7)] for _ in range(7)]
    for item in transitions_data:
        from_idx = STATE_MAP[item["from_state"]]
        to_idx = STATE_MAP[item["to_state"]]
        matrix[from_idx][to_idx] = float(item["count"])
    
    # Normalize rows to sum to 1.0
    p_matrix = []
    for row in matrix:
        row_sum = sum(row)
        if row_sum > 0:
            p_matrix.append([val / row_sum for val in row])
        else:
            p_matrix.append([0.0 for _ in range(7)])
    
    return p_matrix

def vector_matrix_multiply(vector, matrix):
    """
    Multiplies 1x7 row vector by 7x7 matrix.
    """
    result = [0.0 for _ in range(7)]
    for j in range(7):
        col_sum = 0.0
        for i in range(7):
            col_sum += vector[i] * matrix[i][j]
        result[j] = col_sum
    return result

def forecast_growth(current_state_vector, p_matrix, projected_new_users, days=30):
    """
    Forecasts user state distribution over `days` days.
    
    Parameters:
    - current_state_vector: [N, C, R, Res, sWAU, sMAU, Dead] on Day 0
    - p_matrix: 7x7 transition probability matrix
    - projected_new_users: list of projected New Users for days 1..days (or single average int)
    - days: number of forecast days
    
    Returns:
    - forecast_history: list of dicts with daily counts for each state, DAU, WAU, MAU.
    """
    if isinstance(projected_new_users, (int, float)):
        projected_new_users = [float(projected_new_users)] * days
    elif len(projected_new_users) < days:
        projected_new_users = list(projected_new_users) + [projected_new_users[-1]] * (days - len(projected_new_users))

    history = []
    current_s = [float(x) for x in current_state_vector]

    for day in range(1, days + 1):
        # Propagate through Markov transitions
        next_s = vector_matrix_multiply(current_s, p_matrix)
        
        # Inject new users on this day
        new_u = projected_new_users[day - 1]
        next_s[0] = new_u # N on day D is newly arrived users
        
        dau = next_s[0] + next_s[1] + next_s[2] + next_s[3]
        wau = dau + next_s[4]
        mau = wau + next_s[5]

        history.append({
            "day": day,
            "N": round(next_s[0]),
            "C": round(next_s[1]),
            "R": round(next_s[2]),
            "Res": round(next_s[3]),
            "sWAU": round(next_s[4]),
            "sMAU": round(next_s[5]),
            "Dead": round(next_s[6]),
            "DAU": round(dau),
            "WAU": round(wau),
            "MAU": round(mau),
        })

        current_s = next_s

    return history

if __name__ == "__main__":
    # Test run for Prep Practice Lab
    s0 = [1000, 15000, 1200, 500, 6000, 12000, 50000]
    
    # Sample realistic P matrix
    sample_p = [
        [0.0, 0.65, 0.00, 0.00, 0.35, 0.00, 0.00], # N -> C (65%), sWAU (35%)
        [0.0, 0.82, 0.00, 0.00, 0.18, 0.00, 0.00], # C -> C (82%), sWAU (18%)
        [0.0, 0.60, 0.00, 0.00, 0.40, 0.00, 0.00], # R -> C (60%), sWAU (40%)
        [0.0, 0.50, 0.00, 0.00, 0.50, 0.00, 0.00], # Res -> C (50%), sWAU (50%)
        [0.0, 0.45, 0.00, 0.00, 0.40, 0.15, 0.00], # sWAU -> C (45%), sWAU (40%), sMAU (15%)
        [0.0, 0.00, 0.12, 0.00, 0.00, 0.70, 0.18], # sMAU -> R (12%), sMAU (70%), Dead (18%)
        [0.0, 0.00, 0.00, 0.02, 0.00, 0.00, 0.98], # Dead -> Res (2%), Dead (98%)
    ]

    results = forecast_growth(s0, sample_p, projected_new_users=1200, days=14)
    print("=== 14-Day DAU Growth Forecast (Prep Practice Lab) ===")
    print(f"{'Day':<5} | {'DAU':<8} | {'Current(C)':<12} | {'At-Risk WAU':<12} | {'WAU':<8} | {'MAU':<8}")
    print("-" * 65)
    for r in results:
        print(f"{r['day']:<5} | {r['DAU']:<8} | {r['C']:<12} | {r['sWAU']:<12} | {r['WAU']:<8} | {r['MAU']:<8}")
