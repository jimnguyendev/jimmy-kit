#!/usr/bin/env python3
"""
Amplitude 4-Quadrant Engagement Matrix Calculator.
Pure Python Standard Library (Zero external dependencies).

Computes Breadth (% MAU), Frequency (Events / User), Median Split Coordinates,
and outputs Quadrant Assignments (Core, Niche, Utility, Ghost).
"""

import sys
import json
import statistics

def analyze_engagement_matrix(features_data, total_mau):
    """
    Parameters:
    - features_data: list of dicts:
      [
        {"feature_name": "ai_speaking_grading", "unique_users": 14200, "total_events": 85000},
        {"feature_name": "grammar_error_deepdive", "unique_users": 3800, "total_events": 28000},
        ...
      ]
    - total_mau: total unique active users in the 30-day window (int)

    Returns:
    - result: dict with medians, classified features, and quadrant breakdowns.
    """
    processed = []
    breadths = []
    frequencies = []

    for f in features_data:
        unique_u = f["unique_users"]
        total_e = f["total_events"]
        
        breadth_pct = (unique_u / total_mau) * 100.0
        freq = total_e / unique_u if unique_u > 0 else 0.0
        
        breadths.append(breadth_pct)
        frequencies.append(freq)

        processed.append({
            "feature_name": f["feature_name"],
            "unique_users": unique_u,
            "total_events": total_e,
            "breadth_pct": round(breadth_pct, 2),
            "frequency": round(freq, 2),
        })

    median_breadth = statistics.median(breadths) if breadths else 0.0
    median_frequency = statistics.median(frequencies) if frequencies else 0.0

    quadrants = {
        "CORE (Top-Right: High Breadth, High Freq)": [],
        "NICHE / POWER (Top-Left: Low Breadth, High Freq)": [],
        "UTILITY (Bottom-Right: High Breadth, Low Freq)": [],
        "GHOST (Bottom-Left: Low Breadth, Low Freq)": [],
    }

    for item in processed:
        is_high_breadth = item["breadth_pct"] >= median_breadth
        is_high_freq = item["frequency"] >= median_frequency

        if is_high_breadth and is_high_freq:
            item["quadrant"] = "CORE"
            item["action"] = "PROTECT & OPTIMIZE (Target P95 latency < 20s)"
            quadrants["CORE (Top-Right: High Breadth, High Freq)"].append(item)
        elif not is_high_breadth and is_high_freq:
            item["quadrant"] = "NICHE"
            item["action"] = "GROWTH GOLDMINE (Expose in Onboarding Tour)"
            quadrants["NICHE / POWER (Top-Left: Low Breadth, High Freq)"].append(item)
        elif is_high_breadth and not is_high_freq:
            item["quadrant"] = "UTILITY"
            item["action"] = "MAINTAIN STABLE (Periodic UX audit)"
            quadrants["UTILITY (Bottom-Right: High Breadth, Low Freq)"].append(item)
        else:
            item["quadrant"] = "GHOST"
            item["action"] = "DEPRECATE CANDIDATE (60-day probation)"
            quadrants["GHOST (Bottom-Left: Low Breadth, Low Freq)"].append(item)

    return {
        "total_mau": total_mau,
        "total_features": len(features_data),
        "median_breadth_pct": round(median_breadth, 2),
        "median_frequency": round(median_frequency, 2),
        "quadrants": quadrants,
        "features": processed,
    }

if __name__ == "__main__":
    # Test dataset for a generic practice lab
    sample_mau = 20000
    sample_features = [
        {"feature_name": "ai_speaking_part2_grading", "unique_users": 15600, "total_events": 94000},
        {"feature_name": "pronunciation_sentence_repeat", "unique_users": 14200, "total_events": 120000},
        {"feature_name": "grammar_error_deepdive", "unique_users": 4200, "total_events": 38000},
        {"feature_name": "sample_band8_audio_listen", "unique_users": 5100, "total_events": 41000},
        {"feature_name": "full_mock_test_weekend", "unique_users": 12800, "total_events": 16500},
        {"feature_name": "monthly_progress_report_view", "unique_users": 11500, "total_events": 12000},
        {"feature_name": "advanced_topic_filter_4level", "unique_users": 850, "total_events": 1200},
        {"feature_name": "handwritten_notes_tool", "unique_users": 420, "total_events": 610},
    ]

    analysis = analyze_engagement_matrix(sample_features, sample_mau)
    
    print("=" * 75)
    print("=== AMPLITUDE 4-QUADRANT ENGAGEMENT MATRIX (GENERIC PRACTICE LAB) ===")
    print(f"Total MAU: {analysis['total_mau']:,} | Features Audited: {analysis['total_features']}")
    print(f"Median Breadth: {analysis['median_breadth_pct']}% | Median Frequency: {analysis['median_frequency']} events/user")
    print("=" * 75)

    for q_name, items in analysis["quadrants"].items():
        print(f"\n📌 {q_name} ({len(items)} features):")
        print(f"{'Feature Name':<32} | {'Breadth %':<10} | {'Frequency':<10} | {'Action Plan'}")
        print("-" * 75)
        for item in items:
            print(f"{item['feature_name']:<32} | {item['breadth_pct']:>8}% | {item['frequency']:>9} | {item['action']}")
