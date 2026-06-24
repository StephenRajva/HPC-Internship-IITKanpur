import matplotlib.pyplot as plt

mesh = ["2x2", "4x4", "8x8", "16x16", "32x32"]

# Replace with your actual values when available
hopcount = [3.58, 6.75, 9.80, 15.22, 28.50]

plt.figure(figsize=(8,5))
plt.plot(mesh, hopcount, marker='o', linewidth=2)

plt.title("Mesh Scaling: Average Hop Count")
plt.xlabel("Mesh Topology")
plt.ylabel("Average Hop Count")
plt.grid(True)

plt.savefig("mesh_scaling_hopcount.png", dpi=300)
print("Created: mesh_scaling_hopcount.png")
