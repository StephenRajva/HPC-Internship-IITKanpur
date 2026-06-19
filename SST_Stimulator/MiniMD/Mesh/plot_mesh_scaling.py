import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("mesh_summary.csv")

plt.figure(figsize=(8,5))
plt.plot(df["Topology"], df["AvgLatency"], marker="o")
plt.title("MiniMD Mesh Scaling - Average Latency")
plt.ylabel("Latency")
plt.grid(True)
plt.savefig("mesh_latency.png")
plt.close()

plt.figure(figsize=(8,5))
plt.plot(df["Topology"], df["Packets"], marker="o")
plt.title("MiniMD Mesh Scaling - Packet Count")
plt.ylabel("Packets")
plt.grid(True)
plt.savefig("mesh_packets.png")
plt.close()

plt.figure(figsize=(8,5))
plt.plot(df["Topology"], df["Throughput"], marker="o")
plt.title("MiniMD Mesh Scaling - Throughput")
plt.ylabel("Throughput")
plt.grid(True)
plt.savefig("mesh_throughput.png")
plt.close()

print("Created:")
print("mesh_latency.png")
print("mesh_packets.png")
print("mesh_throughput.png")
