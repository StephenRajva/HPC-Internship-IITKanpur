import pandas as pd

files = {
    "Mesh16": "minimd_mesh_stats.csv",
    "Mesh64": "minimd_mesh_stats64.csv"
}

results = []

for topo, file in files.items():

    print(f"\nProcessing {file}...")

    df = pd.read_csv(file, header=None)

    send_bits = df[df[1].astype(str).str.contains("send_bit_count", na=False)]
    packets = df[df[1].astype(str).str.contains("send_packet_count", na=False)]
    stalls = df[df[1].astype(str).str.contains("output_port_stalls", na=False)]
    idle = df[df[1].astype(str).str.contains("idle_time", na=False)]
    latency = df[df[1].astype(str).str.contains("packet_latency", na=False)]

    total_send_bits = pd.to_numeric(send_bits[6], errors="coerce").sum()
    total_packets = pd.to_numeric(packets[6], errors="coerce").sum()
    total_stalls = pd.to_numeric(stalls[6], errors="coerce").sum()

    avg_latency = (
        pd.to_numeric(latency[9], errors="coerce").mean()
        if len(latency) > 0 else 0
    )

    avg_idle = (
        pd.to_numeric(idle[6], errors="coerce").mean()
        if len(idle) > 0 else 0
    )

    throughput = total_send_bits / avg_latency if avg_latency > 0 else 0

    results.append([
        topo,
        total_send_bits,
        total_packets,
        total_stalls,
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

print("\n===== MESH COMPARISON =====")
print(summary)

summary.to_csv("mesh_summary.csv", index=False)

print("\nSaved: mesh_summary.csv")
