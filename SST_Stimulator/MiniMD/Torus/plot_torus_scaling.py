import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("torus_summary.csv")

plt.figure(figsize=(8,5))
plt.plot(df["Topology"], df["AvgLatency"], marker="o")
plt.title("MiniMD Torus Scaling - Average Latency")
plt.ylabel("Latency")
plt.grid(True)
plt.savefig("torus_latency.png")
plt.close()

plt.figure(figsize=(8,5))
plt.plot(df["Topology"], df["Packets"], marker="o")
plt.title("MiniMD Torus Scaling - Packet Count")
plt.ylabel("Packets")
plt.grid(True)
plt.savefig("torus_packets.png")
plt.close()

plt.figure(figsize=(8,5))
plt.plot(df["Topology"], df["Throughput"], marker="o")
plt.title("MiniMD Torus Scaling - Throughput")
plt.ylabel("Throughput")
plt.grid(True)
plt.savefig("torus_throughput.png")
plt.close()

print("Created:")
print("torus_latency.png")
print("torus_packets.png")
print("torus_throughput.png")
