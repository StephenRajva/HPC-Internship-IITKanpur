import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("combined_topology_comparison.csv")

df["Nodes"] = df["Topology"].str.extract(r'(\d+)').astype(int)

dragonfly = df[df["Family"] == "DragonFly"].sort_values("Nodes")
torus = df[df["Family"] == "Torus"].sort_values("Nodes")

# 1. Latency
plt.figure(figsize=(8,5))
plt.plot(dragonfly["Nodes"], dragonfly["AvgLatency"], marker='o', label="DragonFly")
plt.plot(torus["Nodes"], torus["AvgLatency"], marker='o', label="Torus")
plt.xlabel("Nodes")
plt.ylabel("Average Packet Latency")
plt.title("Latency vs Network Size")
plt.legend()
plt.grid(True)
plt.savefig("latency_comparison.png")
plt.close()

# 2. Packet Count
plt.figure(figsize=(8,5))
plt.plot(dragonfly["Nodes"], dragonfly["Packets"], marker='o', label="DragonFly")
plt.plot(torus["Nodes"], torus["Packets"], marker='o', label="Torus")
plt.xlabel("Nodes")
plt.ylabel("Packet Count")
plt.title("Packet Count vs Network Size")
plt.legend()
plt.grid(True)
plt.savefig("packet_comparison.png")
plt.close()

# 3. Idle Time
plt.figure(figsize=(8,5))
plt.plot(dragonfly["Nodes"], dragonfly["AvgIdleTime"], marker='o', label="DragonFly")
plt.plot(torus["Nodes"], torus["AvgIdleTime"], marker='o', label="Torus")
plt.xlabel("Nodes")
plt.ylabel("Average Idle Time")
plt.title("Idle Time vs Network Size")
plt.legend()
plt.grid(True)
plt.savefig("idletime_comparison.png")
plt.close()

print("Created:")
print("latency_comparison.png")
print("packet_comparison.png")
print("idletime_comparison.png")
