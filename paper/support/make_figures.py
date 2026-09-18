"""Reproduce the paper's measured pilot and explicitly analytic vector figures.

No empirical observations are synthesized. Figure 1 values are transcribed from
the immutable pilot README identified in figures/figures_manifest_captions.md.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8,
    "axes.titlesize": 9, "axes.labelsize": 8,
    "xtick.labelsize": 7.5, "ytick.labelsize": 8,
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#AAB2BB", "axes.linewidth": .65,
    "text.color": "#243342", "axes.labelcolor": "#243342",
    "xtick.color": "#526170", "ytick.color": "#243342",
    "savefig.facecolor": "white",
})
INK = "#243342"
MUTED = "#657786"
TEAL = "#007F7B"
COLORS = ["#7B8794", "#354F72", "#AD7138", TEAL]
MARKERS = ["o", "s", "^", "D"]
METHODS = ["Plain", "SSD", "SPD-hard", "SPECTRUM"]

def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf", bbox_inches=None)
    fig.savefig(OUT / f"{name}.png", dpi=240, bbox_inches=None)
    plt.close(fig)

def observation():
    fig = plt.figure(figsize=(7, 2.25))
    gs = fig.add_gridspec(1, 2, width_ratios=[.40, .60], left=.16, right=.975,
                          top=.70, bottom=.245, wspace=.34)
    ax1, ax2 = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    vals = [[36.82, 36.89, 36.87, 36.65], [3.393, 3.391, 3.409, 3.422]]
    for ax, vv, lim, ticks, decimals in [
        (ax1, vals[0], (35.5, 38.0), [35.5, 36, 36.5, 37, 37.5, 38], 2),
        (ax2, vals[1], (3.35, 3.46), [3.35, 3.375, 3.4, 3.425, 3.45], 3),
    ]:
        ax.set_xlim(*lim)
        ax.set_ylim(3.48, -.48)
        ax.set_xticks(ticks)
        ax.grid(axis="x", color="#E8ECF0", linewidth=.65)
        for j, (value, color, marker) in enumerate(zip(vv, COLORS, MARKERS)):
            ax.scatter(value, j, s=33 if j == 3 else 28, color=color,
                       marker=marker, zorder=3, edgecolor="white", linewidth=.4)
            ax.annotate(f"{value:.{decimals}f}", (value, j), xytext=(7, 0),
                        textcoords="offset points", va="center", fontsize=7.6,
                        color=color, weight="bold" if j == 3 else "normal")
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.set_yticks(range(4))
    ax1.set_yticklabels(METHODS)
    ax1.get_yticklabels()[-1].set_color(TEAL)
    ax1.get_yticklabels()[-1].set_weight("bold")
    ax2.set_yticklabels([])
    ax1.set_title("(a) Single-draw correctness", loc="left", pad=9, weight="bold")
    ax2.set_title("(b) Correct-code diversity", loc="left", pad=9, weight="bold")
    ax1.set_xlabel("pass@1 (%)  ↑", labelpad=4)
    ax2.set_xlabel(r"Expected AST coverage, $D_4^{\mathrm{AST}}$  ↑", labelpad=4)
    ax2.set_xticklabels(["3.350", "3.375", "3.400", "3.425", "3.450"])
    fig.text(.16, .98, "Correctness and correct-code diversity have different leaders",
             fontsize=10, weight="bold", va="top")
    fig.text(.16, .89, "SSD has the highest pass@1; SPECTRUM has the highest AST coverage.",
             fontsize=7.7, color=MUTED, va="top")
    fig.text(.16, .027, "Exploratory pilot · one cycle · seed 42 · 64 MBPP tasks × 64 samples per task",
             fontsize=7, color=MUTED)
    save(fig, "fig1_observation")

def rounded(ax, x, y, w, h, title, body, face="#F5F7F9", edge="#C9D2DA", title_color=INK,
            title_size=7.8, body_size=7.0):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.04,rounding_size=0.10",
                               facecolor=face,edgecolor=edge,linewidth=.85))
    ax.text(x+w/2, y+h-.26, title, ha="center", va="center", fontsize=title_size,
            weight="bold",color=title_color)
    ax.text(x+w/2, y+.34*h, body, ha="center", va="center", fontsize=body_size,
            linespacing=1.5,color=INK)

def arrow(ax, start, end, color=MUTED, style="-", lw=.9, rad=0):
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle="-|>",mutation_scale=8,
                               color=color,linewidth=lw,linestyle=style,
                               connectionstyle=f"arc3,rad={rad}",shrinkA=1.5,shrinkB=2))

def line_arrow(ax, points, color=MUTED, style="-", lw=.9):
    xs, ys = zip(*points[:-1])
    ax.plot(xs,ys,color=color,ls=style,lw=lw,solid_capstyle="round")
    arrow(ax,points[-2],points[-1],color,style,lw)

def method():
    fig, ax = plt.subplots(figsize=(7, 2.72))
    fig.subplots_adjust(left=.012,right=.988,bottom=.025,top=.99)
    ax.set_xlim(0,14); ax.set_ylim(0,5.44); ax.axis("off")
    ax.text(.12,5.18,"SPECTRUM: spectral control during data generation, then native learning",
            fontsize=9.5,weight="bold",va="center")
    ax.text(.12,4.79,"GENERATION / CALIBRATION",fontsize=6.8,weight="bold",color=MUTED)
    rounded(ax,.30,3.24,1.30,1.08,"Native",r"$\theta_t$",body_size=11)
    rounded(ax,1.99,3.13,3.12,1.35,"Reference calibration",
            "Native K/V output gradients\n"+r"$C = \frac{1}{M}\sum_{i,u} g_{iu} g_{iu}^{\top}$",body_size=7.0)
    rounded(ax,5.55,2.96,3.75,1.65,"Soft spectral transform",
            r"$\bar C = C / \lambda_{\max}(C)$"+"\n"+
            r"$T=[I+\tau(I-\bar C)]^{-1}$"+"\n"+r"$\tau=1$",
            face="#E7F3F1",edge=TEAL,title_color=TEAL,body_size=8)
    rounded(ax,9.75,3.13,3.83,1.35,"Temporarily fold; generate",
            r"$W'=T^{\top}W,\quad b'=T^{\top}b$"+"\n1 raw completion / training prompt",body_size=7.0)
    arrow(ax,(1.62,3.8),(1.96,3.8))
    arrow(ax,(5.13,3.8),(5.51,3.8),TEAL)
    arrow(ax,(9.32,3.8),(9.72,3.8),TEAL)
    ax.text(3.55,2.73,"Completion-masked reference CE;\nall nonpadding token positions in C",
            fontsize=6.65,ha="center",va="center",color=MUTED,linespacing=1.3)
    # The saved native state, not the transformed generator, initializes LoRA.
    rounded(ax,1.18,1.00,2.2,1.08,"Restore native",r"$\theta_t$ before LoRA",body_size=7.4)
    rounded(ax,4.12,1.00,3.1,1.08,"Ordinary LoRA","All raw outputs; all-token loss",body_size=7.1)
    rounded(ax,7.95,1.00,2.43,1.08,"Merge updates",r"Native $\theta_{t+1}$",body_size=8)
    rounded(ax,11.12,1.00,2.52,1.08,"Native evaluation","No spectral transform",face="white",body_size=7.0)
    line_arrow(ax,[(.95,3.2),(.95,1.54),(1.15,1.54)])
    ax.text(.99,2.37,"saved\nstate",fontsize=6.5,ha="center",color=MUTED)
    arrow(ax,(3.4,1.54),(4.08,1.54))
    arrow(ax,(7.24,1.54),(7.92,1.54))
    arrow(ax,(10.40,1.54),(11.08,1.54),style="--")
    line_arrow(ax,[(11.65,3.1),(11.65,2.39),(5.68,2.39),(5.68,2.11)],TEAL)
    ax.text(8.72,2.49,"raw completions",fontsize=6.8,ha="center",color=TEAL)
    # Recurrence updates the precise native checkpoint used in calibration.
    line_arrow(ax,[(9.16,.97),(9.16,.47),(.30,.47),(.16,.47),(.16,3.78),(.27,3.78)],
               color="#84929F",lw=.85)
    ax.text(4.78,.14,"Next round: recompute C and T from the merged native checkpoint",
            fontsize=6.8,ha="center",color=MUTED)
    ax.text(10.75,.54,"TRAINING",fontsize=6.5,weight="bold",color=MUTED,ha="right")
    ax.text(12.34,.54,"EVALUATION",fontsize=6.5,weight="bold",color=MUTED,ha="center")
    save(fig,"fig2_method")

def gain():
    fig, ax = plt.subplots(figsize=(7,2.2))
    fig.subplots_adjust(left=.095,right=.665,bottom=.235,top=.77)
    lam=np.linspace(0,1,501)
    ax.plot(lam,np.ones_like(lam),"--",color="#87929D",lw=1.15,label="Identity")
    for tau,color,ls,lw in [(.5,"#6B84A8",":",1.8),(1,TEAL,"-",2),(2,"#AD7138","-.",1.45)]:
        val=1/(1+tau*(1-lam))
        ax.plot(lam,val,color=color,ls=ls,lw=lw,label=rf"$\tau={tau:g}$")
    ax.set_xlim(0,1);ax.set_ylim(0,1.045)
    ax.set_xticks([0,.25,.5,.75,1]);ax.set_yticks([0,.25,.5,.75,1])
    ax.grid(color="#E8ECF0",linewidth=.65)
    ax.set_xlabel(r"Normalized second-moment eigenvalue $\mu$",labelpad=4)
    ax.set_ylabel(r"Directional gain $s_\tau(\mu)$",labelpad=5)
    fig.text(.095,.95,"Analytic soft gain preserves every direction",fontsize=10,weight="bold",va="top")
    fig.text(.095,.84,"Larger second-moment eigenvalues receive larger gain; no direction is zeroed.",fontsize=7.7,color=MUTED,va="top")
    ax.legend(loc="lower right",fontsize=7,frameon=False,ncol=2,columnspacing=1.25,handlelength=2.4)
    fig.text(.72,.74,r"$s_\tau(\mu)=\frac{1}{1+\tau(1-\mu)}$",fontsize=11,color=INK,va="top")
    fig.text(.72,.59,r"$\mu=\lambda/\lambda_{\max}$",fontsize=8.4,color=MUTED,va="top")
    fig.text(.72,.48,"Default: τ = 1",fontsize=8.4,color=TEAL,weight="bold",va="top")
    fig.text(.72,.375,"Gain range: [½, 1]\nFull-rank transform\nAnalytic illustration",fontsize=7.9,linespacing=1.65,color=MUTED,va="top")
    fig.text(.095,.027,"Native K/V gradient second moment; curves are not measured model spectra.",fontsize=7,color=MUTED)
    save(fig,"fig3_gain")

if __name__ == "__main__":
    observation();method();gain()
    print("Created fig1_observation, fig2_method, fig3_gain (PDF + PNG).")
