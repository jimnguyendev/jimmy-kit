#!/usr/bin/env python3
"""
Jenks Natural Breaks (1D Fisher-Jenks Algorithm) & RFM Regularity Calculator.
Pure Python Standard Library (Zero external dependencies).
"""

import sys
import math
import statistics

def compute_jenks_breaks(data_list, num_classes=4):
    """
    Computes 1D Jenks Natural Breaks optimization.
    
    Parameters:
    - data_list: list of numeric values (e.g. revenue or frequency)
    - num_classes: number of bins/tiers (e.g. 4)

    Returns:
    - breaks: list of boundary values [min, b1, b2, ..., max]
    - gvf: Goodness of Variance Fit (float between 0 and 1.0)
    """
    data = sorted([float(x) for x in data_list])
    n = len(data)
    if n == 0 or num_classes <= 1:
        return [data[0], data[-1]] if data else [], 1.0
    if n <= num_classes:
        return data, 1.0

    # lower_class_limits and variance_combinations matrices
    mat1 = [[0] * (num_classes + 1) for _ in range(n + 1)]
    mat2 = [[float('inf')] * (num_classes + 1) for _ in range(n + 1)]

    for i in range(1, num_classes + 1):
        mat1[1][i] = 1
        mat2[1][i] = 0.0

    for i in range(2, n + 1):
        s1 = 0.0
        s2 = 0.0
        w = 0.0
        for m in range(1, i + 1):
            i3 = i - m + 1
            val = data[i3 - 1]
            s2 += val * val
            s1 += val
            w += 1.0
            variance = s2 - (s1 * s1) / w
            i4 = i3 - 1
            if i4 != 0:
                for j in range(2, num_classes + 1):
                    if mat2[i][j] >= (variance + mat2[i4][j - 1]):
                        mat1[i][j] = i3
                        mat2[i][j] = variance + mat2[i4][j - 1]
            else:
                mat1[i][1] = 1
                mat2[i][1] = variance

    k = n
    kclass = [0.0] * (num_classes + 1)
    kclass[num_classes] = data[n - 1]
    kclass[0] = data[0]

    count_num = num_classes
    while count_num >= 2:
        idx = int(mat1[k][count_num]) - 2
        if idx >= 0:
            kclass[count_num - 1] = data[idx]
        k = int(mat1[k][count_num] - 1)
        count_num -= 1

    # Clean breaks to ensure strictly non-decreasing
    kclass = sorted(kclass)

    # Calculate GVF (Goodness of Variance Fit)
    mean_total = statistics.mean(data)
    sdam = sum((x - mean_total) ** 2 for x in data)
    sdcm = mat2[n][num_classes]
    gvf = (sdam - sdcm) / sdam if sdam > 0 else 1.0

    return kclass, round(gvf, 4)

def calculate_regularity_cv(session_intervals_in_days):
    """
    Computes Coefficient of Variation (CV = std_dev / mean) for intervals between active sessions.
    
    Returns:
    - cv: float
    - tier: 'X' (CV < 0.3), 'Y' (0.3 <= CV <= 0.7), 'Z' (CV > 0.7)
    """
    if len(session_intervals_in_days) < 2:
        return 0.0, "X"
    
    mean_interval = statistics.mean(session_intervals_in_days)
    if mean_interval == 0:
        return 0.0, "X"
    
    std_dev = statistics.stdev(session_intervals_in_days)
    cv = std_dev / mean_interval
    
    if cv < 0.3:
        tier = "X" # Highly consistent
    elif cv <= 0.7:
        tier = "Y" # Moderately consistent
    else:
        tier = "Z" # Erratic / Spiky
        
    return round(cv, 3), tier

if __name__ == "__main__":
    # Test dataset for Prep Practice Lab Revenue & Activity
    sample_revenue = [
        50000, 50000, 60000, 75000, 99000, 120000, 150000, 180000,
        450000, 500000, 650000, 790000, 890000, 1200000, 1500000,
        2800000, 3200000, 3500000, 4800000, 6800000, 8500000, 15000000, 22000000
    ]

    breaks, gvf = compute_jenks_breaks(sample_revenue, num_classes=4)
    print("=" * 65)
    print("=== JENKS NATURAL BREAKS CLASSIFICATION (PREP LAB REVENUE) ===")
    print(f"Goodness of Variance Fit (GVF): {gvf * 100:.2f}% (Target ≥ 85%)")
    print("-" * 65)
    for i in range(len(breaks) - 1):
        print(f"Tier {i+1}: [{breaks[i]:>10,.0f} VNĐ ➔ {breaks[i+1]:>10,.0f} VNĐ]")
    print("=" * 65)

    # Test CV for 2 learners
    learner_a_intervals = [2, 3, 2, 2, 3, 2, 3] # Steady every 2-3 days
    learner_b_intervals = [1, 1, 1, 14, 21, 1]   # Crammed, then 3 weeks gap

    cv_a, tier_a = calculate_regularity_cv(learner_a_intervals)
    cv_b, tier_b = calculate_regularity_cv(learner_b_intervals)

    print(f"\nLearner A (Steady): CV = {cv_a} ➔ Tier {tier_a} (True Core VIP)")
    print(f"Learner B (Burst):  CV = {cv_b} ➔ Tier {tier_b} (Opportunistic Deal Hunter)")
