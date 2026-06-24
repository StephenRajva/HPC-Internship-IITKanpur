import matplotlib.pyplot as plt

ranks = [4, 16, 64, 256, 1024]
barrier = [3.829, 7.890, 13.222, 21.957, 36.923]

plt.figure(figsize=(8,5))
plt.plot(ranks, barrier, marker='o')

plt.xscale("log", base=2)

plt.title("Mesh Scaling (PPN=1)")
plt.xlabel("MPI Ranks")
plt.ylabel("Barrier Latency (us)")
plt.grid(True)

plt.savefig("mesh_scaling_barrier.png")
print("Created: mesh_scaling_barrier.png")
