import matplotlib.pyplot as plt

ranks = [4, 16, 64, 256, 1024]
latency = [3.830, 7.875, 13.178, 21.885, 36.923]

plt.figure(figsize=(8,5))
plt.plot(ranks, latency, marker='o')

plt.xscale("log", base=2)

plt.title("Mesh Scaling (PPN=1)")
plt.xlabel("MPI Ranks")
plt.ylabel("Allreduce Latency (us)")
plt.grid(True)

plt.savefig("mesh_scaling_allreduce.png")
print("Created: mesh_scaling_allreduce.png")
