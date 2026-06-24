#!/usr/bin/env python3
# =============================================================================
#  analyze_minimd_mesh3d.py  -  two graphs for the MiniMD 3D-mesh scaling study
#
#    Graph 1: Average packet latency  vs  topology size   (from the CSVs)
#    Graph 2: Average hop count        vs  topology size   (3D geometry math)
#
#  Run:  python3 analyze_minimd_mesh3d.py
# =============================================================================

import os
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from itertools import combinations

DATA_DIR = os.environ.get("DATA_DIR", "./results")

# (x-axis label, X, Y, Z, csv filename)
RUNS = [
    ("2x2x2", 2, 2, 2, "minimd_mesh_2x2x2_ppn1_nodes8_stats.csv"),
    ("2x2x4", 2, 2, 4, "minimd_mesh_2x2x4_ppn1_nodes16_stats.csv"),
    ("4x4x4", 4, 4, 4, "minimd_mesh_4x4x4_ppn1_nodes64_stats.csv"),
    ("4x4x8", 4, 4, 8, "minimd_mesh_4x4x8_ppn1_nodes128_stats.csv"),
    ("8x8x8", 8, 8, 8, "minimd_mesh_8x8x8_ppn1_nodes512_stats.csv"),
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


def average_hops_3d(X, Y, Z):
    """Average hop count = mean 3D Manhattan distance over all node pairs.
       rank r -> (x,y,z) with x=r%X, y=(r//X)%Y, z=r//(X*Y)."""
    coords = []
    for r in range(X * Y * Z):
        x = r % X
        y = (r // X) % Y
        z = r // (X * Y)
        coords.append((x, y, z))
    total, count = 0, 0
    for (x1, y1, z1), (x2, y2, z2) in combinations(coords, 2):
        total += abs(x1 - x2) + abs(y1 - y2) + abs(z1 - z2)
        count += 1
    return total / count if count else 0.0


# ---- gather data ----
labels, latency, hops = [], [], []
for label, X, Y, Z, fname in RUNS:
    path = os.path.join(DATA_DIR, fname)
    if not os.path.exists(path):
        print(f"!! missing: {path}  (skipping)")
        continue
    labels.append(label)
    latency.append(average_latency_ns(path))
    hops.append(average_hops_3d(X, Y, Z))

print(f"\n{'Topology':<10}{'Avg latency (ns)':<20}{'Avg hop count':<15}")
print("-" * 45)
for lab, lat, hp in zip(labels, latency, hops):
    print(f"{lab:<10}{lat:<20.2f}{hp:<15.3f}")

x = list(range(len(labels)))

# ---- Graph 1: average latency ----
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x, latency, "o-", color="#2c6fbb", linewidth=2, markersize=8)
for xi, yi in zip(x, latency):
    ax.annotate(f"{yi:.0f} ns", (xi, yi), textcoords="offset points",
                xytext=(0, 10), ha="center", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_xlabel("3D mesh topology size")
ax.set_ylabel("Average packet latency (ns)")
ax.set_title("MiniMD: average latency vs mesh size  (PPN = 1)")
ax.grid(True, axis="y", linestyle="--", alpha=0.4)
fig.tight_layout()
fig.savefig("minimd_latency_vs_size.png", dpi=150)
print("\nSaved: minimd_latency_vs_size.png")

# ---- Graph 2: average hop count ----
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x, hops, "s-", color="#c0392b", linewidth=2, markersize=8)
for xi, yi in zip(x, hops):
    ax.annotate(f"{yi:.2f}", (xi, yi), textcoords="offset points",
                xytext=(0, 10), ha="center", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_xlabel("3D mesh topology size")
ax.set_ylabel("Average hop count")
ax.set_title("MiniMD: average hop count vs mesh size  (PPN = 1)")
ax.grid(True, axis="y", linestyle="--", alpha=0.4)
fig.tight_layout()
fig.savefig("minimd_hop_count_vs_size.png", dpi=150)
print("Saved: minimd_hop_count_vs_size.png")
