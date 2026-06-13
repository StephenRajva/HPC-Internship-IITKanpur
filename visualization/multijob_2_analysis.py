import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

results = {
    "Dragonfly": {"sim_time_us": 91.8707,  "Allreduce": 4.556,  "Scatter": 4.657, "Bcast": 6.501,  "Alltoall": 77.565,  "hops": 2.80},
    "Mesh":      {"sim_time_us": 235.488,  "Allreduce": 12.786, "Scatter": 8.805, "Bcast": 16.566, "Alltoall": 189.785, "hops": 21.87},
    "Torus":     {"sim_time_us": 106.084,  "Allreduce": 6.349,  "Scatter": 7.609, "Bcast": 8.878,  "Alltoall": 88.865,  "hops": 3.05},
    "Polarfly":  {"sim_time_us": 75.2969,  "Allreduce": 4.304,  "Scatter": 4.598, "Bcast": 5.954,  "Alltoall": 62.644,  "hops": 3.50},
}
colors = {'Dragonfly':'#2196F3','Mesh':'#F44336','Torus':'#4CAF50','Polarfly':'#9C27B0'}
topos = list(results.keys())
topo_colors = [colors[t] for t in topos]

print("=" * 70)
print("         Multijob_2 - FULL 4-TOPOLOGY SIMULATION RESULTS")
print("=" * 70)
print()
print("Multijob_2 runs 4 jobs SIMULTANEOUSLY on the same network.")
print("Simulates a real supercomputer where many users share resources.")
print()
print(f"  {'Topology':<12} {'Allreduce':>10} {'Scatter':>10} {'Bcast':>10} {'Alltoall':>10} {'SimTime':>10}")
print(f"  {'-'*12} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
for t, d in results.items():
    print(f"  {t:<12} {d['Allreduce']:>10.3f} {d['Scatter']:>10.3f} {d['Bcast']:>10.3f} {d['Alltoall']:>10.3f} {d['sim_time_us']:>10.3f}")
print()
print("WINNER SUMMARY (all latencies in microseconds):")
print()
for op in ['Allreduce','Scatter','Bcast','Alltoall']:
    winner = min(topos, key=lambda t: results[t][op])
    print(f"  {op:<12}: WINNER = {winner} ({results[winner][op]:.3f} us)")
print()
best = min(topos, key=lambda t: results[t]['sim_time_us'])
print(f"  OVERALL WINNER (fastest total): {best} ({results[best]['sim_time_us']:.3f} us)")
print()
print("FINAL RANKING:")
ranked = sorted(topos, key=lambda t: results[t]['sim_time_us'])
medals = ['1st', '2nd', '3rd', '4th']
for i, t in enumerate(ranked):
    print(f"  {medals[i]} {t}: {results[t]['sim_time_us']:.4f} us")
print("=" * 70)

fig = plt.figure(figsize=(18, 12))
fig.suptitle('Multijob_2 - All 4 Topologies (4 Jobs Simultaneously)', fontsize=16, fontweight='bold')

ops = ['Allreduce','Scatter','Bcast','Alltoall']
op_titles = ['Allreduce Latency','Scatter Latency','Broadcast Latency','Alltoall Latency\n(Most Important)']

for i, (op, title) in enumerate(zip(ops, op_titles)):
    ax = fig.add_subplot(3, 3, i+1)
    vals = [results[t][op] for t in topos]
    bars = ax.bar(topos, vals, color=topo_colors, edgecolor='black', linewidth=0.8)
    ax.set_title(title, fontweight='bold', fontsize=11)
    ax.set_ylabel('Latency (us)', fontsize=9)
    ax.set_ylim(0, max(vals)*1.3)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+max(vals)*0.02,
                f'{v:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.tick_params(axis='x', labelsize=8)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

ax5 = fig.add_subplot(3, 3, 5)
sim_vals = [results[t]['sim_time_us'] for t in topos]
bars = ax5.bar(topos, sim_vals, color=topo_colors, edgecolor='black', linewidth=0.8)
ax5.set_title('Total Simulation Time\n(Overall Winner)', fontweight='bold', fontsize=11)
ax5.set_ylabel('Time (us)', fontsize=9)
ax5.set_ylim(0, max(sim_vals)*1.3)
for bar, v in zip(bars, sim_vals):
    ax5.text(bar.get_x()+bar.get_width()/2, bar.get_height()+3,
             f'{v:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax5.tick_params(axis='x', labelsize=8)
ax5.grid(axis='y', alpha=0.3)
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)

ax6 = fig.add_subplot(3, 3, 6)
hop_topos = ['Dragonfly','Mesh','Torus','Polarfly']
hop_vals  = [results[t]['hops'] for t in hop_topos]
hop_colors= [colors[t] for t in hop_topos]
bars = ax6.bar(hop_topos, hop_vals, color=hop_colors, edgecolor='black', linewidth=0.8)
ax6.set_title('Avg Hop Count\n(lower = less travel = faster)', fontweight='bold', fontsize=11)
ax6.set_ylabel('Avg Hops', fontsize=9)
ax6.set_ylim(0, max(hop_vals)*1.3)
for bar, v in zip(bars, hop_vals):
    ax6.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
             f'{v:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax6.tick_params(axis='x', labelsize=8)
ax6.grid(axis='y', alpha=0.3)
ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)

ax7 = fig.add_subplot(3, 3, 7)
x = np.arange(len(topos))
width = 0.2
op_colors_list = ['#42A5F5','#66BB6A','#FFA726','#EF5350']
for i, (op, c) in enumerate(zip(ops, op_colors_list)):
    vals = [results[t][op] for t in topos]
    ax7.bar(x+i*width, vals, width, label=op, color=c, edgecolor='white', linewidth=0.5, alpha=0.9)
ax7.set_title('All Operations\nSide by Side', fontweight='bold', fontsize=11)
ax7.set_ylabel('Latency (us)', fontsize=9)
ax7.set_xticks(x+width*1.5)
ax7.set_xticklabels(topos, fontsize=8)
ax7.legend(fontsize=8)
ax7.grid(axis='y', alpha=0.3)
ax7.spines['top'].set_visible(False)
ax7.spines['right'].set_visible(False)

ax8 = fig.add_subplot(3, 3, 8)
ranked = sorted(topos, key=lambda t: results[t]['sim_time_us'])
r_times = [results[t]['sim_time_us'] for t in ranked]
r_colors = [colors[t] for t in ranked]
bars = ax8.barh(ranked, r_times, color=r_colors, edgecolor='black', linewidth=0.8)
ax8.set_title('Final Ranking\n(Total Simulation Time)', fontweight='bold', fontsize=11)
ax8.set_xlabel('Total Time (us)', fontsize=9)
ranks_label = ['1st','2nd','3rd','4th']
for i, (bar, v) in enumerate(zip(bars, r_times)):
    ax8.text(v+2, bar.get_y()+bar.get_height()/2,
             f'{ranks_label[i]}: {v:.1f} us', va='center', fontsize=9, fontweight='bold')
ax8.set_xlim(0, max(r_times)*1.35)
ax8.grid(axis='x', alpha=0.3)
ax8.spines['top'].set_visible(False)
ax8.spines['right'].set_visible(False)

ax9 = fig.add_subplot(3, 3, 9)
max_vals = {'Allreduce':12.786,'Scatter':8.805,'Bcast':16.566,'Alltoall':189.785,'SimTime':235.488}
scores = {}
for t in topos:
    s = [(1 - results[t][op]/max_vals[op])*100 for op in ['Allreduce','Scatter','Bcast','Alltoall']]
    s.append((1 - results[t]['sim_time_us']/max_vals['SimTime'])*100)
    scores[t] = sum(s)/len(s)
score_vals = [scores[t] for t in topos]
bars = ax9.bar(topos, score_vals, color=topo_colors, edgecolor='black', linewidth=0.8)
ax9.set_title('Overall Performance Score\n(higher = better)', fontweight='bold', fontsize=11)
ax9.set_ylabel('Score (0-100)', fontsize=9)
ax9.set_ylim(0, 110)
for bar, v in zip(bars, score_vals):
    ax9.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
             f'{v:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax9.tick_params(axis='x', labelsize=8)
ax9.grid(axis='y', alpha=0.3)
ax9.spines['top'].set_visible(False)
ax9.spines['right'].set_visible(False)

legend_patches = [mpatches.Patch(color=colors[t], label=t) for t in topos]
fig.legend(handles=legend_patches, loc='lower center', ncol=4, fontsize=11, bbox_to_anchor=(0.5,-0.02))
plt.tight_layout(rect=[0,0.03,1,0.96])
out = os.path.expanduser('~/Downloads/multijob_2_results.png')
plt.savefig(out, dpi=150, bbox_inches='tight')
plt.close()
print(f"\nGraph saved: {out}")
