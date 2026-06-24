import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("adjacent_stats.csv")

print("\n=== AVAILABLE STATISTICS ===")
print(df["StatisticName"].unique())


metrics = {}

reads = df[df["StatisticName"] == "reads"]["Sum.u64"].values
metrics["Reads"] = reads[0] if len(reads) > 0 else 0

writes = df[df["StatisticName"] == "writes"]["Sum.u64"].values
metrics["Writes"] = writes[0] if len(writes) > 0 else 0

gets = df[df["StatisticName"] == "stateEvent_GetS_M"]["Sum.u64"].values
metrics["Cache_GetS"] = gets[0] if len(gets) > 0 else 0

getx = df[df["StatisticName"] == "stateEvent_GetX_M"]["Sum.u64"].values
metrics["Cache_GetX"] = getx[0] if len(getx) > 0 else 0

pend = df[df["StatisticName"] == "pendCycle"]["Sum.u64"].values
metrics["PendingCycles"] = pend[0] if len(pend) > 0 else 0


print("\n=== EXTRACTED METRICS ===")

for k, v in metrics.items():
    print(f"{k}: {v}")


labels = list(metrics.keys())
values = list(metrics.values())

plt.figure(figsize=(10,6))

plt.bar(labels, values)

plt.title("SST Adjacent Pattern Statistics")
plt.xlabel("Metric")
plt.ylabel("Value")

plt.xticks(rotation=15)

plt.tight_layout()

plt.savefig("adjacent_graph.png")

print("\nGraph saved as adjacent_graph.png")

plt.show()

