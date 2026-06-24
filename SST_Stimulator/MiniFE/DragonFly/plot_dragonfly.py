import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("dragonfly_comparison.csv")

# Send Bits
plt.figure(figsize=(8,5))
plt.plot(df["Topology"], df["SendBits"], marker='o')
plt.title("DragonFly Scaling - Send Bits")
plt.ylabel("Send Bits")
plt.grid(True)
plt.savefig("sendbits.png")

# Packets
plt.figure(figsize=(8,5))
plt.plot(df["Topology"], df["Packets"], marker='o')
plt.title("DragonFly Scaling - Packets")
plt.ylabel("Packet Count")
plt.grid(True)
plt.savefig("packets.png")

# Latency
plt.figure(figsize=(8,5))
plt.plot(df["Topology"], df["Latency"], marker='o')
plt.title("DragonFly Scaling - Latency")
plt.ylabel("Latency")
plt.grid(True)
plt.savefig("latency.png")

print("Graphs generated")
