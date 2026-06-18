import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("scaling_results.csv")

plt.figure(figsize=(10,6))

plt.plot(df["opCount"], df["Reads"], marker='o', label="Reads")
plt.plot(df["opCount"], df["Writes"], marker='o', label="Writes")
plt.plot(df["opCount"], df["Cache_GetS"], marker='o', label="Cache_GetS")
plt.plot(df["opCount"], df["Cache_GetX"], marker='o', label="Cache_GetX")
plt.plot(df["opCount"], df["PendingCycles"], marker='o', label="PendingCycles")

plt.xlabel("Operation Count")
plt.ylabel("Metric Value")
plt.title("SST Scaling Analysis")
plt.legend()
plt.grid(True)

plt.savefig("overall_scaling_graph.png")
plt.show()
