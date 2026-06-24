import pandas as pd
import matplotlib.pyplot as plt

# Read CSV
df = pd.read_csv("scaling_results.csv")

print("\n=== SCALING DATA ===")
print(df)

# Create graph
plt.figure(figsize=(8,5))

plt.plot(df["Processes"],
         df["Latency"],
         marker='o')

plt.xlabel("Number of Processes")
plt.ylabel("Latency (seconds)")
plt.title("Latency vs Process Count")

plt.grid(True)

# Save graph
plt.savefig("scaling_graph.png")

print("\nGraph saved as scaling_graph.png")
