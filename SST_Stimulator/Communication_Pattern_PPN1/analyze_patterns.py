#!/usr/bin/env python3
# =============================================================================
#  analyze_patterns.py  -  Compare adjacent / halfshift / mirrored on a Mesh.
#  Reads each pattern run's NIC packet_latency from its CSV and pairs it with
#  the representative Manhattan hop count, then overlays all three patterns on
#  two charts: latency-vs-size and hops-vs-size.
#
#  Run from the Communication_Pattern_PPN1 folder (with adjacent/ halfshift/
#  mirrored/ subfolders each containing results/).
# =============================================================================
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PATTERNS = ["adjacent", "halfshift", "mirrored"]
# (label, shape, nodes)
SIZES = [("2x2", 4), ("4x4", 16), ("8x8", 64), ("16x16", 256), ("32x32", 1024)]

def partner_of(pattern, N):
    if pattern == "adjacent":  return 1
    if pattern == "halfshift": return N // 2
    if pattern == "mirrored":  return N - 1

def coord(nid, dims):
    c, rem = [], nid
    for d in dims:
        c.append(rem % d); rem //= d
    return c

def hops(pattern, shape, N):
    dims = [int(x) for x in shape.split("x")]
    p = partner_of(pattern, N)
    a, b = coord(0, dims), coord(p, dims)
    return sum(abs(x - y) for x, y in zip(a, b))

def avg_latency_ns(csv_path):
    """Average packet_latency (ns) over NIC rows that recorded it."""
    if not os.path.exists(csv_path):
        return None
    tot_sum, tot_cnt = 0.0, 0
    with open(csv_path) as f:
        for row in csv.reader(f):
            row = [c.strip() for c in row]
            if len(row) < 9:
                continue
            if row[1] == "packet_latency":
                try:
                    s = float(row[6]); c = float(row[8])
                except ValueError:
                    continue
                tot_sum += s; tot_cnt += c
    if tot_cnt == 0:
        return None
    return tot_sum / tot_cnt

# gather
data = {p: {"nodes": [], "lat": [], "hop": []} for p in PATTERNS}
print(f"{'Pattern':10} {'Size':7} {'Nodes':6} {'Hops':5} {'Latency(ns)':12}")
print("-" * 50)
for p in PATTERNS:
    for shape, N in SIZES:
        csv_path = os.path.join(p, "results", f"{p}_mesh_{shape}_ppn1_nodes{N}_stats.csv")
        lat = avg_latency_ns(csv_path)
        h = hops(p, shape, N)
        if lat is None:
            print(f"{p:10} {shape:7} {N:6} {h:5}  MISSING ({csv_path})")
            continue
        data[p]["nodes"].append(N)
        data[p]["lat"].append(lat)
        data[p]["hop"].append(h)
        print(f"{p:10} {shape:7} {N:6} {h:5} {lat:12.2f}")

# latency vs size
plt.figure(figsize=(8, 5))
for p in PATTERNS:
    plt.plot(data[p]["nodes"], data[p]["lat"], marker="o", label=p)
plt.xscale("log", base=2)
plt.xlabel("Nodes (PPN=1)"); plt.ylabel("Avg packet latency (ns)")
plt.title("Communication patterns on Mesh - Latency vs Size")
plt.legend(); plt.grid(True, which="both", ls=":")
plt.savefig("pattern_latency_vs_size.png", dpi=130, bbox_inches="tight")
print("Saved: pattern_latency_vs_size.png")

# hops vs size
plt.figure(figsize=(8, 5))
for p in PATTERNS:
    plt.plot(data[p]["nodes"], data[p]["hop"], marker="s", label=p)
plt.xscale("log", base=2)
plt.xlabel("Nodes (PPN=1)"); plt.ylabel("Representative hops (Manhattan)")
plt.title("Communication patterns on Mesh - Hops vs Size")
plt.legend(); plt.grid(True, which="both", ls=":")
plt.savefig("pattern_hops_vs_size.png", dpi=130, bbox_inches="tight")
print("Saved: pattern_hops_vs_size.png")
