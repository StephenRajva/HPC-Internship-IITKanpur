import pandas as pd

dfly = pd.read_csv("dragonfly_summary.csv")
torus = pd.read_csv("torus_summary.csv")

dfly["Family"] = "DragonFly"
torus["Family"] = "Torus"

combined = pd.concat([dfly, torus], ignore_index=True)

combined.to_csv("combined_topology_comparison.csv", index=False)

print("\n===== COMBINED DATA =====")
print(combined)

print("\nSaved: combined_topology_comparison.csv")
