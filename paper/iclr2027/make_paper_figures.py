#!/usr/bin/env python3
"""Draw monochrome figures from archived measurements; no model/evaluator runs."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = Path(__file__).resolve().parent
D = json.loads((HERE/'source-data/rewrite_sources.json').read_text())
A = json.loads((HERE/'source-data/derived_analysis.json').read_text())
OUT = HERE/'figures'
OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,
 'axes.labelsize':8,'axes.titlesize':8.2,'xtick.labelsize':7,'ytick.labelsize':7,
 'legend.fontsize':7.4,'axes.linewidth':.6,'pdf.fonttype':42,'ps.fonttype':42,
 'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white',
 'savefig.facecolor':'white','lines.linewidth':1.5})
STYLE={'base':dict(color='.65',marker='D',ls=':'),
       'plain':dict(color='.48',marker='s',ls='--'),
       'spectral_soft':dict(color='.08',marker='o',ls='-')}
LABEL={'base':'Initial model','plain':'Plain','spectral_soft':'SPECTRUM'}

def clean(ax):
    ax.grid(axis='y',color='.9',lw=.5); ax.set_axisbelow(True)
    ax.tick_params(length=2.5,width=.6)

def save(fig,name):
    fig.savefig(OUT/(name+'.pdf'))
    fig.savefig(OUT/(name+'.png'),dpi=240)
    plt.close(fig)

def rounds(m):
    return [D['mbpp16']['base/evaluation']] + [D['mbpp16'][f'{m}/round_{r}/evaluation'] for r in range(1,6)]

# Figure 1: empirical discovery. The phase trajectory is the dominant panel.
fig=plt.figure(figsize=(6.65,2.36))
axes=[fig.add_axes(rect) for rect in ([.074,.24,.438,.59],[.622,.24,.145,.59],[.85,.24,.145,.59])]
for m in ['plain','spectral_soft']:
    ss=rounds(m)
    x=np.array([s['pass_at_1']['mean']*100 for s in ss])
    y=np.array([s['implementation_coverage_at_k']['16']['mean'] for s in ss])
    axes[0].plot(x,y,ms=3.5,label=LABEL[m],**STYLE[m])
    for r in range(1,6):
        axes[0].annotate(str(r),(x[r],y[r]),xytext=(3,6 if m=='spectral_soft' else -10),
                         textcoords='offset points',fontsize=6.5,color=STYLE[m]['color'])
    delta=[D['mbpp16_comparisons'][f'{m}/round_{r}/evaluation - base/evaluation']['implementation_proxy']['correct_matched_coverage'] for r in range(1,6)]
    ym=np.array([a['mean'] for a in delta]);ci=np.array([a['ci95'] for a in delta])
    axes[1].errorbar(range(1,6),ym,yerr=np.stack([ym-ci[:,0],ci[:,1]-ym]),
        ms=2.5,elinewidth=.5,capsize=1,**STYLE[m])
    vals=[s['implementation_simpson_diversity']['mean'] for s in ss]
    axes[2].plot(range(6),vals,ms=2.5,**STYLE[m])
axes[0].scatter([37.925],[4.016],s=24,c='.65',marker='D',zorder=8)
axes[0].annotate('Initial',(37.925,4.016),xytext=(4,6),textcoords='offset points',fontsize=7)
axes[0].set(xlabel='Pass@1 (%)',ylabel='Correct AST richness@16',xlim=(37.45,41.8),ylim=(2.92,4.17))
axes[0].set_title('(a) More accurate, fewer correct structures',loc='left',pad=10)
axes[0].legend(frameon=False,loc='lower left')
axes[1].axhline(0,c='.65',lw=.6,ls=':')
axes[1].set(xlabel='Round',ylabel=r'Paired change in $D_4$',xlim=(.6,5.4),ylim=(-.7,.02))
axes[1].set_xticks([1,3,5]);axes[1].set_title('(b) Equal successes',loc='center',pad=10)
axes[2].set(xlabel='Round',ylabel='Correct AST Simpson',xlim=(-.2,5.2),ylim=(.67,.87))
axes[2].set_xticks([0,3,5]);axes[2].set_title('(c) Simpson',loc='center',pad=10)
for ax in axes:clean(ax)
save(fig,'fig1_motivation')

# Figure 2: reference data persist; geometry changes with the native student.
fig=plt.figure(figsize=(6.65,2.92));ax=fig.add_axes([.005,.005,.99,.99]);ax.set(xlim=(0,100),ylim=(0,100));ax.axis('off')
def box(x,y,w,h,txt,fill='white',lw=.8,fs=8):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.45,rounding_size=1.2',
        fc=fill,ec='.2',lw=lw));ax.text(x+w/2,y+h/2,txt,ha='center',va='center',fontsize=fs)
def arrow(a,b,style='-',lw=.85):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=8,
        color='.2',lw=lw,linestyle=style,connectionstyle='arc3'))
ax.text(1,97,'SPECTRUM inside Looped Self-Distillation',fontsize=10,weight='bold',va='top')
box(2,68,22,17,'Fixed reference anchor\n'+r'$\mathcal{A}=\{(x_i,y_i^\star)\}$',fill='.95')
box(31,68,29,17,'Re-estimate K/V geometry\n'+r'$\bar C_t=C_t/\lambda_{\max}(C_t)$')
box(69,65,28,23,'Proximal spectral gain\n'+r'$T_t=[I+\tau(I-\bar C_t)]^{-1}$',fill='.94',lw=1.2)
arrow((24.5,76.5),(30.5,76.5));arrow((60.5,76.5),(68.5,76.5))
ax.text(13,63,'same examples every round',ha='center',fontsize=6.8,color='.35')
box(2,32,19,18,'Current student\n'+r'$\theta_t$')
box(29,32,28,18,'Temporary K/V folding\nGenerate all raw samples',fill='.94')
box(68,32,29,18,'Restore native weights\nSingle-LoRA SFT '+r'$\to\theta_{t+1}$')
arrow((21.5,41),(28.5,41));arrow((57.5,41),(67.5,41))
ax.text(62.5,45,r'$\mathcal{D}_t$',ha='center',fontsize=8)
arrow((82,64.5),(46,50.5));arrow((14,50.5),(38,67.5),'--')
ax.text(35,55,'reference loss on '+r'$\theta_t$',ha='center',fontsize=6.8)
ax.plot([82.5,82.5,11.5],[31.5,17,17],color='.18',lw=1)
arrow((11.5,17),(11.5,31.5),lw=1)
ax.text(45,19,'Next round: updated student, same reference anchor',ha='center',fontsize=7.4)
ax.text(50,5,'All completions enter SFT  |  No rollout scoring or filtering  |  Native final inference',
        ha='center',va='center',fontsize=7.2)
save(fig,'fig2_framework')

# Figure 3: all budget points use the same final 64-sample pools.
fig=plt.figure(figsize=(6.65,2.50))
axes=[fig.add_axes(rect) for rect in ([.067,.26,.445,.59],[.618,.26,.157,.59],[.865,.26,.13,.59])]
ks=[1,4,8,16,64];bs=[4,8,16]
for m in ['base','plain','spectral_soft']:
    row=D['mbpp64'][m]
    axes[0].plot(ks,[row['implementation_coverage_at_k'][str(k)]['mean'] for k in ks],ms=3.3,label=LABEL[m],**STYLE[m])
    axes[1].plot(ks,[100*row['pass_at_k'][str(k)]['mean'] for k in ks],ms=2.7,**STYLE[m])
for ax in axes[:2]:
    ax.set_xscale('log',base=2);ax.set_xticks([1,4,16,64],[1,4,16,64]);ax.set_xlabel('Total draws $k$')
axes[0].set(ylabel='Correct AST richness',ylim=(0,14));axes[0].set_title('(a) Broader correct-solution sampling',loc='left',pad=10)
axes[0].legend(frameon=False,loc='upper left')
axes[1].set(ylabel='Pass@k (%)',ylim=(34,76));axes[1].set_title('(b) Task success',loc='center',pad=10)
contrasts=D['mbpp64_comparisons']['spectral_soft_minus_plain']['correct_matched_coverage_at_budgets']
y=np.array([contrasts[str(b)]['mean'] for b in bs]);ci=np.array([contrasts[str(b)]['ci95'] for b in bs])
axes[2].errorbar(range(3),y,yerr=np.stack([y-ci[:,0],ci[:,1]-y]),fmt='ko-',ms=3,capsize=2,elinewidth=.8)
axes[2].axhline(0,color='.6',ls=':',lw=.6);axes[2].set_xticks(range(3),bs)
axes[2].set(xlabel='Correct draws $b$',ylabel=r'Paired $\Delta D_b$',ylim=(-.1,2.3),xlim=(-.25,2.25))
axes[2].set_title('(c) Matched',loc='center',pad=10)
for ax in axes:clean(ax)
save(fig,'fig3_budget')

# Figure 4 (appendix): both signs, one deterministic case-selection rule.
fig=plt.figure(figsize=(6.65,2.33))
ax1=fig.add_axes([.077,.24,.46,.60]);ax2=fig.add_axes([.65,.24,.34,.60])
for ax,word,title in [(ax1,'broader','(a) HumanEval/3: one additional structure'),
                      (ax2,'narrower','(b) HumanEval/2: a counterexample')]:
    case=A['equal_correct_count_examples']['HumanEval+ / '+word]
    p=sorted(case['Plain']['counts'].values(),reverse=True)
    s=sorted(case['SPECTRUM']['counts'].values(),reverse=True)
    n=max(len(p),len(s));x=np.arange(n)
    ax.bar(x-.18,p+[0]*(n-len(p)),width=.36,color='.72',edgecolor='.3',lw=.5,label='Plain')
    ax.bar(x+.18,s+[0]*(n-len(s)),width=.36,color='.12',edgecolor='.12',lw=.5,label='SPECTRUM')
    ax.set_title(title,loc='left',pad=10);ax.set(xlabel='Within-model AST frequency rank',ylabel='Correct sample count')
    ax.set_xticks(x[::max(1,n//4)],1+x[::max(1,n//4)])
    ax.text(.98,.96,f"Both: {case['correct_count']}/16 correct",transform=ax.transAxes,ha='right',va='top',fontsize=7)
    ax.set_ylim(0,18 if word=='broader' else 2.8);clean(ax)
ax1.legend(frameon=False,loc='center right')
save(fig,'fig4_examples')
print('Wrote four measured/vector figures as PDF and PNG.')
