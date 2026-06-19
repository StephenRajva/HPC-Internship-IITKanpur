import pandas as pd

files = {
    "Torus16": "minimd_torus_stats.csv",
    "Torus64": "minimd_torus_stats64.csv"
}

results = []

for topo, file in files.items():

    print(f"\nProcessing {file}...")

    df = pd.read_csv(file, header=None, skipinitialspace=True)

    send_bits = df[df[1].astype(str).str.contains("send_bit_count", na=False)]
    packets = df[df[1].astype(str).str.contains("send_packet_count", na=False)]
    stalls = df[df[1].astype(str).str.contains("output_port_stalls", na=False)]
    latency = df[df[1].astype(str).str.contains("packet_latency", na=False)]
    idle = df[df[1].astype(str).str.contains("idle_time", na=False)]

    send_bits_total = pd.to_numeric(send_bits[6], errors="coerce").fillna(0).sum()
    packets_total = pd.to_numeric(packets[6], errors="coerce").fillna(0).sum()
    stalls_total = pd.to_numeric(stalls[6], errors="coerce").fillna(0).sum()

    latency_col = pd.to_numeric(latency[9], errors="coerce")
    idle_col = pd.to_numeric(idle[6], errors="coerce")

    avg_latency = latency_col.mean()
    avg_idle = idle_col.mean()

    throughput = send_bits_total / avg_latency if avg_latency > 0 else 0

    results.append([
        topo,
        send_bits_total,
        packets_total,
        stalls_total,
        avg_latency,
        avg_idle,
        throughput
    ])

summary = pd.DataFrame(
    results,
    columns=[
        "Topology",
        "SendBits",
        "Packets",
        "Stalls",
        "AvgLatency",
        "AvgIdleTime",
        "Throughput"
    ]
)

print("\n===== TORUS COMPARISON =====")
print(summary)

summary.to_csv("torus_summary.csv", index=False)

print("\nSaved: torus_summary.csv")
