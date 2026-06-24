#!/usr/bin/env python3
# =============================================================================
#  analyze_mesh.py  -  two simple graphs for the PPN=1 mesh scaling study
#
#    Graph 1: Average packet latency  vs  topology size
#    Graph 2: Average hop count       vs  topology size
#
#  Run:  python3 analyze_mesh.py
# =============================================================================

import os
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from itertools import combinations

# Folder holding the CSVs (override with: export DATA_DIR=/path/to/results)
DATA_DIR = os.environ.get("DATA_DIR", "./results")

# (label shown on x-axis, A, B, csv filename)
RUNS = [
    ("2x2",    2,  2,  "mesh_2x2_ppn1_nodes4_stats.csv"),
    ("4x4",    4,  4,  "mesh_4x4_ppn1_nodes16_stats.csv"),
    ("8x8",    8,  8,  "mesh_8x8_ppn1_nodes64_stats.csv"),
    ("16x16",  16, 16, "mesh_16x16_ppn1_nodes256_stats.csv"),
    ("32x32",  32, 32, "mesh_32x32_ppn1_nodes1024_stats.csv"),
]


def average_latency_ns(csv_path):
    """Average packet latency = (all latency added up) / (number of packets)."""
    total, packets = 0, 0
    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        header = [h.strip() for h in next(reader)]
        i_stat = header.index("StatisticName")
        i_sum  = header.index("Sum.u64")
        i_cnt  = header.index("Count.u64")
        for row in reader:
            if len(row) <= i_cnt:
                continue
            if row[i_stat].strip() == "packet_latency":
                total   += int(row[i_sum].strip())
                packets += int(row[i_cnt].strip())
    return total / packets if packets else 0.0


def average_hops(A, B):
    """Average hop count = mean Manhattan distance over all node pairs."""
    coords = [(i // B, i % B) for i in range(A * B)]
    total, count = 0, 0
    for (r1, c1), (r2, c2) in combinations(coords, 2):
        total += abs(r1 - r2) + abs(c1 - c2)
        count += 1
    return total / count if count else 0.0


# ---- gather data ----
labels, latency, hops = [], [], []
for label, A, B, fname in RUNS:
    path = os.path.join(DATA_DIR, fname)
    if not os.path.exists(path):
        print(f"!! missing: {path}  (skipping)")
        continue
    labels.append(label)
    latency.append(average_latency_ns(path))
    hops.append(average_hops(A, B))

# ---- print a small table ----
print(f"\n{'Topology':<10}{'Avg latency (ns)':<20}{'Avg hop count':<15}")
print("-" * 45)
for lab, lat, hp in zip(labels, latency, hops):
    print(f"{lab:<10}{lat:<20.2f}{hp:<15.3f}")

x = list(range(len(labels)))  # evenly spaced categories on the x-axis

# ---- Graph 1: average latency ----
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x, latency, "o-", color="#2c6fbb", linewidth=2, markersize=8)
for xi, yi in zip(x, latency):
    ax.annotate(f"{yi:.0f} ns", (xi, yi), textcoords="offset points",
                xytext=(0, 10), ha="center", fontsize=9)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_xlabel("Mesh topology size")
ax.set_ylabel("Average packet latency (ns)")
ax.set_title("Average latency vs mesh size  (PPN = 1)")
ax.grid(True, axis="y", linestyle="--", alpha=0.4)
fig.tight_layout()
fig.savefig("latency_vs_size.png", dpi=150)
print("\nSaved: latency_vs_size.png")

# ---- Graph 2: average hop count ----
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x, hops, "s-", color="#c0392b", linewidth=2, markersize=8)
for xi, yi in zip(x, hops):
    ax.annotate(f"{yi:.2f}", (xi, yi), textcoords="offset points",
                xytext=(0, 10), ha="center", fontsize=9)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_xlabel("Mesh topology size")
ax.set_ylabel("Average hop count")
ax.set_title("Average hop count vs mesh size  (PPN = 1)")
ax.grid(True, axis="y", linestyle="--", alpha=0.4)
fig.tight_layout()
fig.savefig("hop_count_vs_size.png", dpi=150)
print("Saved: hop_count_vs_size.png")
