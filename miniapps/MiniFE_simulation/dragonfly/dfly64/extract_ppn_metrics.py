import pandas as pd

files = {
    "PPN1": "minife_dfly_ppn1.csv",
    "PPN2": "minife_dfly_ppn2.csv",
    "PPN4": "minife_dfly64.csv"
}

results = []

for label, file in files.items():

    print(f"\nProcessing {file}...")

    df = pd.read_csv(file, header=None)

    sendbits = df[df[1].astype(str).str.contains("send_bit_count", na=False)]
    packets = df[df[1].astype(str).str.contains("send_packet_count", na=False)]
    stalls = df[df[1].astype(str).str.contains("output_port_stalls", na=False)]
    latency = df[df[1].astype(str).str.contains("packet_latency", na=False)]
    idle = df[df[1].astype(str).str.contains("idle_time", na=False)]

    send_bits = pd.to_numeric(sendbits[7], errors="coerce").sum()
    packet_count = pd.to_numeric(packets[6], errors="coerce").sum()
    stall_count = pd.to_numeric(stalls[6], errors="coerce").sum()

    avg_latency = pd.to_numeric(latency[9], errors="coerce").mean()
    avg_idle = pd.to_numeric(idle[6], errors="coerce").mean()

    throughput = send_bits / avg_latency if avg_latency > 0 else 0

    results.append([
        label,
        send_bits,
        packet_count,
        stall_count,
        avg_latency,
        avg_idle,
        throughput
    ])

summary = pd.DataFrame(
    results,
    columns=[
        "PPN",
        "SendBits",
        "Packets",
        "Stalls",
        "AvgLatency",
        "AvgIdleTime",
        "Throughput"
    ]
)

print("\n===== PPN COMPARISON =====")
print(summary)

summary.to_csv("dfly_ppn_summary.csv", index=False)

print("\nSaved: dfly_ppn_summary.csv")
