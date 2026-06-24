import csv
import numpy as np

# Topology Configuration
torus_shape = (2, 2, 4) 
num_ranks = torus_shape[0] * torus_shape[1] * torus_shape[2]  # 16

# Map rank -> (x, y, z)
def rank_to_coords(rank):
    x = rank % torus_shape[0]
    y = (rank // torus_shape[0]) % torus_shape[1]
    z = rank // (torus_shape[0] * torus_shape[1])
    return (x, y, z)

# 3D Torus shortest path hops (no injection yet)
def torus_distance(a, b):
    dist_x = abs(a[0] - b[0])
    dist_y = abs(a[1] - b[1])
    dist_z = abs(a[2] - b[2])

    hop_x = min(dist_x, torus_shape[0] - dist_x)
    hop_y = min(dist_y, torus_shape[1] - dist_y)
    hop_z = min(dist_z, torus_shape[2] - dist_z)

    return hop_x + hop_y + hop_z

# Total hop count including injection/ejection
def hop_count(rank_a, rank_b):
    return torus_distance(rank_to_coords(rank_a), rank_to_coords(rank_b)) + 2

# Get neighbor pairs for an offset, no duplicates
def get_neighbors_for_offset(offset):
    x_off, y_off, z_off = offset
    pairs = []
    seen = set()
    for rank in range(num_ranks):
        nx = (rank_to_coords(rank)[0] + x_off) % torus_shape[0]
        ny = (rank_to_coords(rank)[1] + y_off) % torus_shape[1]
        nz = (rank_to_coords(rank)[2] + z_off) % torus_shape[2]
        neighbor_rank = nx + ny * torus_shape[0] + nz * torus_shape[0] * torus_shape[1]

        # Avoid counting both (A,B) and (B,A)
        if (neighbor_rank, rank) not in seen and rank != neighbor_rank:
            pairs.append((rank, neighbor_rank))
            seen.add((rank, neighbor_rank))
    return pairs

# Average hop count for all unique pairs (Allreduce model)
def average_pairwise_hops(size):
    total_hops = 0
    count = 0
    for i in range(size):
        for j in range(i + 1, size):  # unique pairs only
            total_hops += hop_count(i, j)
            count += 1
    return total_hops / count

# Barrier hop count model (log2 tree broadcast/reduce)
def barrier_hops(size):
    return round(2 * (np.log2(size) + 1), 3)

def main():
    neighbor_offsets = [
        (1, 0, 0),  # x+1
        (0, 1, 0),  # y+1
        (0, 0, 1),  # z+1
        (1, 1, 1),  # diagonal
    ]

    print(f"Calculating hop counts for 3D Torus {torus_shape}...")

    # Store results
    summary_rows = [["Pattern", "Ranks", "Number of Pairs", "Avg Hop Count"]]

    # --- AllPingPong ---
    for idx, offset in enumerate(neighbor_offsets):
        pairs = get_neighbors_for_offset(offset)
        hops_list = [hop_count(a, b) for (a, b) in pairs]
        avg_hops = round(np.mean(hops_list), 3)
        summary_rows.append([f"AllPingPong Neighbor{idx+1}", num_ranks, len(pairs), avg_hops])

    # --- Allreduce ---
    summary_rows.append(["Allreduce", num_ranks, "-", round(average_pairwise_hops(num_ranks), 3)])

    # --- Barrier ---
    summary_rows.append(["Barrier", num_ranks, "-", barrier_hops(num_ranks)])

    with open("minimd_3dtorus_hopcount_summary.csv", "w", newline="") as f:
        csv.writer(f).writerows(summary_rows)

    
    with open("minimd_3dtorus_per_rank_neighbors.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Rank", "Neighbor Rank", "Offset (x,y,z)", "Hop Count"])
        for idx, offset in enumerate(neighbor_offsets):
            for (a, b) in get_neighbors_for_offset(offset):
                writer.writerow([a, b, str(offset), hop_count(a, b)])

    
    print("\nMiniMD 3D Torus Hop Count Summary:")
    for row in summary_rows:
        print(f"{row[0]:<35} Ranks: {row[1]:<3} Pairs: {row[2]:<5} Avg Hops: {row[3]}")

if __name__ == "__main__":
    main()
