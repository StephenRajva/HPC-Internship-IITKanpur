import numpy as np
import csv

# Job definitions - 256 ranks
jobs = [
    {"size": 32, "start": 0, "pattern": "Allreduce", "params": "arg.count=2048 arg.iterations=20 arg.compute=50ns"},
    {"size": 60, "start": 32, "pattern": "Alltoall", "params": "arg.bytes=1024 arg.iterations=10 arg.compute=100ns"},
    {"size": 64, "start": 92, "pattern": "Barrier", "params": "arg.iterations=30"},
    {"size": 32, "start": 156, "pattern": "Scatter", "params": "arg.root=0 arg.count=4096 arg.iterations=5 arg.compute=150ns"},
    {"size": 66, "start": 188, "pattern": "Bcast", "params": "arg.root=0 arg.count=8192 arg.iterations=8 arg.compute=75ns"},
    {"size": 2, "start": 254, "pattern": "PingPong", "params": "arg.messageSize=1024 arg.iterations=15 arg.rank2=1"}
]

# Generate mesh coordinates
x_coords = np.tile(np.arange(32), 32)
y_coords = np.repeat(np.arange(32), 32)
all_coords = list(zip(x_coords, y_coords))

# Randomly select 256 nodes for ranks
np.random.seed(42)
rank_coords = [all_coords[i] for i in np.random.choice(1024, 256, replace=False)]

# Manhattan hop distance
def manhattan(coord1, coord2):
    return abs(coord1[0]-coord2[0]) + abs(coord1[1]-coord2[1]) + 2  # +2 for injection/ejection

# Hop count calculation based on pattern
def pattern_hops(job):
    start, size, pattern = job["start"], job["size"], job["pattern"]
    coords = rank_coords[start:start+size]

    if pattern in ["Allreduce", "Alltoall"]:
        total = 0
        for i in range(size):
            for j in range(size):
                if i != j:
                    total += manhattan(coords[i], coords[j])
        return total / (size * (size - 1))

    elif pattern == "Barrier":
        return 2 * (np.log2(size) + 1)

    elif pattern in ["Scatter", "Bcast"]:
        root = int(job["params"].split("root=")[1].split()[0])
        root_coord = coords[root]
        total = sum(manhattan(root_coord, c) for i, c in enumerate(coords) if i != root)
        return total / (size - 1)

    elif pattern == "PingPong":
        return manhattan(coords[0], coords[1])

# Print job summary
print("Job Hop Count Analysis:\n")

# Collect per-rank CSV rows
csv_rows = [["Job ID", "Pattern", "Size", "Avg Hop Count", "Rank", "Coordinates"]]

for job_id, job in enumerate(jobs, start=1):
    hops = pattern_hops(job)
    coords = rank_coords[job["start"]:job["start"] + job["size"]]
    
    print(f"Job {job_id}: {job['pattern']:<10} Size={job['size']:<3} Avg Hops={hops:.2f}")
    
    for rank, coord in enumerate(coords):
        csv_rows.append([
            job_id,
            job["pattern"],
            job["size"],
            round(hops, 2),
            rank,
            f"({int(coord[0])},{int(coord[1])})"
        ])

# Overall average
total_avg = np.mean([pattern_hops(job) for job in jobs])
print(f"\nOverall Average Hop Count: {total_avg:.2f}")

# Export to CSV
with open("hopcount_analysis.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(csv_rows)


