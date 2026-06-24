import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

print("=" * 65)
print("   PATTERN III: MIRRORED PAIRING - mpi_mirrored.c")
print("=" * 65)
print()
print("Pattern: Process i pairs with Process (P-1-i)")
print("Rule   : rank < P/2 SENDS, rank >= P/2 RECEIVES")
print()
print("With 4 processes (P=4):")
print("  Rank 0 -> Rank 3  (partner=3-0=3) OUTER pair")
print("  Rank 1 -> Rank 2  (partner=3-1=2) INNER pair")
print()
print("With 8 processes (P=8):")
print("  Rank 0->7, 1->6, 2->5, 3->4")
print()
mpip={"Send R0":0.040,"Send R1":0.058,"Recv R2":0.373,"Recv R3":0.260}
mpi_pct={"Send R0":43.96,"Send R1":43.28,"Recv R2":91.87,"Recv R3":95.59}
partners={"Send R0":3,"Send R1":2,"Recv R2":1,"Recv R3":0}
print(f"  {'Process':<12} {'Partner':>8} {'Time(ms)':>10} {'MPI%':>8}")
print(f"  {'-'*12} {'-'*8} {'-'*10} {'-'*8}")
for k in mpip:
    print(f"  {k:<12} {partners[k]:>8} {mpip[k]:>10.3f} {mpi_pct[k]:>8.2f}%")
print()
print("KEY FINDINGS:")
print("  Rank 0 talks to FARTHEST rank (P-1)!")
print("  Creates butterfly/mirror communication pattern")
print("  Used in FFT algorithms")
print()
print("ALL 3 PATTERNS COMPARED:")
print(f"  {'Pattern':<12} {'Send':>8} {'Recv':>8} {'Partner':>10} {'Use Case'}")
print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*10} {'-'*15}")
print(f"  {'Adjacent':<12} {'0.040ms':>8} {'0.260ms':>8} {'i+1':>10} Pipeline/Image")
print(f"  {'HalfShift':<12} {'0.040ms':>8} {'0.373ms':>8} {'i+P/2':>10} Matrix/Sort")
print(f"  {'Mirrored':<12} {'0.040ms':>8} {'0.373ms':>8} {'P-1-i':>10} FFT/Butterfly")
print()

fig=plt.figure(figsize=(16,12))
fig.suptitle('Pattern III: Mirrored Pairing (0->P-1, 1->P-2)\nmpi_mirrored.c',fontsize=15,fontweight='bold')
colors_role=['#2196F3','#2196F3','#F44336','#F44336']

ax1=fig.add_subplot(3,3,1)
ax1.set_xlim(0,10);ax1.set_ylim(0,10);ax1.axis('off')
ax1.set_title('Pattern (4 processes)\nMirror Reflection',fontweight='bold')
for x,y,lbl,c in [(1.5,7,'Rank 0\n(SEND)','#2196F3'),(3.5,7,'Rank 1\n(SEND)','#2196F3'),(6.5,7,'Rank 2\n(RECV)','#F44336'),(8.5,7,'Rank 3\n(RECV)','#F44336')]:
    ax1.add_patch(plt.Rectangle((x-0.9,y-0.6),1.8,1.2,color=c,alpha=0.85,zorder=3))
    ax1.text(x,y,lbl,ha='center',va='center',fontsize=7.5,color='white',fontweight='bold',zorder=4)
ax1.annotate('',xy=(7.6,5.5),xytext=(1.5,6.4),arrowprops=dict(arrowstyle='->',color='#1565C0',lw=2.5,connectionstyle='arc3,rad=0.4'))
ax1.text(5,3.8,'0->3\n(OUTER)',ha='center',fontsize=9,color='#1565C0',fontweight='bold')
ax1.annotate('',xy=(5.6,6.2),xytext=(3.5,6.4),arrowprops=dict(arrowstyle='->',color='#1B5E20',lw=2.5,connectionstyle='arc3,rad=0.3'))
ax1.text(5,5.0,'1->2\n(INNER)',ha='center',fontsize=9,color='#1B5E20',fontweight='bold')
ax1.axvline(x=5,color='gray',linestyle='--',alpha=0.7,linewidth=1.5)
ax1.text(5,9,'|mirror|',ha='center',fontsize=9,color='gray',style='italic')
ax1.legend(handles=[mpatches.Patch(color='#2196F3',label='Sender'),mpatches.Patch(color='#F44336',label='Receiver')],loc='lower center',fontsize=8)

ax2=fig.add_subplot(3,3,2)
ax2.set_xlim(0,10);ax2.set_ylim(0,10);ax2.axis('off')
ax2.set_title('Pattern (8 processes)\nButterfly Structure',fontweight='bold')
x_pos=[1,2.3,3.6,4.9,5.2,6.5,7.8,9.1]
for i,x in enumerate(x_pos[:4]):
    ax2.add_patch(plt.Rectangle((x-0.5,7-0.4),1.0,0.8,color='#2196F3',alpha=0.85,zorder=3))
    ax2.text(x,7,f'R{i}',ha='center',va='center',fontsize=8,color='white',fontweight='bold',zorder=4)
for i,x in enumerate(x_pos[4:]):
    ax2.add_patch(plt.Rectangle((x-0.5,3-0.4),1.0,0.8,color='#F44336',alpha=0.85,zorder=3))
    ax2.text(x,3,f'R{i+4}',ha='center',va='center',fontsize=8,color='white',fontweight='bold',zorder=4)
for (si,ri),c in zip([(0,7),(1,6),(2,5),(3,4)],['#1565C0','#1B5E20','#E65100','#6A1B9A']):
    ax2.annotate('',xy=(x_pos[ri],3.4),xytext=(x_pos[si],6.6),arrowprops=dict(arrowstyle='->',color=c,lw=1.8))
ax2.text(5,1.5,'partner = (P-1) - rank',ha='center',fontsize=9,color='gray',style='italic')

ax3=fig.add_subplot(3,3,3)
calls=['Send\nR0','Send\nR1','Recv\nR2','Recv\nR3']
lats=[0.040,0.058,0.373,0.260]
bars=ax3.bar(calls,lats,color=colors_role,edgecolor='black')
ax3.set_title('MPI Call Latency\nOuter vs Inner',fontweight='bold')
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
roles=['Sender\n(R0)','Receiver\n(R3)']
mpi_t=[43.96,95.59];comp_t=[56.04,4.41]
x=np.arange(2)
ax5.bar(x,mpi_t,label='MPI Time',color='#F44336',edgecolor='black')
ax5.bar(x,comp_t,bottom=mpi_t,label='Compute',color='#4CAF50',edgecolor='black')
ax5.set_title('Time Breakdown\nOuter Pair (0->3)',fontweight='bold')
ax5.set_ylabel('%');ax5.set_xticks(x);ax5.set_xticklabels(roles);ax5.set_ylim(0,115)
ax5.legend(fontsize=9)
for i,(m,c) in enumerate(zip(mpi_t,comp_t)):
    ax5.text(i,m/2,f'{m:.1f}%',ha='center',va='center',fontsize=9,color='white',fontweight='bold')
    ax5.text(i,m+c/2,f'{c:.1f}%',ha='center',va='center',fontsize=9,color='white',fontweight='bold')
ax5.grid(axis='y',alpha=0.3);ax5.spines['top'].set_visible(False);ax5.spines['right'].set_visible(False)

ax6=fig.add_subplot(3,3,6)
P=8;ranks=list(range(P//2))
distances=[abs((P-1-r)-r) for r in ranks]
labels_d=[f'R{r}->R{P-1-r}' for r in ranks]
bars=ax6.bar(labels_d,distances,color=['#1565C0','#1976D2','#1E88E5','#42A5F5'],edgecolor='black')
ax6.set_title('Partner Distance\n(8 processes)',fontweight='bold')
ax6.set_ylabel('Rank difference');ax6.set_ylim(0,max(distances)*1.3)
for bar,v in zip(bars,distances):
    ax6.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.05,f'{v}',ha='center',va='bottom',fontsize=10,fontweight='bold')
ax6.grid(axis='y',alpha=0.3);ax6.spines['top'].set_visible(False);ax6.spines['right'].set_visible(False)

ax7=fig.add_subplot(3,3,7)
patterns=['Adjacent\n0->1','HalfShift\n0->P/2','Mirrored\n0->P-1']
send_lats=[0.040,0.040,0.040];recv_lats=[0.260,0.373,0.373]
x=np.arange(3);w=0.35
ax7.bar(x-w/2,send_lats,w,label='Send',color='#2196F3',edgecolor='black')
ax7.bar(x+w/2,recv_lats,w,label='Recv',color='#F44336',edgecolor='black')
ax7.set_title('All 3 Patterns\nLatency Comparison',fontweight='bold')
ax7.set_ylabel('Time (ms)');ax7.set_xticks(x);ax7.set_xticklabels(patterns,fontsize=8);ax7.set_ylim(0,0.5)
ax7.legend(fontsize=9)
ax7.grid(axis='y',alpha=0.3);ax7.spines['top'].set_visible(False);ax7.spines['right'].set_visible(False)

ax8=fig.add_subplot(3,3,8)
patterns_s=['Adjacent','HalfShift','Mirrored']
sender_p=[43.96,43.96,43.96];receiver_p=[95.59,91.87,95.59]
x=np.arange(3);w=0.35
ax8.bar(x-w/2,sender_p,w,label='Sender MPI%',color='#2196F3',edgecolor='black',alpha=0.9)
ax8.bar(x+w/2,receiver_p,w,label='Receiver MPI%',color='#F44336',edgecolor='black',alpha=0.9)
ax8.set_title('Sender vs Receiver MPI%\nAll 3 Patterns',fontweight='bold')
ax8.set_ylabel('MPI Time %');ax8.set_xticks(x);ax8.set_xticklabels(patterns_s,fontsize=9);ax8.set_ylim(0,115)
ax8.axhline(y=50,color='gray',linestyle='--',alpha=0.5)
ax8.legend(fontsize=8)
for i,(s,r) in enumerate(zip(sender_p,receiver_p)):
    ax8.text(i-w/2,s+1,f'{s:.0f}%',ha='center',va='bottom',fontsize=8,fontweight='bold')
    ax8.text(i+w/2,r+1,f'{r:.0f}%',ha='center',va='bottom',fontsize=8,fontweight='bold')
ax8.grid(axis='y',alpha=0.3);ax8.spines['top'].set_visible(False);ax8.spines['right'].set_visible(False)

ax9=fig.add_subplot(3,3,9);ax9.axis('off')
summary=[('Pattern','0->P-1, 1->P-2'),('Formula','partner=(P-1)-rank'),('Pairs (4 proc)','2 mirror pairs'),('Pairs (8 proc)','4 mirror pairs'),('Outer pair','0 <-> P-1 (far!)'),('Inner pair','1 <-> P-2 (close)'),('Send Latency','0.040 ms'),('Recv Latency','0.373 ms'),('Sender MPI%','43.96%'),('Receiver MPI%','95.59%'),('Use case','FFT/Butterfly algo')]
y=0.95
for l,v in summary:
    ax9.text(0.02,y,f'{l}:',fontsize=9,fontweight='bold',transform=ax9.transAxes,va='top')
    ax9.text(0.50,y,v,fontsize=9,transform=ax9.transAxes,va='top',color='#880E4F')
    y-=0.087
ax9.set_title('Summary Card',fontweight='bold')
ax9.add_patch(plt.Rectangle((0,0),1,1,fill=False,edgecolor='#880E4F',linewidth=2,transform=ax9.transAxes))

plt.tight_layout(rect=[0,0,1,0.95])
out=os.path.expanduser('~/Downloads/mirrored_results.png')
plt.savefig(out,dpi=150,bbox_inches='tight')
plt.close()
print(f"Graph saved: {out}")
