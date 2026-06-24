import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

print("=" * 65)
print("   PATTERN II: HALF SHIFT - mpi_halfshift.c")
print("=" * 65)
print()
print("Pattern: First half sends to second half")
print("Rule   : Rank i (i < P/2) sends to Rank i + P/2")
print()
print("With 4 processes (half=2):")
print("  Rank 0 -> Rank 2  (0+2=2)")
print("  Rank 1 -> Rank 3  (1+2=3)")
print()
print("With 8 processes (half=4):")
print("  Rank 0->4, 1->5, 2->6, 3->7")
print()
mpip={"Send R0":0.040,"Send R1":0.058,"Recv R2":0.373,"Recv R3":0.260}
mpi_pct={"Send R0":43.96,"Send R1":43.28,"Recv R2":91.87,"Recv R3":95.59}
print(f"  {'Process':<12} {'Time(ms)':>10} {'MPI%':>8}")
print(f"  {'-'*12} {'-'*10} {'-'*8}")
for k in mpip:
    print(f"  {k:<12} {mpip[k]:>10.3f} {mpi_pct[k]:>8.2f}%")
print()
print("KEY FINDINGS:")
print("  Senders  : ~44% time in MPI")
print("  Receivers: ~92-96% time in MPI (waiting!)")
print("  Recv latency HIGHER than Adjacent (farther partners)")
print()
print(f"  {'Metric':<25} {'Adjacent':>12} {'HalfShift':>12}")
print(f"  {'-'*25} {'-'*12} {'-'*12}")
print(f"  {'Send latency (ms)':<25} {'0.040':>12} {'0.040':>12}")
print(f"  {'Recv latency (ms)':<25} {'0.260':>12} {'0.373':>12}")
print(f"  {'Partner distance':<25} {'i+1':>12} {'i+P/2':>12}")
print()

fig=plt.figure(figsize=(16,12))
fig.suptitle('Pattern II: Half Shift (0->P/2, 1->P/2+1)\nmpi_halfshift.c',fontsize=15,fontweight='bold')
colors_role=['#2196F3','#2196F3','#F44336','#F44336']

ax1=fig.add_subplot(3,3,1)
ax1.set_xlim(0,10);ax1.set_ylim(0,10);ax1.axis('off')
ax1.set_title('Pattern (4 processes)\nFirst Half -> Second Half',fontweight='bold')
for x,y,lbl,c in [(2,8,'Rank 0\n(SEND)','#2196F3'),(4,8,'Rank 1\n(SEND)','#2196F3'),(6,8,'Rank 2\n(RECV)','#F44336'),(8,8,'Rank 3\n(RECV)','#F44336')]:
    ax1.add_patch(plt.Rectangle((x-0.9,y-0.6),1.8,1.2,color=c,alpha=0.85,zorder=3))
    ax1.text(x,y,lbl,ha='center',va='center',fontsize=7.5,color='white',fontweight='bold',zorder=4)
ax1.annotate('',xy=(5.1,6.5),xytext=(2,7.4),arrowprops=dict(arrowstyle='->',color='#1565C0',lw=2.5,connectionstyle='arc3,rad=-0.3'))
ax1.text(3.3,5.8,'0->2',fontsize=9,color='#1565C0',fontweight='bold')
ax1.annotate('',xy=(7.1,6.5),xytext=(4,7.4),arrowprops=dict(arrowstyle='->',color='#1B5E20',lw=2.5,connectionstyle='arc3,rad=-0.3'))
ax1.text(5.3,5.8,'1->3',fontsize=9,color='#1B5E20',fontweight='bold')
ax1.text(5,2.5,'half = P/2 = 2',ha='center',fontsize=10,fontweight='bold',color='gray')
ax1.legend(handles=[mpatches.Patch(color='#2196F3',label='Sender (rank<P/2)'),mpatches.Patch(color='#F44336',label='Receiver (rank>=P/2)')],loc='lower center',fontsize=8)

ax2=fig.add_subplot(3,3,2)
ax2.set_xlim(0,10);ax2.set_ylim(0,10);ax2.axis('off')
ax2.set_title('Pattern (8 processes)\nFirst 4 -> Last 4',fontweight='bold')
senders=[(1.5,8),(3.5,8),(5.5,8),(7.5,8)]
receivers=[(1.5,4),(3.5,4),(5.5,4),(7.5,4)]
for (x,y),lbl in zip(senders,['R0\n(S)','R1\n(S)','R2\n(S)','R3\n(S)']):
    ax2.add_patch(plt.Rectangle((x-0.7,y-0.6),1.4,1.2,color='#2196F3',alpha=0.85,zorder=3))
    ax2.text(x,y,lbl,ha='center',va='center',fontsize=8,color='white',fontweight='bold',zorder=4)
for (x,y),lbl in zip(receivers,['R4\n(R)','R5\n(R)','R6\n(R)','R7\n(R)']):
    ax2.add_patch(plt.Rectangle((x-0.7,y-0.6),1.4,1.2,color='#F44336',alpha=0.85,zorder=3))
    ax2.text(x,y,lbl,ha='center',va='center',fontsize=8,color='white',fontweight='bold',zorder=4)
for (sx,sy),(rx,ry),c in zip(senders,receivers,['#1565C0','#1B5E20','#E65100','#6A1B9A']):
    ax2.annotate('',xy=(rx,ry+0.6),xytext=(sx,sy-0.6),arrowprops=dict(arrowstyle='->',color=c,lw=1.8))
ax2.text(5,1.5,'half = P/2 = 4',ha='center',fontsize=10,fontweight='bold',color='gray')

ax3=fig.add_subplot(3,3,3)
calls=['Send\nR0','Send\nR1','Recv\nR2','Recv\nR3']
lats=[0.040,0.058,0.373,0.260]
bars=ax3.bar(calls,lats,color=colors_role,edgecolor='black')
ax3.set_title('MPI Call Latency\nSend vs Recv',fontweight='bold')
ax3.set_ylabel('Time (ms)');ax3.set_ylim(0,max(lats)*1.35)
for bar,v in zip(bars,lats):
    ax3.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.005,f'{v:.3f}ms',ha='center',va='bottom',fontsize=9,fontweight='bold')
ax3.grid(axis='y',alpha=0.3);ax3.spines['top'].set_visible(False);ax3.spines['right'].set_visible(False)

ax4=fig.add_subplot(3,3,4)
pcts=[43.96,43.28,91.87,95.59]
bars=ax4.bar(calls,pcts,color=colors_role,edgecolor='black')
ax4.set_title('Time in MPI per Process',fontweight='bold')
ax4.set_ylabel('MPI Time %');ax4.set_ylim(0,115)
ax4.axhline(y=50,color='gray',linestyle='--',alpha=0.5)
for bar,v in zip(bars,pcts):
    ax4.text(bar.get_x()+bar.get_width()/2,bar.get_height()+1,f'{v:.1f}%',ha='center',va='bottom',fontsize=9,fontweight='bold')
ax4.grid(axis='y',alpha=0.3);ax4.spines['top'].set_visible(False);ax4.spines['right'].set_visible(False)

ax5=fig.add_subplot(3,3,5)
roles=['Sender\n(R0)','Receiver\n(R2)']
mpi_t=[43.96,91.87];comp_t=[56.04,8.13]
x=np.arange(2)
ax5.bar(x,mpi_t,label='MPI Time',color='#F44336',edgecolor='black')
ax5.bar(x,comp_t,bottom=mpi_t,label='Compute',color='#4CAF50',edgecolor='black')
ax5.set_title('Time Breakdown\nMPI vs Compute',fontweight='bold')
ax5.set_ylabel('%');ax5.set_xticks(x);ax5.set_xticklabels(roles);ax5.set_ylim(0,115)
ax5.legend(fontsize=9)
for i,(m,c) in enumerate(zip(mpi_t,comp_t)):
    ax5.text(i,m/2,f'{m:.1f}%',ha='center',va='center',fontsize=9,color='white',fontweight='bold')
    ax5.text(i,m+c/2,f'{c:.1f}%',ha='center',va='center',fontsize=9,color='white',fontweight='bold')
ax5.grid(axis='y',alpha=0.3);ax5.spines['top'].set_visible(False);ax5.spines['right'].set_visible(False)

ax6=fig.add_subplot(3,3,6)
procs=[2,4,6,8,10,12];pairs=[p//2 for p in procs]
ax6.plot(procs,pairs,'go-',linewidth=2,markersize=8)
ax6.fill_between(procs,pairs,alpha=0.2,color='green')
ax6.set_title('Pairs vs Process Count\n(always P/2)',fontweight='bold')
ax6.set_xlabel('Processes (P)');ax6.set_ylabel('Pairs (P/2)');ax6.set_xticks(procs)
ax6.grid(alpha=0.3);ax6.spines['top'].set_visible(False);ax6.spines['right'].set_visible(False)

ax7=fig.add_subplot(3,3,7)
pairs_8=['0->4','1->5','2->6','3->7']
first_elems=[0,10,20,30]
bars=ax7.bar(pairs_8,first_elems,color=['#2196F3','#4CAF50','#FF9800','#9C27B0'],edgecolor='black')
ax7.set_title('First Element Values\n(8 processes, N=10)',fontweight='bold')
ax7.set_xlabel('Pair');ax7.set_ylabel('Value (rank x 10)');ax7.set_ylim(0,40)
for bar,v in zip(bars,first_elems):
    ax7.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.3,str(v),ha='center',va='bottom',fontsize=11,fontweight='bold')
ax7.grid(axis='y',alpha=0.3);ax7.spines['top'].set_visible(False);ax7.spines['right'].set_visible(False)

ax8=fig.add_subplot(3,3,8)
patterns=['Adjacent\n0->1','HalfShift\n0->P/2']
send_lat=[0.040,0.040];recv_lat=[0.260,0.373]
x=np.arange(2);w=0.35
b1=ax8.bar(x-w/2,send_lat,w,label='Send',color='#2196F3',edgecolor='black')
b2=ax8.bar(x+w/2,recv_lat,w,label='Recv',color='#F44336',edgecolor='black')
ax8.set_title('Adjacent vs HalfShift\nLatency',fontweight='bold')
ax8.set_ylabel('Time (ms)');ax8.set_xticks(x);ax8.set_xticklabels(patterns);ax8.set_ylim(0,0.5)
ax8.legend(fontsize=9)
for bar,v in zip(list(b1)+list(b2),send_lat+recv_lat):
    ax8.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.005,f'{v:.3f}',ha='center',va='bottom',fontsize=9,fontweight='bold')
ax8.grid(axis='y',alpha=0.3);ax8.spines['top'].set_visible(False);ax8.spines['right'].set_visible(False)

ax9=fig.add_subplot(3,3,9);ax9.axis('off')
summary=[('Pattern','0->P/2, 1->P/2+1'),('Rule','rank<P/2 SEND'),('Pairs (4 proc)','2 pairs'),('Pairs (8 proc)','4 pairs'),('Partner dist.','P/2 ranks away'),('Send Latency','0.040 ms'),('Recv Latency','0.373 ms'),('Sender MPI%','43.96%'),('Receiver MPI%','91.87%'),('vs Adjacent','Recv 43% slower'),('Scales as','P/2 pairs always')]
y=0.95
for l,v in summary:
    ax9.text(0.02,y,f'{l}:',fontsize=9,fontweight='bold',transform=ax9.transAxes,va='top')
    ax9.text(0.50,y,v,fontsize=9,transform=ax9.transAxes,va='top',color='#1B5E20')
    y-=0.087
ax9.set_title('Summary Card',fontweight='bold')
ax9.add_patch(plt.Rectangle((0,0),1,1,fill=False,edgecolor='#4CAF50',linewidth=2,transform=ax9.transAxes))

plt.tight_layout(rect=[0,0,1,0.95])
out=os.path.expanduser('~/Downloads/halfshift_results.png')
plt.savefig(out,dpi=150,bbox_inches='tight')
plt.close()
print(f"Graph saved: {out}")
