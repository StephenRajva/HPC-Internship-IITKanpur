import numpy as np
import csv

# Mesh size
DIM_X, DIM_Y = 16, 16

# Map ranks to (x,y) coordinates
rank_coords = {r: (r // DIM_Y, r % DIM_Y) for r in range(DIM_X * DIM_Y)}

def manhattan(a, b):
    """Hop count in Mesh with +2 for injection/ejection"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + 2

# Representative PingPong pairs 
rep_pairs = [
    (0, 1),       # nearest neighbor
    (0, 15),      # same row, far end
    (0, 240),     # same column, far end
    (0, 255),     # farthest diagonal
    (128, 129),   # middle node neighbor
    (127, 128)    # across center boundary
]


motifs = [
    {"pattern": "Allreduce", "size": 256},
    {"pattern": "Bcast", "root": 0, "size": 256},
    {"pattern": "Reduce", "root": 0, "size": 256},
    {"pattern": "Allgather", "size": 256},
    {"pattern": "Barrier", "size": 256},
    {"pattern": "PingPong", "pairs": rep_pairs}
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

# Compute overall average
overall = sum(hop_values) / len(hop_values)
rows_avg.append(["Overall", "-", round(overall, 2)])

# Per-rank neighbor analysis
rows_neighbors = [["Rank", "Neighbors", "Avg HopCount"]]

for r in range(DIM_X * DIM_Y):
    x, y = rank_coords[r]
    neighbors = []
    # 4-neighborhood: up, down, left, right
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx, ny = x+dx, y+dy
        if 0 <= nx < DIM_X and 0 <= ny < DIM_Y:
            neighbor_rank = nx*DIM_Y + ny
            neighbors.append(manhattan((x,y),(nx,ny)))
    if neighbors:
        avg = sum(neighbors) / len(neighbors)
        rows_neighbors.append([r, len(neighbors), round(avg, 2)])


with open("mesh16x16_hopcount_summary.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(rows_avg)

with open("mesh16x16_per_rank_neighbors.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(rows_neighbors)

print("Hop Count per Pattern:")
for row in rows_avg:
    print(f"{row[0]:<20} {row[1]:<5} {row[2]}")

