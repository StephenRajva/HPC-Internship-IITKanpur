import math
from collections import Counter

def calculate_hop_count(node_i, node_j, num_groups, routers_per_group, hosts_per_router, intergroup_links):
    # Decompose node addresses
    nodes_per_group = routers_per_group * hosts_per_router
    group_i = node_i // nodes_per_group
    group_j = node_j // nodes_per_group

    router_i = (node_i % nodes_per_group) // hosts_per_router
    router_j = (node_j % nodes_per_group) // hosts_per_router
    
    # Same group
    if group_i == group_j:
        if router_i == router_j:# Same router
            return 2
        else:
            return 3
    # Different groups   
    else:
        # Determine if groups are directly connected
        groups_per_router = num_groups // intergroup_links
        for link in range(intergroup_links):
            dest_group = (group_i + link * groups_per_router + 1) % num_groups
            if dest_group == group_j:
                return 4
        return 5

def calculate_job_hop_count(job, num_groups, routers_per_group, hosts_per_router, intergroup_links):
    start = job["start"]
    size = job["size"]
    nodes = list(range(start, start + size))
    total_hops = 0
    count = 0
    hop_counter = Counter()

    # Scatter/Bcast: Only root communicates with others
    if job["pattern"] in ["Scatter", "Bcast"]:
        root = nodes[0]
        for node_j in nodes[1:]:
            hops = calculate_hop_count(root, node_j, num_groups, routers_per_group, hosts_per_router, intergroup_links)
            total_hops += hops
            hop_counter[hops] += 1
            count += 1
     # Allreduce/Alltoall: All pairs communicate       
    else: 
        for i in nodes:
            for j in nodes:
                if i != j:
                    hops = calculate_hop_count(i, j, num_groups, routers_per_group, hosts_per_router, intergroup_links)
                    total_hops += hops
                    hop_counter[hops] += 1
                    count += 1

    avg = total_hops / count if count > 0 else 0
    return avg, hop_counter

# Parameters for dragonfly
num_groups = 16
routers_per_group = 8
hosts_per_router = 4
intergroup_links = 4

jobs = [
    {"size": 16, "start": 0, "pattern": "Allreduce"},
    {"size": 64, "start": 16, "pattern": "Alltoall"},
    {"size": 32, "start": 80, "pattern": "Scatter"},
    {"size": 64, "start": 112, "pattern": "Bcast"}
]

# Print results
print("Hop Count Analysis Per Job:\n")
for idx, job in enumerate(jobs):
    avg_hops, hop_dist = calculate_job_hop_count(job, num_groups, routers_per_group, hosts_per_router, intergroup_links)
    print(f"  Job {idx + 1}: {job['pattern']} (size={job['size']})")
    print(f"     Average Hop Count: {avg_hops:.2f}")
    print(f"     Hop Count Breakdown: {dict(hop_dist)}\n")

