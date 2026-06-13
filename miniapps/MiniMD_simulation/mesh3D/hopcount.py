import csv
import numpy as np


mesh_shape = (2, 2, 4)
num_ranks = mesh_shape[0] * mesh_shape[1] * mesh_shape[2]  # 16 ranks

# Map rank ID -> 3D coordinates
def rank_to_coords(rank):
    x = rank % mesh_shape[0]
    y = (rank // mesh_shape[0]) % mesh_shape[1]
    z = rank // (mesh_shape[0] * mesh_shape[1])
    return (x, y, z)

# Manhattan distance + 2 hops for injection/ejection
def manhattan_with_latency(rank_a, rank_b):
    a = rank_to_coords(rank_a)
    b = rank_to_coords(rank_b)
    dist = abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])
    return dist + 2

# Neighbor offsets for AllPingPong motifs 
neighbor_offsets = [
    (1, 0, 0),  # Neighbor pattern 1: x+1 direction
    (0, 1, 0),  # Neighbor pattern 2: y+1 direction
    (0, 0, 1),  # Neighbor pattern 3: z+1 direction
    (1, 1, 1),  # Neighbor pattern 4: diagonal (x+1,y+1,z+1)
]

# Find neighbor pairs for a given offset
def get_neighbors_for_offset(offset):
    x_off, y_off, z_off = offset
    neighbors = []
    for rank in range(num_ranks):
        x, y, z = rank_to_coords(rank)
        nx, ny, nz = x + x_off, y + y_off, z + z_off
        if 0 <= nx < mesh_shape[0] and 0 <= ny < mesh_shape[1] and 0 <= nz < mesh_shape[2]:
            neighbor_rank = nx + ny * mesh_shape[0] + nz * mesh_shape[0] * mesh_shape[1]
            neighbors.append((rank, neighbor_rank))
    return neighbors

# Compute average hops for collectives (Allreduce)
def average_pairwise_hops(size):
    total_hops = 0
    count = 0
    for i in range(size):
        for j in range(size):
            if i != j:
                total_hops += manhattan_with_latency(i, j)
                count += 1
    return total_hops / count if count > 0 else 0

# Compute barrier hops (estimated with 2 * (log2(size) + 1))
def barrier_hops(size):
    return 2 * (np.log2(size) + 1)

#Compute AllPingPong neighbor info
allpingpong_averages = []
allpingpong_individual_pairs = []
per_rank_neighbors = {rank: [] for rank in range(num_ranks)}

for idx, offset in enumerate(neighbor_offsets):
    neighbors = get_neighbors_for_offset(offset)
    hops_list = []
    for (rank_a, rank_b) in neighbors:
        hops = manhattan_with_latency(rank_a, rank_b)
        allpingpong_individual_pairs.append({
            "pattern": f"AllPingPong Neighbor{idx+1} (offset {offset})",
            "rank_a": rank_a,
            "rank_b": rank_b,
            "hops": hops
        })
        hops_list.append(hops)
        # Add to per-rank neighbors (bidirectional)
        per_rank_neighbors[rank_a].append({"neighbor_rank": rank_b, "offset": offset, "hops": hops})
        per_rank_neighbors[rank_b].append({"neighbor_rank": rank_a, "offset": (-offset[0], -offset[1], -offset[2]), "hops": hops})
    avg_hops = np.mean(hops_list) if hops_list else 0
    allpingpong_averages.append({
        "pattern": f"AllPingPong Neighbor{idx+1}",
        "num_pairs": len(neighbors),
        "avg_hops": avg_hops
    })

# Compute collectives hop counts
allreduce_avg = average_pairwise_hops(num_ranks)
barrier_avg = barrier_hops(num_ranks)

# Compose combined summary rows
summary_rows = [["Pattern", "Ranks", "Number of Pairs", "Avg Hop Count"]]

# Add AllPingPong averages
for m in allpingpong_averages:
    summary_rows.append([m["pattern"], num_ranks, m["num_pairs"], round(m["avg_hops"],3)])

# Add collectives
summary_rows.append(["Allreduce", num_ranks, "-", round(allreduce_avg, 3)])
summary_rows.append(["Barrier", num_ranks, "-", round(barrier_avg, 3)])

# Add individual AllPingPong pairs with hops
for pair in allpingpong_individual_pairs:
    summary_rows.append([
        f"{pair['pattern']} Pair {pair['rank_a']}-{pair['rank_b']}",
        2,
        1,
        pair["hops"]
    ])

# Compute weighted overall average
total_weight = sum(m["num_pairs"] for m in allpingpong_averages) + 2 * num_ranks * 2  # 2 collectives weighted by ranks
weighted_sum = sum(m["avg_hops"] * m["num_pairs"] for m in allpingpong_averages) + allreduce_avg * num_ranks + barrier_avg * num_ranks
overall_avg = weighted_sum / total_weight

summary_rows.append(["Overall Average", "-", "-", round(overall_avg, 3)])

# Write summary CSV
with open("minimd_3dmesh_hopcount_summary.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(summary_rows)

# Write per-rank neighbors CSV
with open("minimd_3dmesh_per_rank_neighbors.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Rank", "Neighbor Rank", "Neighbor Offset (x,y,z)", "Hop Count"])
    for rank in range(num_ranks):
        for n in per_rank_neighbors[rank]:
            writer.writerow([rank, n["neighbor_rank"], str(n["offset"]), n["hops"]])

# Print summary
print("MiniMD 3D Mesh Hop Count Summary:")
for row in summary_rows:
    print(f"{row[0]:<50} Ranks: {row[1]:<3} Pairs: {row[2]:<5} Avg Hops: {row[3]}")



