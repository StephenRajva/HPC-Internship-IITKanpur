import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv(
    "adjacent_trace.csv",
    header=None,
    names=["Source", "Destination", "Bytes", "Latency"]
)

print("\n=== TRACE DATA ===")
print(df)


df["Pair"] = (
    df["Source"].astype(str)
    + " → " +
    df["Destination"].astype(str)
)

# Convert latency to microseconds
df["Latency_us"] = df["Latency"] * 1_000_000


plt.figure(figsize=(10,6))

plt.bar(df["Pair"], df["Latency_us"])

plt.title("Adjacent MPI Communication Latency")
plt.xlabel("Communication Pair")
plt.ylabel("Latency (microseconds)")

plt.tight_layout()

# Save graph
plt.savefig("adjacent_latency.png")

print("\nGraph saved as adjacent_latency.png")

# Show graph
plt.show()

