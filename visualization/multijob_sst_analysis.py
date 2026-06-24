import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

results = {
    "Dragonfly": {"topology": "4 groups x 4 routers x 2 hosts = 16 nodes", "jobs": 2, "total_ranks": 16, "sim_time_us": 21.1248, "operations": {"Allreduce": {"ranks": 16, "latency_us": 4.142}, "Alltoall": {"ranks": 16, "latency_us": 13.805}}},
    "Mesh":      {"topology": "2D Mesh (simple grid topology)", "jobs": 2, "total_ranks": 4, "sim_time_us": 3.80918, "operations": {"Alltoall": {"ranks": 2, "latency_us": 0.937}, "Allreduce": {"ranks": 2, "latency_us": 1.067}}}
}
colors = {'Dragonfly': '#2196F3', 'Mesh': '#FF9800'}

print("=" * 65)
print("       MultiJob_sst - SIMULATION RESULTS SUMMARY")
print("=" * 65)
print()
print("MultiJob_sst runs 2 jobs SIMULTANEOUSLY on the same network.")
print("Tests how well each topology handles shared workloads.")
print()
for topo, data in results.items():
    print("-" * 65)
    print(f"  Topology : {topo}")
    print(f"  Config   : {data['topology']}")
    print(f"  Jobs     : {data['jobs']} simultaneously")
    print(f"  Ranks    : {data['total_ranks']}")
    print(f"  Sim Time : {data['sim_time_us']:.4f} us")
    print()
    print(f"  {'Operation':<15} {'Ranks':>8} {'Latency (us)':>14}")
    print(f"  {'-'*15} {'-'*8} {'-'*14}")
    for op, vals in data['operations'].items():
        print(f"  {op:<15} {vals['ranks']:>8} {vals['latency_us']:>14.3f}")
    print()
print("-" * 65)
print()
print(f"  {'Metric':<30} {'Dragonfly':>12} {'Mesh':>12}")
print(f"  {'-'*30} {'-'*12} {'-'*12}")
print(f"  {'Allreduce Latency (us)':<30} {'4.142':>12} {'1.067':>12}")
print(f"  {'Alltoall Latency (us)':<30} {'13.805':>12} {'0.937':>12}")
print(f"  {'Total Sim Time (us)':<30} {'21.125':>12} {'3.809':>12}")
print(f"  {'Total Ranks':<30} {'16':>12} {'4':>12}")
print()
print("NOTE: Mesh looks faster because it only uses 2 ranks!")
print("Dragonfly uses 16 ranks — a much larger and harder workload.")

fig, axes = plt.subplots(1, 3, figsize=(15, 6))
fig.suptitle('MultiJob_sst - Dragonfly vs Mesh Comparison', fontsize=15, fontweight='bold')
topos = ['Dragonfly\n(16 ranks)', 'Mesh\n(2 ranks)']
topo_colors = [colors['Dragonfly'], colors['Mesh']]

for ax, (title, vals) in zip(axes, [
    ('Allreduce Latency', [4.142, 1.067]),
    ('Alltoall Latency',  [13.805, 0.937]),
    ('Total Sim Time',    [21.1248, 3.80918])
]):
    bars = ax.bar(topos, vals, color=topo_colors, edgecolor='black', width=0.5)
    ax.set_title(title, fontweight='bold')
    ax.set_ylabel('Microseconds (us)')
    ax.set_ylim(0, max(vals) * 1.3)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(vals)*0.02,
                f'{v:.3f} us', ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

legend_patches = [mpatches.Patch(color=colors['Dragonfly'], label='Dragonfly (16 ranks)'),
                  mpatches.Patch(color=colors['Mesh'], label='Mesh (2 ranks)')]
fig.legend(handles=legend_patches, loc='lower center', ncol=2, fontsize=11, bbox_to_anchor=(0.5, -0.05))
plt.tight_layout()
out = os.path.expanduser('~/Downloads/multijob_sst_results.png')
plt.savefig(out, dpi=150, bbox_inches='tight')
plt.close()
print(f"\nGraph saved: {out}")
