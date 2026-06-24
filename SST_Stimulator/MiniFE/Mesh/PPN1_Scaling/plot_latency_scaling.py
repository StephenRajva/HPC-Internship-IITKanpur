import matplotlib.pyplot as plt

ranks = [4, 16, 64, 256, 1024]

allreduce_latency = [
    3.83,
    7.875,
    13.178,
    21.885,
    36.923
]

plt.figure(figsize=(8,5))

plt.plot(
    ranks,
    allreduce_latency,
    marker='o',
    linewidth=2
)

plt.xscale("log", base=2)

plt.title("Mesh Scaling (PPN=1)")
plt.xlabel("MPI Ranks")
plt.ylabel("Allreduce Latency (us)")
plt.grid(True)

plt.savefig("mesh_latency_scaling.png", dpi=300)

print("Created: mesh_latency_scaling.png")
