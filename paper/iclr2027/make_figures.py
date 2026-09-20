#!/usr/bin/env python3
"""Rebuild publication figures from committed aggregate results; no model runs.

All uncertainty is read verbatim from the reports. No new resampling, fitted
curves, or empirical implementation histograms are constructed here.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = ROOT / 'results/retention_5round_train16_eval16_seed43'
OUT = HERE / 'figures'
OUT.mkdir(exist_ok=True)
# The Overleaf archive includes lossless field selections of the measured
# aggregates, so the figures can be rebuilt without cloning the repository.
report_path = RESULTS / 'report.json'
final_path = RESULTS / 'eval64/metrics_compact.json'
if not (report_path.is_file() and final_path.is_file()):
    report_path = HERE / 'source-data/report.compact.json'
    final_path = HERE / 'source-data/eval64.compact.json'
report = json.loads(report_path.read_text())
final = json.loads(final_path.read_text())
stages = {s['id']: s['metrics'] for s in report['stages']
          if s['stage'] == 'evaluation' and s['metrics'] is not None}
comparisons = {(c['candidate'], c['reference']): c['result']
               for c in report['comparisons'] if c['status'] == 'available'}
COLORS = {'base': '#687382', 'plain': '#A35E3C', 'spectral_soft': '#147C80'}
LABELS = {'base': 'Initial model', 'plain': 'Plain', 'spectral_soft': 'SPECTRUM'}
MARKERS = {'base': 'D', 'plain': 's', 'spectral_soft': 'o'}
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8,
 'axes.labelsize': 8, 'axes.titlesize': 8.5, 'xtick.labelsize': 7,
 'ytick.labelsize': 7, 'legend.fontsize': 7.2, 'axes.linewidth': .6,
 'lines.linewidth': 1.7, 'pdf.fonttype': 42, 'ps.fonttype': 42,
 'figure.facecolor': 'white', 'axes.spines.top': False,
 'axes.spines.right': False, 'savefig.facecolor': 'white'})

def clean(ax):
    ax.grid(axis='y', color='#E5E8EC', linewidth=.55, zorder=0)
    ax.tick_params(length=2.5, width=.6)
    ax.set_axisbelow(True)

def save(fig, name):
    fig.savefig(OUT / f'{name}.pdf')
    fig.savefig(OUT / f'{name}.png', dpi=220)
    plt.close(fig)

def round_metric(method, name, budget=None):
    rows = [stages['base/evaluation']]
    rows += [stages[f'{method}/round_{r}/evaluation'] for r in range(1, 6)]
    vals = [row[name] if budget is None else row[name][str(budget)] for row in rows]
    return np.array([v['mean'] for v in vals]), np.array([v['ci95'] for v in vals])

# Figure 1: measured two-objective evolution and a explicitly analytic example.
fig = plt.figure(figsize=(6.7, 2.22))
ax = fig.add_axes([.085, .23, .53, .63])
for method in ['plain', 'spectral_soft']:
    x, _ = round_metric(method, 'pass_at_1')
    y, _ = round_metric(method, 'implementation_coverage_at_k', 16)
    ax.plot(100*x, y, marker=MARKERS[method], ms=3.4,
            color=COLORS[method], label=LABELS[method])
    for r in range(1, 6):
        dx, dy = (3, -10) if method == 'plain' else (2, 6)
        ax.annotate(str(r), (100*x[r], y[r]), xytext=(dx,dy),
                    textcoords='offset points', fontsize=6.5, color=COLORS[method])
    ax.annotate('', xy=(100*x[-1],y[-1]), xytext=(100*x[-2],y[-2]),
                arrowprops=dict(arrowstyle='->', color=COLORS[method], lw=1.4))
ax.scatter(37.925, 4.016, color=COLORS['base'], marker='D', s=24, zorder=5)
ax.annotate('Initial', (37.925,4.016), xytext=(5,4), textcoords='offset points',
            color=COLORS['base'], fontsize=7)
ax.set_xlim(37.4,41.8); ax.set_ylim(2.98,4.14)
ax.set_xlabel('pass@1 (%)  ↑', labelpad=3)
ax.set_ylabel('Correct AST richness@16  ↑', labelpad=5)
ax.set_title('(a) Correctness rises; implementation breadth contracts', loc='left', pad=8)
clean(ax)
ax.legend(loc='lower left', frameon=False, fontsize=7)
ax2 = fig.add_axes([.73,.30,.245,.52])
qA = np.array([.25]*4); qB=np.array([1.,0,0,0]); x=np.arange(4)
ax2.bar(x-.16,qA,width=.29,color='#BEDDDB',edgecolor=COLORS['spectral_soft'],lw=.5,label='Broad')
ax2.bar(x+.16,qB,width=.29,color='#C9B7AA',edgecolor=COLORS['plain'],lw=.5,label='Concentrated')
ax2.set_ylim(0,1.12);ax2.set_xticks(x, ['A','B','C','D']);ax2.set_yticks([0,.5,1])
ax2.set_ylabel('Conditional probability', fontsize=7, labelpad=3)
ax2.set_xlabel('Correct implementation class', fontsize=7, labelpad=2)
ax2.set_title('(b) Equal correctness, different breadth',fontsize=6.7,pad=10)
ax2.text(.5, .95, 'Analytic example',transform=ax2.transAxes,ha='center',fontsize=6.5)
ax2.legend(frameon=False,loc='upper right',bbox_to_anchor=(1.02,.90),fontsize=5.8,handlelength=.8,labelspacing=.15)
clean(ax2)
fig.text(.853,.067,'Both: pass@1 = 40%\nCorrect-conditioned richness@4: 2.734 vs 1',ha='center',fontsize=6.4)
fig.text(.085,.025,'(a) MBPP, 500 tasks, 16 samples/task; labels denote rounds. (b) Illustrative distributions, not measured outputs.',fontsize=6.25,color='#505761')
save(fig,'fig1_motivation')

# Figure 2: general loop, then concrete SPECTRUM operator and native student.
fig = plt.figure(figsize=(6.7,2.60)); ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
def box(x,y,w,h,text,face='#F2F4F6',edge='#9CA8B3',fs=8,bold=False):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.004,rounding_size=0.008',
                 fc=face,ec=edge,lw=.75))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=fs,
            weight='bold' if bold else 'normal',linespacing=1.4)
def arrow(p,q,style='-',color='#596673',connection='arc3',lw=.85):
    ax.add_patch(FancyArrowPatch(p,q,arrowstyle='-|>',mutation_scale=8,lw=lw,
                 color=color,linestyle=style,connectionstyle=connection))
ax.text(.025,.955,'Looped Self-Distillation',fontsize=10,weight='bold',va='top')
ax.text(.975,.95,'Re-estimate the generator from each new student',fontsize=7.5,ha='right',va='top',color='#53606B')
box(.025,.68,.125,.18,'Student\n'+r'$\theta_t$')
box(.197,.68,.165,.18,'Generation operator\n'+r'$\mathcal{A}_t = \mathcal{A}(\theta_t)$',face='#DBEFEB',edge=COLORS['spectral_soft'])
box(.409,.68,.153,.18,'Generate\n'+r'$\mathcal{D}_t$',fs=8)
box(.609,.68,.171,.18,'Learn from '+r'$\mathcal{D}_t$'+'\none LoRA',fs=8)
box(.833,.68,.14,.18,'Next student\n'+r'$\theta_{t+1}$')
for p,q in [((.151,.77),(.195,.77)),((.364,.77),(.408,.77)),((.564,.77),(.608,.77)),((.782,.77),(.831,.77))]:arrow(p,q)
# Recurrent return has one unambiguous destination: the next operator estimate.
ax.plot([.905,.905,.280,.280],[.68,.565,.565,.68],color='#596673',lw=.9)
arrow((.280,.62),(.280,.679))
ax.text(.59,.575,'recalibrate next round',fontsize=7,ha='center',va='bottom',backgroundcolor='white')
ax.text(.485,.64,'16 raw samples / prompt',fontsize=6.8,ha='center')
ax.text(.695,.64,'restore '+r'$\theta_t$'+' before SFT',fontsize=6.8,ha='center')
ax.text(.925,.48,'Native\ninference',fontsize=7.5,ha='center',va='center')
arrow((.949,.68),(.949,.535),style='--')
ax.axhline(.435,xmin=.025,xmax=.975,color='#CCD5DC',lw=.7)
ax.text(.025,.393,'SPECTRUM instantiation',fontsize=9,weight='bold',color=COLORS['spectral_soft'])
box(.025,.125,.182,.195,'Reference loss\n'+r'$g=\nabla_h\ell_{\mathrm{ref}}$',fs=8)
box(.242,.125,.190,.195,'Loss-sensitive geometry\n'+r'$\bar C \propto \mathbb{E}[gg^\top]$',fs=8)
box(.467,.125,.235,.195,'Proximal spectral modulation\n'+r'$T=[I+\tau(I-\bar C)]^{-1}$',face='#DBEFEB',edge=COLORS['spectral_soft'],fs=7.2)
for p,q in [((.209,.222),(.240,.222)),((.434,.222),(.465,.222))]:arrow(p,q,color=COLORS['spectral_soft'])
ax.text(.467,.058,'Fold '+r'$T$'+' into K/V weights for generation; restore before student learning.',fontsize=7,ha='center')
# Analytic gain plot, no empirical spectrum or selected numerical strength.
gainax=fig.add_axes([.76,.105,.21,.23]);u=np.linspace(0,1,100)
gainax.plot(u,1/(1+(1-u)),color=COLORS['spectral_soft'],lw=1.8)
gainax.axhline(1,color='#ADB8C0',ls=':',lw=.6)
gainax.set_xlim(0,1);gainax.set_ylim(.38,1.05);gainax.set_xticks([0,1]);gainax.set_yticks([.5,1],[r'$\frac{1}{1+\tau}$','1'])
gainax.set_xlabel('Normalized sensitivity',fontsize=6.3,labelpad=1)
gainax.set_title('Continuous, positive gain',fontsize=7,pad=4)
gainax.tick_params(labelsize=6,length=2);gainax.spines[['top','right']].set_visible(False)
save(fig,'fig2_framework')

# Figure 3: exact final64 budget points with task-bootstrap uncertainty.
fig=plt.figure(figsize=(6.7,2.20)); a=fig.add_axes([.08,.22,.53,.64]); b=fig.add_axes([.72,.22,.255,.64])
ks=np.array([1,4,8,16,64])
for method in ['base','plain','spectral_soft']:
    for ax,field,scale in [(a,'implementation_coverage_at_k',1),(b,'pass_at_k',100)]:
        d=final[method][field];y=np.array([d[str(k)]['mean'] for k in ks])*scale
        ci=np.array([d[str(k)]['ci95'] for k in ks])*scale
        ax.fill_between(ks,ci[:,0],ci[:,1],color=COLORS[method],alpha=.085,lw=0)
        ax.plot(ks,y,color=COLORS[method],marker=MARKERS[method],ms=3.5,label=LABELS[method],
                ls='--' if method=='base' else '-')
        if ax is a:ax.annotate(f'{y[-1]:.2f}',(64,y[-1]),xytext=(4,0),textcoords='offset points',color=COLORS[method],fontsize=7,va='center')
for ax in [a,b]:
    ax.set_xscale('log',base=2);ax.set_xticks(ks,[str(k) for k in ks]);ax.set_xlabel('Sampling budget k',labelpad=3);clean(ax)
a.set_xlim(.88,91);a.set_ylim(0,14.6);a.set_ylabel('Correct AST richness@k  ↑',labelpad=4)
a.set_title('(a) More samples expose more retained implementations',loc='left',pad=8)
b.set_xlim(.86,78);b.set_ylim(30,79);b.set_ylabel('pass@k (%)  ↑',labelpad=3);b.set_title('(b) Success probability',loc='left',pad=8)
a.legend(frameon=False,loc='upper left',fontsize=7)
fig.text(.08,.02,'500 MBPP tasks; final students; 64 samples/task. Shading: reported pointwise 95% task-bootstrap CIs (2,000 resamples).',fontsize=6.3,color='#505761')
save(fig,'fig3_budget')

# Figure 4: only genuinely available paired comparisons are plotted.
fig=plt.figure(figsize=(6.7,2.25));a=fig.add_axes([.115,.24,.495,.62]);b=fig.add_axes([.735,.25,.24,.61])
rs=np.arange(1,6)
for method,offset in [('plain',-.065),('spectral_soft',.065)]:
    data=[comparisons[(f'{method}/round_{r}/evaluation','base/evaluation')]['implementation_proxy']['correct_matched_coverage'] for r in rs]
    y=np.array([v['mean'] for v in data]); ci=np.array([v['ci95'] for v in data])
    a.errorbar(rs+offset,y,yerr=np.array([y-ci[:,0],ci[:,1]-y]),fmt=MARKERS[method]+'-',
                color=COLORS[method],ms=3.7,capsize=2,lw=1.4,elinewidth=.9,label=LABELS[method])
    cy,cci=round_metric(method,'implementation_coverage_at_k',16)
    b.fill_between(np.arange(6),cci[:,0],cci[:,1],color=COLORS[method],alpha=.10,lw=0)
    b.plot(np.arange(6),cy,color=COLORS[method],marker=MARKERS[method],ms=3.1)
a.axhline(0,color='#7F8C99',lw=.8,ls=':');a.set_xlim(.7,5.3);a.set_ylim(-.70,.10);a.set_xticks(rs);a.set_xlabel('Learning round',labelpad=1)
a.set_ylabel('Change in correct-conditioned\nAST richness@4',labelpad=4,fontsize=7.5)
a.set_title('(a) Paired change from the initial model',loc='left',pad=8);a.legend(frameon=False,loc='lower left',fontsize=7)
b.set_xticks([0,1,2,3,4,5]);b.set_xlim(-.15,5.15);b.set_ylim(2.65,4.47);b.set_xlabel('Learning round',labelpad=2)
b.set_ylabel('Correct AST richness@16',labelpad=3);b.set_title('(b) All 500 tasks',loc='left',pad=8)
for ax in [a,b]:clean(ax)
fig.text(.115,.025,'16 samples/task. (a) Paired eligible tasks vs initial, n = 236–246. (b) Full cohort. 95% task-bootstrap CIs.',fontsize=6.25,color='#505761')
save(fig,'fig4_retention')

# Machine-readable provenance for all plotted values. The analytic examples
# are explicitly separate from measured data and are reproducible.
ledger={'sources':['results/retention_5round_train16_eval16_seed43/report.json',
                   'results/retention_5round_train16_eval16_seed43/eval64/metrics_compact.json'],
 'uncertainty':'Reported pointwise 95% task-bootstrap confidence intervals, 2000 resamples; one training seed.',
 'figure1_analytic':{'status':'ILLUSTRATIVE','a':.4,'q_broad':[.25]*4,'q_concentrated':[1,0,0,0],
                    'D4_broad':4*(1-.75**4),'D4_concentrated':1},
 'figure2_gain':{'status':'ANALYTIC ILLUSTRATION','formula':'1/(1+tau*(1-mu))','tau_for_drawn_shape':1,
                'note':'Shape illustrative; ticks use symbolic tau and do not select an experimental strength.'},
 'eval16':{},'eval64':{},'paired_vs_initial':{}}
def compact(obj):
    return {k:obj[k] for k in ['mean','ci95','eligible_tasks','total_tasks'] if k in obj}
for id,m in stages.items():
    if id.split('/')[0] not in ['base','plain','spectral_soft']:continue
    ledger['eval16'][id]={'pass_at_1':compact(m['pass_at_1']),
       'C16':compact(m['implementation_coverage_at_k']['16']),
       'D4':compact(m['implementation_correct_matched_coverage'])}
for method in ['base','plain','spectral_soft']:
    ledger['eval64'][method]={f:{k:compact(v) for k,v in final[method][f].items()}
                            for f in ['pass_at_k','implementation_coverage_at_k']}
for method in ['plain','spectral_soft']:
    for r in range(1,6):
        v=comparisons[(f'{method}/round_{r}/evaluation','base/evaluation')]['implementation_proxy']['correct_matched_coverage']
        ledger['paired_vs_initial'][f'{method}/round_{r}']=compact(v)
(OUT/'figure_data.json').write_text(json.dumps(ledger,indent=2)+'\n')
print('Wrote four PDF/PNG figures and figures/figure_data.json')
