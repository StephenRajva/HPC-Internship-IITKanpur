import pandas as pd

files = {
    "Torus4":"miniFE_communication_stats_torus.csv",
    "Torus16":"miniFE_communication_stats_torus16.csv",
    "Torus64":"miniFE_communication_stats_torus64.csv"
}

results = []

for topo,file in files.items():

    df = pd.read_csv(file, header=None)

    send_bits = pd.to_numeric(
        df[df[1].astype(str).str.contains("send_bit_count", na=False)][7],
        errors="coerce"
    ).sum()

    packets = pd.to_numeric(
        df[df[1].astype(str).str.contains("send_packet_count", na=False)][6],
        errors="coerce"
    ).sum()

    stalls = pd.to_numeric(
        df[df[1].astype(str).str.contains("output_port_stalls", na=False)][6],
        errors="coerce"
    ).sum()

    idle = pd.to_numeric(
        df[df[1].astype(str).str.contains("idle_time", na=False)][10],
        errors="coerce"
    ).mean()

    latency_df = df[df[1].astype(str).str.contains("packet_latency", na=False)]

    latency = pd.to_numeric(
        latency_df[10],
        errors="coerce"
    ).mean()

    throughput = send_bits / latency if latency > 0 else 0

    results.append([
        topo,
        send_bits,
        packets,
        stalls,
        latency,
        idle,
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

print(summary)

summary.to_csv("torus_summary.csv", index=False)

print("\nSaved: torus_summary.csv")
