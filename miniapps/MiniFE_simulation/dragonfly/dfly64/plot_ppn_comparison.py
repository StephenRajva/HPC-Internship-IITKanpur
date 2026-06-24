import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("dfly_ppn_summary.csv")

# Latency
plt.figure(figsize=(8,5))
plt.plot(df["PPN"], df["AvgLatency"], marker="o")
plt.title("DragonFly PPN vs Packet Latency")
plt.xlabel("PPN")
plt.ylabel("Average Packet Latency")
plt.grid(True)
plt.savefig("ppn_latency.png")
plt.close()

# Throughput
plt.figure(figsize=(8,5))
plt.plot(df["PPN"], df["Throughput"], marker="o")
plt.title("DragonFly PPN vs Throughput")
plt.xlabel("PPN")
plt.ylabel("Throughput")
plt.grid(True)
plt.savefig("ppn_throughput.png")
plt.close()

# Packet Count
plt.figure(figsize=(8,5))
plt.plot(df["PPN"], df["Packets"], marker="o")
plt.title("DragonFly PPN vs Packet Count")
plt.xlabel("PPN")
plt.ylabel("Packet Count")
plt.grid(True)
plt.savefig("ppn_packets.png")
plt.close()

# Send Bits
plt.figure(figsize=(8,5))
plt.plot(df["PPN"], df["SendBits"], marker="o")
plt.title("DragonFly PPN vs Send Bits")
plt.xlabel("PPN")
plt.ylabel("Send Bits")
plt.grid(True)
plt.savefig("ppn_sendbits.png")
plt.close()

print("Created:")
print("ppn_latency.png")
print("ppn_throughput.png")
print("ppn_packets.png")
print("ppn_sendbits.png")
