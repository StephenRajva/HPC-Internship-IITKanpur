import csv
import numpy as np

# Dragonfly 4-node rank → (group, router)
rank_coords = {
    0: (0, 0),  # group 0, router 0
    1: (0, 1),  # group 0, router 1
    2: (1, 0),  # group 1, router 0
    3: (1, 1)   # group 1, router 1
}

def dragonfly_hops(src, dst):
    """Compute hops between two ranks in 2-group, 2-router-per-group Dragonfly (fully connected)."""
    g1, r1 = rank_coords[src]
    g2, r2 = rank_coords[dst]
    
    if g1 == g2:
        if r1 == r2:
            return 2  # same router (Host→Router→Host)
        else:
            return 3  # same group, different router
    else:
        return 4  # different groups (direct global link)

# MiniFE motifs
motifs = [
    {"pattern": "Allreduce", "iterations": 92, "size": 4},
    {"pattern": "Bcast", "root": 0, "iterations": 2, "size": 4},
    {"pattern": "Reduce", "root": 0, "iterations": 2, "size": 4},
    {"pattern": "Allgather", "iterations": 3, "size": 4},
    {"pattern": "Barrier", "iterations": 99, "size": 4},
    {"pattern": "PingPong", "pairs": [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)], "iterations": 35}
]

rows_avg = [["Pattern", "Ranks", "Avg HopCount"]]
hop_values = []

for motif in motifs:
    if motif["pattern"] in ["Allreduce", "Allgather"]:
        size = motif["size"]
        hops = 0
        for i in range(size):
            for j in range(size):
                if i != j:
                    hops += dragonfly_hops(i, j)
        avg = hops / (size * (size - 1))
        rows_avg.append([motif["pattern"], size, round(avg, 2)])
        hop_values.append(avg)
    
    elif motif["pattern"] == "Barrier":
        size = motif["size"]
        avg = 2 * (np.log2(size) + 1) 
        rows_avg.append([motif["pattern"], size, round(avg, 2)])
        hop_values.append(avg)
    
    elif motif["pattern"] in ["Bcast", "Reduce"]:
        root = motif["root"]
        size = motif["size"]
        hops = sum(dragonfly_hops(root, r) for r in range(size) if r != root)
        avg = hops / (size - 1)
        rows_avg.append([motif["pattern"], size, round(avg, 2)])
        hop_values.append(avg)
    
    elif motif["pattern"] == "PingPong":
        for a, b in motif["pairs"]:
            hops = dragonfly_hops(a, b)
            rows_avg.append([f"PingPong {a}-{b}", 2, hops])
            hop_values.append(hops)

# Overall average
overall = sum(hop_values) / len(hop_values)
rows_avg.append(["Overall", "-", round(overall, 2)])

# Write to CSV
with open("hopcount_dragonfly.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(rows_avg)

# Print summary
print("Hop Count per Pattern:")
for row in rows_avg:
    print(f"{row[0]:<15} {row[1]:<3} {row[2]}")
