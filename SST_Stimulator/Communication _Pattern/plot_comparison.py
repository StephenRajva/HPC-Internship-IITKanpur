import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("communication_comparison.csv")

plt.figure(figsize=(8,5))

plt.plot(df["Processes"], df["Adjacent"],
         marker="o", label="Adjacent")

plt.plot(df["Processes"], df["HalfShift"],
         marker="o", label="HalfShift")

plt.plot(df["Processes"], df["Mirrored"],
         marker="o", label="Mirrored")

plt.xlabel("Number of Processes")
plt.ylabel("Latency (seconds)")
plt.title("Communication Pattern Comparison")

plt.grid(True)
plt.legend()

plt.savefig("communication_comparison.png")
plt.show()
