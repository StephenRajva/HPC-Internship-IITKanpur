import pandas as pd

mesh = pd.read_csv("mesh_summary.csv")
mesh["Family"] = "Mesh"

torus = pd.read_csv("torus_summary.csv")
torus["Family"] = "Torus"

combined = pd.concat([mesh, torus], ignore_index=True)

print("\n===== COMBINED MINIMD DATA =====")
print(combined)

combined.to_csv("combined_minimd_comparison.csv", index=False)

print("\nSaved: combined_minimd_comparison.csv")
