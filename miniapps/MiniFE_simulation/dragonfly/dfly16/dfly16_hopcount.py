import csv
import numpy as np
from collections import Counter

def dragonfly_hops(src, dst, num_groups, routers_per_group, hosts_per_router, intergroup_links):
    nodes_per_group = routers_per_group * hosts_per_router

    g1 = src // nodes_per_group
    g2 = dst // nodes_per_group
    r1 = (src % nodes_per_group) // hosts_per_router
    r2 = (dst % nodes_per_group) // hosts_per_router

    # Same group
    if g1 == g2:
        if r1 == r2:
            return 2  # same router: Host→Router→Host
        else:
            return 3  # same group, different router

    # Different groups
    else:
        #directly connected
        groups_per_router = max(1, num_groups // intergroup_links)
        connected = False
        for link in range(intergroup_links):
            dest_group = (g1 + link * groups_per_router + 1) % num_groups
            if dest_group == g2:
                connected = True
                break
        return 4 if connected else 5


def calculate_allpairs(size, num_groups, routers_per_group, hosts_per_router, intergroup_links):
    hops, count = 0, 0
    for i in range(size):
        for j in range(size):
            if i != j:
                h = dragonfly_hops(i, j, num_groups, routers_per_group, hosts_per_router, intergroup_links)
                hops += h
                count += 1
    return hops / count if count > 0 else 0


def calculate_rooted(size, root, num_groups, routers_per_group, hosts_per_router, intergroup_links):
    hops, count = 0, 0
    for r in range(size):
        if r != root:
            h = dragonfly_hops(root, r, num_groups, routers_per_group, hosts_per_router, intergroup_links)
            hops += h
            count += 1
    return hops / count if count > 0 else 0



num_groups = 4              
routers_per_group = 4       
hosts_per_router = 1        
intergroup_links = 2        


jobs = [
    {"pattern": "Allreduce", "size": 16},
    {"pattern": "Bcast", "size": 16, "root": 0},
    {"pattern": "Reduce", "size": 16, "root": 0},
    {"pattern": "Allgather", "size": 16},
    {"pattern": "Barrier", "size": 16},
    {"pattern": "PingPong", "pairs": [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]}
]


rows_avg = [["Pattern", "Ranks", "Avg HopCount"]]
hop_values = []

for job in jobs:
    if job["pattern"] in ["Allreduce", "Allgather"]:
        avg = calculate_allpairs(job["size"], num_groups, routers_per_group, hosts_per_router, intergroup_links)
        rows_avg.append([job["pattern"], job["size"], round(avg, 2)])
        hop_values.append(avg)

    elif job["pattern"] == "Barrier":
        size = job["size"]
        avg = 2 * (np.log2(size) + 1)   
        rows_avg.append([job["pattern"], size, round(avg, 2)])
        hop_values.append(avg)

    elif job["pattern"] in ["Bcast", "Reduce"]:
        avg = calculate_rooted(job["size"], job["root"], num_groups, routers_per_group, hosts_per_router, intergroup_links)
        rows_avg.append([job["pattern"], job["size"], round(avg, 2)])
        hop_values.append(avg)

    elif job["pattern"] == "PingPong":
        for a, b in job["pairs"]:
            hops = dragonfly_hops(a, b, num_groups, routers_per_group, hosts_per_router, intergroup_links)
            rows_avg.append([f"PingPong {a}-{b}", 2, hops])
            hop_values.append(hops)

# Overall average
overall = sum(hop_values) / len(hop_values)
rows_avg.append(["Overall", "-", round(overall, 2)])


with open("hopcount_dragonfly.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(rows_avg)

print(f"Dragonfly Hop Count Summary (Groups={num_groups}, Routers/Group={routers_per_group}, Hosts/Router={hosts_per_router}, InterLinks={intergroup_links})\n")
for row in rows_avg:
    print(f"{row[0]:<15} {row[1]:<3} {row[2]}")
