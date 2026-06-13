import math
import csv
from collections import Counter

# Torus hop distance calculation between routers
def torus_distance(x1, y1, x2, y2, dim_x, dim_y):
    dx = min(abs(x1 - x2), dim_x - abs(x1 - x2))
    dy = min(abs(y1 - y2), dim_y - abs(y1 - y2))
    return dx + dy

# Full hop count between nodes (including NIC<->router)
def calculate_hop_count_torus(node_i, node_j, dim_x, dim_y, hosts_per_router):
    router_i = node_i // hosts_per_router
    router_j = node_j // hosts_per_router

    if router_i == router_j:
        return 2  # same router (NIC→Router + Router→NIC)

    x1, y1 = router_i % dim_x, router_i // dim_x
    x2, y2 = router_j % dim_x, router_j // dim_x

    router_hops = torus_distance(x1, y1, x2, y2, dim_x, dim_y)
    return router_hops + 2  # +2 for NIC-router-NIC

# Calculate average and detailed hop counts for a given job
def calculate_job_hop_count(job, dim_x, dim_y, hosts_per_router):
    start = job["start"]
    size = job["size"]
    nodes = list(range(start, start + size))
    total_hops = 0
    pair_count = 0
    hop_counter = Counter()
    pattern = job["pattern"]

    if pattern in ["Scatter", "Bcast"]:
        root = nodes[0]
        for node in nodes[1:]:
            hops = calculate_hop_count_torus(root, node, dim_x, dim_y, hosts_per_router)
            hop_counter[hops] += 1
            total_hops += hops
            pair_count += 1
    else:
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i != j:
                    hops = calculate_hop_count_torus(nodes[i], nodes[j], dim_x, dim_y, hosts_per_router)
                    hop_counter[hops] += 1
                    total_hops += hops
                    pair_count += 1

    avg = total_hops / pair_count if pair_count > 0 else 0
    return avg, hop_counter

# Torus topology config: 8x8 routers, 10 hosts per router = 640 nodes
dim_x, dim_y = 8, 8
hosts_per_router = 10

# Define 4 jobs
jobs = [
    {"size": 32, "start": 0, "pattern": "Allreduce"},
    {"size": 64, "start": 32, "pattern": "Alltoall"},
    {"size": 128, "start": 96, "pattern": "Scatter"},
    {"size": 256, "start": 224, "pattern": "Bcast"}
]

# Run and store outputs
job_outputs = []
print("Torus Hop Count Analysis Per Job:\n")
for idx, job in enumerate(jobs):
    avg_hops, hop_dist = calculate_job_hop_count(job, dim_x, dim_y, hosts_per_router)
    breakdown = dict(sorted(hop_dist.items()))
    print(f"  Job {idx + 1}: {job['pattern']} (size={job['size']})")
    print(f"     Average Hop Count: {avg_hops:.2f}")
    print(f"     Hop Count Breakdown: {breakdown}\n")

    job_outputs.append({
        "job": idx + 1,
        "pattern": job["pattern"],
        "size": job["size"],
        "avg": avg_hops,
        "breakdown": breakdown
    })

# Collect all unique hop types across all jobs
all_hop_types = sorted({hop for job in job_outputs for hop in job["breakdown"]})

# CSV header
header = ["Job ID", "Pattern", "Size", "Avg Hop Count"] + [str(hop) for hop in all_hop_types]

# CSV rows
rows = []
for job in job_outputs:
    row = [
        f"Job {job['job']}",
        job["pattern"],
        job["size"],
        round(job["avg"], 2),
    ]
    for hop in all_hop_types:
        row.append(job["breakdown"].get(hop, ""))
    rows.append(row)

# Write to CSV file
with open("torus_hopcount_table.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)

print("Hop count data saved to 'torus_hopcount_table.csv'")
