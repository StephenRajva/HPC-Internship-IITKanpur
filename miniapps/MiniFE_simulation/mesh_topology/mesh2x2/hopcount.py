import numpy as np
import csv

# Mesh coordinates for 4 routers (2x2 Mesh, 1 node per router)
rank_coords = {
    0: (0, 0),
    1: (0, 1),
    2: (1, 0),
    3: (1, 1)
}

# Communication motifs extracted from miniFE TAU profile
motifs = [
    {"pattern": "Allreduce", "iterations": 92, "size": 4},
    {"pattern": "Bcast", "root": 0, "iterations": 2, "size": 4},
    {"pattern": "Reduce", "root": 0, "iterations": 2, "size": 4},
    {"pattern": "Allgather", "iterations": 3, "size": 4},
    {"pattern": "Barrier", "iterations": 99, "size": 4},
    {"pattern": "PingPong", "pairs": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)], "iterations": 35}
]

def manhattan(a, b):
    """Calculate hop distance with 2 added for injection/ejection latency."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + 2

rows_avg = [["Pattern", "Ranks", "Avg HopCount"]]
hop_values = []  # To compute overall average later

for motif in motifs:
    if motif["pattern"] in ["Allreduce", "Allgather"]:
        size = motif["size"]
        hops = 0
        for i in range(size):
            for j in range(size):
                if i != j:
                    hops += manhattan(rank_coords[i], rank_coords[j])
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
        hops = sum(manhattan(rank_coords[root], rank_coords[r]) for r in range(size) if r != root)
        avg = hops / (size - 1)
        rows_avg.append([motif["pattern"], size, round(avg, 2)])
        hop_values.append(avg)
    
    elif motif["pattern"] == "PingPong":
        pairs = motif["pairs"]
        for a, b in pairs:
            hops = manhattan(rank_coords[a], rank_coords[b])
            pattern_name = f"PingPong {a}-{b}"
            rows_avg.append([pattern_name, 2, hops])
            hop_values.append(hops)

# Compute overall average hop count across all recorded patterns & pairs
overall = sum(hop_values) / len(hop_values)
rows_avg.append(["Overall", "-", round(overall, 2)])

# Write output CSV
with open("hopcount.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(rows_avg)

# Print output summary
print("Hop Count per Pattern :")
for row in rows_avg:
    print(f"{row[0]:<15} {row[1]:<3}  {row[2]}")

