import pandas as pd

files = {
    "DFly4": "/Users/stephenrajva/Downloads/HPC-Upload 2/miniapps/MiniFE_simulation/dragonfly/dfly4/miniFE_communication_stats_dragonfly.csv",
    "DFly16": "/Users/stephenrajva/Downloads/HPC-Upload 2/miniapps/MiniFE_simulation/dragonfly/dfly16/minife_dfly16.csv",
    "DFly64": "/Users/stephenrajva/Downloads/HPC-Upload 2/miniapps/MiniFE_simulation/dragonfly/dfly64/minife_dfly64.csv"
}

results = []

for topo, filepath in files.items():

    print(f"\nProcessing {topo} ...")

    df = pd.read_csv(filepath, header=None, skipinitialspace=True)

    # Send Bit Count
    send_bits_df = df[df[1].astype(str).str.contains("send_bit_count", na=False)]
    send_bits = pd.to_numeric(send_bits_df[6], errors="coerce").sum()

    # Packet Count
    packet_df = df[df[1].astype(str).str.contains("send_packet_count", na=False)]
    packets = pd.to_numeric(packet_df[6], errors="coerce").sum()

    # Output Port Stalls
    stall_df = df[df[1].astype(str).str.contains("output_port_stalls", na=False)]
    stalls = pd.to_numeric(stall_df[6], errors="coerce").sum()

    # Packet Latency
    latency_df = df[df[1].astype(str).str.contains("packet_latency", na=False)]

    if len(latency_df) > 0:
        latency = pd.to_numeric(latency_df[10], errors="coerce").mean()
    else:
        latency = 0

    # Idle Time
    idle_df = df[df[1].astype(str).str.contains("idle_time", na=False)]

    if len(idle_df) > 0:
        idle_time = pd.to_numeric(idle_df[10], errors="coerce").mean()
    else:
        idle_time = 0

    # Simple Throughput Metric
    if latency > 0:
        throughput = send_bits / latency
    else:
        throughput = 0

    results.append([
        topo,
        send_bits,
        packets,
        stalls,
        round(latency, 2),
        round(idle_time, 2),
        round(throughput, 2)
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

print("\n========== SUMMARY ==========")
print(summary)

summary.to_csv("dragonfly_summary.csv", index=False)

print("\nSaved: dragonfly_summary.csv")
