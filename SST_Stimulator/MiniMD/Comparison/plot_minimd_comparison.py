import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("combined_minimd_comparison.csv")

# Latency
plt.figure(figsize=(8,5))
plt.bar(df["Topology"], df["AvgLatency"])
plt.title("MiniMD Mesh vs Torus - Average Latency")
plt.ylabel("Latency")
plt.grid(True, axis="y")
plt.savefig("latency_comparison.png")
plt.close()

# Throughput
plt.figure(figsize=(8,5))
plt.bar(df["Topology"], df["Throughput"])
plt.title("MiniMD Mesh vs Torus - Throughput")
plt.ylabel("Throughput")
plt.grid(True, axis="y")
plt.savefig("throughput_comparison.png")
plt.close()

# Packets
plt.figure(figsize=(8,5))
plt.bar(df["Topology"], df["Packets"])
plt.title("MiniMD Mesh vs Torus - Packet Count")
plt.ylabel("Packets")
plt.grid(True, axis="y")
plt.savefig("packet_comparison.png")
plt.close()

print("Created:")
print("latency_comparison.png")
print("throughput_comparison.png")
print("packet_comparison.png")
