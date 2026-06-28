#!/usr/bin/env python3
# =============================================================================
#  analyze_universal.py  -  PPN=2 scaling graphs for ANY topology + app
#
#  Produces ONE PNG per metric (latency, hop count, throughput, packets,
#  bits, idle %, port stalls) with topology size on the x-axis.
#
#  Reads every metric from the SST stats CSV. Hop count is computed from
#  geometry (mesh & torus supported). Edit the RUNS table for your files.
#
#  Run:  python3 analyze_universal.py
# =============================================================================

import os, csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from itertools import combinations

DATA_DIR = os.environ.get("DATA_DIR", "./results")

# ---- EDIT THIS: name + topology type + the size sweep --------------------
#  topology: "mesh" or "torus" (for hop count). Use "other" to skip hop count.
STUDY    = "MiniFE_Mesh_PPN2"
TOPOLOGY = "mesh"
# (x-axis label, dims tuple, csv filename)
RUNS = [
    ("2x2",   (2, 2),   "mesh_2x2_ppn2_nodes8_stats.csv"),
    ("4x4",   (4, 4),   "mesh_4x4_ppn2_nodes32_stats.csv"),
    ("8x8",   (8, 8),   "mesh_8x8_ppn2_nodes128_stats.csv"),
    ("16x16", (16, 16), "mesh_16x16_ppn2_nodes512_stats.csv"),
    ("32x32", (32, 32), "mesh_32x32_ppn2_nodes2048_stats.csv"),
]
# -------------------------------------------------------------------------


def read_csv_rows(path):
    with open(path, newline="") as f:
        reader = csv.reader(f)
        header = [h.strip() for h in next(reader)]
        idx = {name: i for i, name in enumerate(header)}
        rows = []
        for r in reader:
            if len(r) < len(header):
                continue
            rows.append(r)
        return idx, rows


def metrics_from_csv(path):
    """Pull all measured metrics from one stats CSV."""
    idx, rows = read_csv_rows(path)
    iC, iN, iT = idx["ComponentName"], idx["StatisticName"], idx["SimTime"]
    iSum, iCnt = idx["Sum.u64"], idx["Count.u64"]

    lat_sum = lat_cnt = 0          # packet_latency (ns)
    bits = packets = 0             # router send totals
    idle_sum = 0; idle_rows = 0    # idle_time (ps), count of ports
    stalls = 0                     # output_port_stalls
    sim_ps = 0                     # max SimTime (ps)

    for r in rows:
        stat = r[iN].strip()
        comp = r[iC].strip()
        try:
            s = int(r[iSum]); c = int(r[iCnt]); t = int(r[iT])
        except ValueError:
            continue
        sim_ps = max(sim_ps, t)
        if stat == "packet_latency":
            lat_sum += s; lat_cnt += c
        elif stat == "send_bit_count" and comp.startswith("rtr_"):
            bits += s
        elif stat == "send_packet_count" and comp.startswith("rtr_"):
            packets += s
        elif stat == "idle_time":
            idle_sum += s; idle_rows += 1
        elif stat == "output_port_stalls":
            stalls += s

    sim_s = sim_ps * 1e-12                         # ps -> seconds
    avg_latency_ns = lat_sum / lat_cnt if lat_cnt else 0
    throughput_GBs = (bits / 8) / 1e9 / sim_s if sim_s else 0   # bits->bytes->GB/s
    idle_pct = (idle_sum / idle_rows) / sim_ps * 100 if (idle_rows and sim_ps) else 0
    return {
        "latency_ns":   avg_latency_ns,
        "throughput":   throughput_GBs,
        "packets":      packets,
        "bits":         bits,
        "idle_pct":     idle_pct,
        "stalls":       stalls,
    }


def avg_hops(dims, topology):
    """Average hop count over all node pairs. mesh = Manhattan;
       torus = Manhattan with wraparound (min of the two ways round)."""
    if topology not in ("mesh", "torus"):
        return None
    ranges = [range(d) for d in dims]
    # build coordinate list
    coords = []
    def rec(prefix, k):
        if k == len(dims):
            coords.append(tuple(prefix)); return
        for v in ranges[k]:
            rec(prefix + [v], k + 1)
    rec([], 0)
    total = count = 0
    for a, b in combinations(coords, 2):
        d = 0
        for ai, bi, n in zip(a, b, dims):
            step = abs(ai - bi)
            if topology == "torus":
                step = min(step, n - step)   # wraparound
            d += step
        total += d; count += 1
    return total / count if count else 0


# ---- gather ----
labels = []
data = {k: [] for k in ["latency_ns", "throughput", "packets", "bits", "idle_pct", "stalls", "hops"]}
for label, dims, fname in RUNS:
    path = os.path.join(DATA_DIR, fname)
    if not os.path.exists(path):
        print(f"!! missing: {path} (skipping)"); continue
    m = metrics_from_csv(path)
    labels.append(label)
    for k in ["latency_ns", "throughput", "packets", "bits", "idle_pct", "stalls"]:
        data[k].append(m[k])
    data["hops"].append(avg_hops(dims, TOPOLOGY))

# ---- table ----
print(f"\n{STUDY}")
print(f"{'Size':<8}{'Latency(ns)':<13}{'Hops':<8}{'Thru(GB/s)':<12}{'Packets':<10}{'Bits':<12}{'Idle%':<8}{'Stalls':<8}")
print("-" * 79)
for i, lab in enumerate(labels):
    h = data['hops'][i]
    print(f"{lab:<8}{data['latency_ns'][i]:<13.2f}{(f'{h:.2f}' if h is not None else '-'):<8}"
          f"{data['throughput'][i]:<12.4f}{data['packets'][i]:<10}{data['bits'][i]:<12}"
          f"{data['idle_pct'][i]:<8.1f}{data['stalls'][i]:<8}")

# ---- one PNG per metric ----
x = list(range(len(labels)))
PLOTS = [
    ("latency_ns", "Average packet latency (ns)", "Average latency",      "{:.0f}",  "#2c6fbb"),
    ("hops",       "Average hop count",            "Average hop count",    "{:.2f}",  "#c0392b"),
    ("throughput", "Network throughput (GB/s)",    "Throughput",           "{:.3f}",  "#27ae60"),
    ("packets",    "Total packets sent",           "Packet count",         "{:.0f}",  "#8e44ad"),
    ("bits",       "Total bits sent",              "Send bit count",       "{:.0f}",  "#d35400"),
    ("idle_pct",   "Average link idle time (%)",   "Idle time",            "{:.1f}",  "#16a085"),
    ("stalls",     "Total output-port stalls",     "Port stalls",          "{:.0f}",  "#7f8c8d"),
]
for key, ylabel, short, fmt, color in PLOTS:
    ys = data[key]
    if any(v is None for v in ys):   # hop count for unsupported topology
        print(f"(skipping {short}: not available for topology '{TOPOLOGY}')"); continue
    fig, ax = plt.subplots(figsize=(8, 5))
    marker = "s-" if key == "hops" else "o-"
    ax.plot(x, ys, marker, color=color, linewidth=2, markersize=8)
    for xi, yi in zip(x, ys):
        ax.annotate(fmt.format(yi), (xi, yi), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_xlabel("Topology size")
    ax.set_ylabel(ylabel)
    ax.set_title(f"{STUDY}: {short} vs size  (PPN = 2)")
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    out = f"{STUDY}_{key}.png"
    fig.savefig(out, dpi=150)
    print(f"Saved: {out}")
