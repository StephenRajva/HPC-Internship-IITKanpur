import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

print("=" * 65)
print("   PATTERN I: ADJACENT PAIRING - mpi_adjacent.c")
print("=" * 65)
print()
print("Pattern: Process i sends to Process i+1")
print("Pairs  : 0->1, 2->3, 4->5, 6->7 ...")
print("Rule   : Even ranks SEND, Odd ranks RECEIVE")
print()
print("With 4 processes:")
print("  Rank 0 -> Rank 1  (even sends to next)")
print("  Rank 2 -> Rank 3  (even sends to next)")
print()
print("With 8 processes:")
print("  Rank 0->1, 2->3, 4->5, 6->7")
print()
mpip = {"Send R0":0.040,"Send R1":0.058,"Recv R2":0.373,"Recv R3":0.260}
mpi_pct = {"Send R0":43.96,"Send R1":43.28,"Recv R2":91.87,"Recv R3":95.59}
print(f"  {'Process':<12} {'Time(ms)':>10} {'MPI%':>8}")
print(f"  {'-'*12} {'-'*10} {'-'*8}")
for k in mpip:
    print(f"  {k:<12} {mpip[k]:>10.3f} {mpi_pct[k]:>8.2f}%")
print()
print("KEY FINDINGS:")
print("  Senders  : ~44% time in MPI")
print("  Receivers: ~95% time in MPI (BOTTLENECK - waiting!)")
print("  Send latency : 0.040 ms")
print("  Recv latency : 0.260 ms")
print()

fig = plt.figure(figsize=(16,12))
fig.suptitle('Pattern I: Adjacent Pairing (0->1, 2->3)\nmpi_adjacent.c', fontsize=15, fontweight='bold')
colors_role = ['#2196F3','#2196F3','#F44336','#F44336']

ax1 = fig.add_subplot(3,3,1)
ax1.set_xlim(0,10); ax1.set_ylim(0,10); ax1.axis('off')
ax1.set_title('Communication Pattern\n(4 processes)', fontweight='bold')
for x,y,lbl,c in [(2,7,'Rank 0\n(SEND)','#2196F3'),(8,7,'Rank 1\n(RECV)','#F44336'),(2,4,'Rank 2\n(SEND)','#2196F3'),(8,4,'Rank 3\n(RECV)','#F44336')]:
    ax1.add_patch(plt.Rectangle((x-1,y-0.7),2,1.4,color=c,alpha=0.85,zorder=3))
    ax1.text(x,y,lbl,ha='center',va='center',fontsize=8,color='white',fontweight='bold',zorder=4)
ax1.annotate('',xy=(7,7),xytext=(3,7),arrowprops=dict(arrowstyle='->',color='black',lw=2))
ax1.text(5,7.5,'20 bytes',ha='center',fontsize=8)
ax1.annotate('',xy=(7,4),xytext=(3,4),arrowprops=dict(arrowstyle='->',color='black',lw=2))
ax1.text(5,4.5,'20 bytes',ha='center',fontsize=8)
ax1.legend(handles=[mpatches.Patch(color='#2196F3',label='Sender'),mpatches.Patch(color='#F44336',label='Receiver')],loc='lower center',fontsize=8)

ax2 = fig.add_subplot(3,3,2)
calls=['Send\nR0','Send\nR1','Recv\nR2','Recv\nR3']
lats=[0.040,0.058,0.373,0.260]
bars=ax2.bar(calls,lats,color=colors_role,edgecolor='black')
ax2.set_title('MPI Call Latency\n(milliseconds)',fontweight='bold')
ax2.set_ylabel('Time (ms)')
ax2.set_ylim(0,max(lats)*1.35)
for bar,v in zip(bars,lats):
    ax2.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.005,f'{v:.3f}ms',ha='center',va='bottom',fontsize=9,fontweight='bold')
ax2.grid(axis='y',alpha=0.3); ax2.spines['top'].set_visible(False); ax2.spines['right'].set_visible(False)

ax3 = fig.add_subplot(3,3,3)
pcts=[43.96,43.28,91.87,95.59]
bars=ax3.bar(calls,pcts,color=colors_role,edgecolor='black')
ax3.set_title('Time Spent in MPI\n(% per process)',fontweight='bold')
ax3.set_ylabel('MPI Time %'); ax3.set_ylim(0,115)
ax3.axhline(y=50,color='gray',linestyle='--',alpha=0.5)
for bar,v in zip(bars,pcts):
    ax3.text(bar.get_x()+bar.get_width()/2,bar.get_height()+1,f'{v:.1f}%',ha='center',va='bottom',fontsize=9,fontweight='bold')
ax3.grid(axis='y',alpha=0.3); ax3.spines['top'].set_visible(False); ax3.spines['right'].set_visible(False)

ax4 = fig.add_subplot(3,3,4)
N_vals=[5,10,50,100,500,1000]
bytes_vals=[n*4 for n in N_vals]
ax4.plot(N_vals,bytes_vals,'bo-',linewidth=2,markersize=8)
ax4.fill_between(N_vals,bytes_vals,alpha=0.2,color='blue')
ax4.set_title('Bytes Transferred vs N',fontweight='bold')
ax4.set_xlabel('N (array size)'); ax4.set_ylabel('Bytes per Send')
ax4.grid(alpha=0.3); ax4.spines['top'].set_visible(False); ax4.spines['right'].set_visible(False)

ax5 = fig.add_subplot(3,3,5)
roles=['Sender\n(R0)','Receiver\n(R2)']
mpi_t=[43.96,91.87]; comp_t=[56.04,8.13]
x=np.arange(2)
ax5.bar(x,mpi_t,label='MPI Time',color='#F44336',edgecolor='black')
ax5.bar(x,comp_t,bottom=mpi_t,label='Compute',color='#4CAF50',edgecolor='black')
ax5.set_title('Time Breakdown\nMPI vs Compute',fontweight='bold')
ax5.set_ylabel('%'); ax5.set_xticks(x); ax5.set_xticklabels(roles); ax5.set_ylim(0,115)
ax5.legend(fontsize=9)
for i,(m,c) in enumerate(zip(mpi_t,comp_t)):
    ax5.text(i,m/2,f'{m:.1f}%',ha='center',va='center',fontsize=9,color='white',fontweight='bold')
    ax5.text(i,m+c/2,f'{c:.1f}%',ha='center',va='center',fontsize=9,color='white',fontweight='bold')
ax5.grid(axis='y',alpha=0.3); ax5.spines['top'].set_visible(False); ax5.spines['right'].set_visible(False)

ax6 = fig.add_subplot(3,3,6)
procs=[2,4,6,8]; pairs=[1,2,3,4]
ax6.bar(procs,pairs,color='#9C27B0',edgecolor='black',width=0.8)
ax6.set_title('Pairs vs Process Count',fontweight='bold')
ax6.set_xlabel('Processes'); ax6.set_ylabel('Pairs'); ax6.set_xticks(procs)
for p,c in zip(procs,pairs):
    ax6.text(p,c+0.03,f'{c}',ha='center',va='bottom',fontsize=10,fontweight='bold')
ax6.grid(axis='y',alpha=0.3); ax6.spines['top'].set_visible(False); ax6.spines['right'].set_visible(False)

ax7 = fig.add_subplot(3,3,7)
pairs_8=['0->1','2->3','4->5','6->7']
first_elems=[0,20,40,60]
bars=ax7.bar(pairs_8,first_elems,color=['#2196F3','#4CAF50','#FF9800','#9C27B0'],edgecolor='black')
ax7.set_title('First Element Values\n(8 processes, N=10)',fontweight='bold')
ax7.set_xlabel('Pair'); ax7.set_ylabel('Value (rank x 10)'); ax7.set_ylim(0,80)
for bar,v in zip(bars,first_elems):
    ax7.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.5,str(v),ha='center',va='bottom',fontsize=11,fontweight='bold')
ax7.grid(axis='y',alpha=0.3); ax7.spines['top'].set_visible(False); ax7.spines['right'].set_visible(False)

ax8 = fig.add_subplot(3,3,8)
sizes=['N=5\n(20B)','N=1000\n(4000B)']
times=[0.195,0.195]
ax8.bar(sizes,times,color=['#42A5F5','#1565C0'],edgecolor='black',width=0.4)
ax8.set_title('Total Time vs Array Size',fontweight='bold')
ax8.set_ylabel('Seconds'); ax8.set_ylim(0,0.3)
for i,v in enumerate(times):
    ax8.text(i,v+0.005,f'{v:.3f}s',ha='center',va='bottom',fontsize=10,fontweight='bold')
ax8.grid(axis='y',alpha=0.3); ax8.spines['top'].set_visible(False); ax8.spines['right'].set_visible(False)

ax9 = fig.add_subplot(3,3,9); ax9.axis('off')
summary=[('Pattern','0->1, 2->3, 4->5'),('Rule','Even SEND, Odd RECV'),('Pairs (4 proc)','2 pairs'),('Pairs (8 proc)','4 pairs'),('Send Latency','0.040 ms'),('Recv Latency','0.260 ms'),('Sender MPI%','43.96%'),('Receiver MPI%','95.59%'),('Bottleneck','Receiver waits!'),('Bytes (N=5)','20 bytes'),('Bytes (N=1000)','4000 bytes')]
y=0.95
for l,v in summary:
    ax9.text(0.02,y,f'{l}:',fontsize=9,fontweight='bold',transform=ax9.transAxes,va='top')
    ax9.text(0.50,y,v,fontsize=9,transform=ax9.transAxes,va='top',color='#1565C0')
    y-=0.087
ax9.set_title('Summary Card',fontweight='bold')
ax9.add_patch(plt.Rectangle((0,0),1,1,fill=False,edgecolor='#2196F3',linewidth=2,transform=ax9.transAxes))

plt.tight_layout(rect=[0,0,1,0.95])
out=os.path.expanduser('~/Downloads/adjacent_results.png')
plt.savefig(out,dpi=150,bbox_inches='tight')
plt.close()
print(f"Graph saved: {out}")
