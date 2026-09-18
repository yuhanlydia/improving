"""SPECTRUM paper figures.

Every number in this file is transcribed from
results/retention_5round_train16_eval16_seed43/ (16-sample tier: metrics.csv,
report.json; 64-sample tier: eval64/metrics_compact.json,
eval64/comparisons_compact.json) and, for the pilot panel, from
results/pilot_seed42_codecentric/README.md.

Tier labels are load-bearing: the 16-sample tier is the only tier with
per-round measurements; the 64-sample (eval64) tier holds base and the three
round-5 checkpoints only. Figures never mix the two without labelling.

Palette validated with the dataviz skill validator:
  node scripts/validate_palette.js "#2a78d6,#eb6834,#1baf7a" --pairs all
  -> ALL CHECKS PASS (worst all-pairs CVD dE 9.2, normal-vision 24.0)
Aqua sits at 2.82:1 on white, so every series carries a direct text label and
colour is never the only identity channel.
"""

from __future__ import annotations

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

# ---------------------------------------------------------------- palette ----
SPECTRUM = "#2a78d6"   # slot 1 - the proposed method
SPD = "#eb6834"        # slot 2 - hard-projection comparator
SSD = "#1baf7a"        # slot 3 - pilot-only comparator (appendix)
PLAIN = "#898781"      # neutral - plain self-distillation
BASE_INK = "#52514e"   # neutral - the undistilled reference level
INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SURFACE = "#ffffff"

MARKERS = {"spectral_soft": "D", "spd_hard": "^", "plain": "o", "ssd": "s"}
COLORS = {"spectral_soft": SPECTRUM, "spd_hard": SPD, "plain": PLAIN, "ssd": SSD}
LABELS = {
    "spectral_soft": "SPECTRUM",
    "spd_hard": "SPD-hard",
    "plain": "plain",
    "ssd": "SSD",
}

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans"],
        "font.size": 8,
        "axes.titlesize": 8.5,
        "axes.labelsize": 8,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 7.5,
        "legend.fontsize": 7.5,
        "axes.edgecolor": AXIS,
        "axes.linewidth": 0.6,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

ROOT = pathlib.Path(__file__).resolve().parent
FIGDIR = ROOT / "figures"
FIGDIR.mkdir(exist_ok=True)

# ------------------------------------------------------------------ data -----
# 16-sample tier, per-round. cm@4 = correct-matched AST coverage at 4 correct draws.
ROUNDS = [1, 2, 3, 4, 5]
CM4_BASE = 3.310434709480511
CM4 = {
    "plain": [3.173048067300941, 3.0800160393097196, 2.8954791209655024,
              2.803304432193321, 2.746691347624183],
    "spd_hard": [3.14389616004402, 3.0590361365642265, 2.888999737241925,
                 2.774081202840601, 2.689757274108419],
    "spectral_soft": [3.221975831745947, 3.159304273589988, 3.0633024736078176,
                      2.991413656052439, 2.9971258357189914],
}
# 16-sample tier, round-5 pass@1 (fraction) with 95% task-bootstrap CI.
P1_R5 = {
    "base": (0.37925, 0.346871875, 0.414003125),
    "plain": (0.413, 0.379375, 0.44975625),
    "spd_hard": (0.4135, 0.379371875, 0.451378125),
    "spectral_soft": (0.40175, 0.368490625, 0.43750625),
}
# 16-sample tier, paired cm@4 difference vs spd_hard and vs base, per round.
CM4_DELTA_SPD = [
    (0.06621751581751582, 0.0348426, 0.0970828),
    (0.12715416691794645, 0.0864609, 0.168198),
    (0.1622940903182839, 0.121548, 0.202213),
    (0.2294052444654854, 0.181879, 0.274728),
    (0.2929389999111115, 0.23322470344098753, 0.3531874808062307),
]
CM4_DELTA_BASE = [
    (-0.09968, -0.16601, -0.03544),
    (-0.13999, -0.21132, -0.06973),
    (-0.22102, -0.30476, -0.14572),
    (-0.31630, -0.39198, -0.24395),
    (-0.31530, -0.39445073313153484, -0.2395721128340615),
]
# Paired D4 difference against the undistilled base for EVERY arm, per-round
# tier.  Panel (b) of Figure 5 needs the comparator arms on the same footing as
# SPECTRUM, and the pairing convention must match panel (a): these are paired
# task-bootstrap differences (report.json -> comparisons[*] ->
# implementation_proxy.correct_matched_coverage_at_budgets["4"]), NOT the
# difference of the two arms' mean levels (which is what CM4[arm] - CM4_BASE
# would give, and which is a different and slightly smaller number).
CM4_DELTA_BASE_ALL = {
    "plain": [
        (-0.13830, -0.20800, -0.06800),
        (-0.22020, -0.29350, -0.14520),
        (-0.37610, -0.45270, -0.29870),
        (-0.50030, -0.57360, -0.42960),
        (-0.57420, -0.65370, -0.49870),
    ],
    "spd_hard": [
        (-0.16480, -0.23300, -0.09620),
        (-0.23970, -0.31360, -0.16610),
        (-0.39340, -0.47030, -0.31530),
        (-0.53570, -0.61360, -0.45690),
        (-0.62560, -0.70900, -0.54440),
    ],
    "spectral_soft": [
        (-0.09970, -0.16600, -0.03540),
        (-0.14000, -0.21130, -0.06970),
        (-0.22100, -0.30480, -0.14570),
        (-0.31630, -0.39200, -0.24390),
        (-0.31530, -0.39450, -0.23960),
    ],
}
# eval64 tier (500 tasks x 64 samples), SPECTRUM minus reference.
# (endpoint, unit, point, lo, hi, n_paired)
EVAL64 = {
    "base": {
        "cm@4": (-0.21621423592999497, -0.26338146288134634, -0.1712302020285684, 311),
        "cov@64": (-1.292, -1.78605, -0.78, 500),
        "pass@1": (0.023875, 0.01578046875, 0.032221875, 500),
        "pass@64": (0.006, -0.018, 0.03, 500),
    },
    "plain": {
        "cm@4": (0.29542497837164544, 0.2488768199584551, 0.34316922020628526, 316),
        "cov@64": (3.004, 2.568, 3.4941, 500),
        "pass@1": (-0.01115625, -0.01609453125, -0.00628125, 500),
        "pass@64": (0.022, 0.004, 0.042, 500),
    },
    "spd_hard": {
        "cm@4": (0.3343973321781965, 0.28955470590964033, 0.3787110897843099, 318),
        "cov@64": (3.122, 2.68595, 3.59605, 500),
        "pass@1": (-0.01434375, -0.01887578125, -0.00978046875, 500),
        "pass@64": (0.024, 0.006, 0.044, 500),
    },
}
NI_MARGIN_PP = -1.0


def _clean(ax, grid_axis="y"):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)
    ax.grid(True, axis=grid_axis, color=GRID, linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)


def _save(fig, name):
    fig.savefig(FIGDIR / f"{name}.pdf", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(FIGDIR / f"{name}.png", dpi=240, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


# =========================================================== figure 1 ========
def fig1_problem():
    """Self-distillation erodes correctness-matched coverage in every arm."""
    fig = plt.figure(figsize=(7.0, 2.45))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.85, 1.0], wspace=0.40)

    ax = fig.add_subplot(gs[0, 0])
    _clean(ax)
    x = np.arange(len(ROUNDS))
    ax.axhline(CM4_BASE, color=BASE_INK, ls=(0, (4, 2)), lw=1.0, zorder=1)
    ax.annotate(
        f"undistilled base  {CM4_BASE:.2f}",
        xy=(x[-1] + 0.05, CM4_BASE), xytext=(0, 5), textcoords="offset points",
        ha="right", va="bottom", fontsize=7.2, color=BASE_INK,
    )
    order = ["plain", "spd_hard", "spectral_soft"]
    for arm in order:
        y = CM4[arm]
        ax.plot(x, y, color=COLORS[arm], lw=1.6, marker=MARKERS[arm], ms=4.6,
                mec="white", mew=0.6, zorder=3, label=LABELS[arm],
                clip_on=False)
        ax.annotate(
            LABELS[arm], xy=(x[-1], y[-1]), xytext=(6, 0),
            textcoords="offset points", va="center", ha="left",
            fontsize=7.4, color=COLORS[arm], fontweight="bold", clip_on=False,
        )
    ax.fill_between(x, CM4["spectral_soft"], CM4_BASE, color=SPECTRUM, alpha=0.10,
                    zorder=0, lw=0)
    ax.set_xticks(x)
    ax.set_xticklabels([str(r) for r in ROUNDS])
    ax.set_xlabel("self-distillation round", labelpad=2)
    ax.set_ylabel("AST coverage in 4 correct draws  $D_4$   $\\uparrow$", labelpad=2)
    ax.set_ylim(2.58, 3.42)
    ax.set_xlim(-0.18, 5.05)
    ax.set_title("(a)  Correct-implementation coverage collapses in every arm",
                 loc="left", pad=4, color=INK)

    ax2 = fig.add_subplot(gs[0, 1])
    _clean(ax2, grid_axis="x")
    rows = ["base", "plain", "spd_hard", "spectral_soft"]
    ypos = np.arange(len(rows))[::-1]
    for yi, arm in zip(ypos, rows):
        m, lo, hi = P1_R5[arm]
        c = COLORS.get(arm, BASE_INK)
        ax2.plot([lo * 100, hi * 100], [yi, yi], color=c, lw=1.3, alpha=0.75,
                 zorder=2, solid_capstyle="round")
        ax2.plot([m * 100], [yi], marker=MARKERS.get(arm, "s"), ms=5.2, color=c,
                 mec="white", mew=0.6, zorder=3)
        ax2.annotate(f"{m*100:.1f}", xy=(m * 100, yi), xytext=(0, 6),
                     textcoords="offset points", ha="center", fontsize=6.8,
                     color=c)
    ax2.set_yticks(ypos)
    ax2.set_yticklabels([LABELS.get(a, "base") for a in rows], fontsize=7.4)
    for tick, arm in zip(ax2.get_yticklabels(), rows):
        tick.set_color(COLORS.get(arm, BASE_INK))
    ax2.set_ylim(-0.6, len(rows) - 0.4)
    ax2.set_xlim(32.5, 47.5)
    ax2.set_xlabel("pass@1 (%)   $\\uparrow$", labelpad=2)
    ax2.set_title("(b)  ... while single-sample accuracy rises",
                  loc="left", pad=4, color=INK)

    fig.text(0.0, -0.085,
             "Per-round evaluation  ·  Qwen2.5-Coder-1.5B-Instruct  ·  MBPP  ·  "
             "500 tasks $\\times$ 16 samples  ·  seed 43  ·  5 rounds",
             fontsize=6.6, color=MUTED, ha="left")
    _save(fig, "fig1_problem")


# =========================================================== figure 3 ========
def fig3_operator():
    """Soft gain profile vs the hard projector it replaces."""
    fig = plt.figure(figsize=(7.0, 1.95))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.0], wspace=0.22)
    mu = np.linspace(0, 1, 501)

    ax = fig.add_subplot(gs[0, 0])
    _clean(ax)
    ax.plot(mu, mu, color=AXIS, ls=(0, (4, 2)), lw=1.0, zorder=2)
    ax.annotate("identity (no intervention)", xy=(0.02, 0.02), xytext=(4, 4),
                textcoords="offset points", fontsize=6.6, color=MUTED)
    taus = [(0.5, (0, (1, 1.6)), 1.4), (1.0, "solid", 1.9), (2.0, (0, (5, 1.6)), 1.4)]
    for tau, ls, lw in taus:
        g = 1.0 / (1.0 + tau * (1.0 - mu))
        ax.plot(mu, g, color=SPECTRUM, ls=ls, lw=lw,
                alpha=1.0 if tau == 1.0 else 0.55, zorder=3)
    ax.annotate("$\\tau = 1$ (default)", xy=(0.40, 0.605), xytext=(0, 0),
                textcoords="offset points", fontsize=6.8, color=SPECTRUM,
                fontweight="bold", ha="left", va="center")
    ax.annotate("$\\tau = 0.5$", xy=(0.06, 1 / 1.47), xytext=(4, 3),
                textcoords="offset points", fontsize=6.8, color=SPECTRUM, alpha=0.85)
    # Anchor on the tau=2 curve itself: at mu=0.62 that curve is
    # 1/(1 + 2*(1 - 0.62)) = 1/1.76.  The label is then offset below it.
    ax.annotate("$\\tau = 2$", xy=(0.62, 1 / 1.76), xytext=(-6, -28),
                textcoords="offset points", fontsize=6.8, color=SPECTRUM, alpha=0.85,
                ha="right")
    ax.set_xlabel("normalized second-moment eigenvalue  $\\mu = \\lambda/\\lambda_{\\max}$",
                  labelpad=2)
    ax.set_ylabel("directional gain  $s_\\tau(\\mu)$", labelpad=2)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.06)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_title("(a)  Soft gain: no direction is zeroed", loc="left", pad=4)

    ax2 = fig.add_subplot(gs[0, 1])
    _clean(ax2)
    tau = 1.0
    soft = 1.0 / (1.0 + tau * (1.0 - mu))
    r = 0.5
    hard = np.where(mu >= 1.0 - r, 1.0, 0.0)
    ax2.fill_between(mu, 0, soft, color=SPECTRUM, alpha=0.13, lw=0)
    ax2.plot(mu, soft, color=SPECTRUM, lw=1.9, zorder=3)
    ax2.plot(mu, hard, color=SPD, lw=1.9, ls=(0, (5, 1.6)), zorder=3)
    ax2.axvline(1.0 - r, color=AXIS, lw=0.7, zorder=1)
    # Both labels must stay clear of the cutoff line at mu = 1 - r: a label the
    # line strikes through reads as struck out, and a label that spills across
    # the line describes a region it does not sit in.  T1 is kept whole to the
    # left of the line; T2 is given the empty box below the ramp on the right,
    # which is also the region the hard projector actually keeps.
    ax2.annotate("SPECTRUM\ncontinuous, full rank", xy=(0.03, 0.86),
                 xytext=(0, 0), textcoords="offset points", fontsize=6.6,
                 color=SPECTRUM, fontweight="bold", va="center")
    ax2.annotate("hard top-$r$ projection\n(SPD-style)", xy=(0.56, 0.42),
                 xytext=(0, 0), textcoords="offset points", fontsize=6.6,
                 color=SPD, ha="left")
    ax2.annotate("discarded\ndirections", xy=(0.2, 0.03), xytext=(0, 2),
                 textcoords="offset points", fontsize=6.6, color=MUTED, ha="center")
    ax2.annotate("kept", xy=(0.75, 1.05), xytext=(0, -11),
                 textcoords="offset points", fontsize=6.6, color=MUTED, ha="center")
    ax2.set_xlabel("normalized second-moment eigenvalue  $\\mu$", labelpad=2)
    ax2.set_ylabel("directional gain", labelpad=2)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1.12)
    ax2.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax2.set_title("(b)  A cutoff discards; a ramp attenuates", loc="left", pad=4)

    # -0.16 rather than -0.10: panel (a)'s xlabel ends in the subscript of
    # lambda_max, whose descender reaches the baseline band; at -0.10 the
    # footnote sat on that baseline and its ascenders met the subscript.
    fig.text(0.0, -0.16,
             "Analytic evaluations of $s_\\tau(\\mu)=1/[1+\\tau(1-\\mu)]$ · "
             "not measured model spectra · the hard curve is the SPD-style "
             "top-$r$ projector with $r$ set to half the directions",
             fontsize=6.6, color=MUTED, ha="left")
    _save(fig, "fig3_operator")


# =========================================================== figure 4 ========
def fig4_effects():
    """Paired effects at the round-5 checkpoint, 64-sample tier.

    $D_4$ and $C_{64}$ are different endpoints and are never drawn on one axis.
    Their round-5 effects span 0.64 and 5.38 AST classes respectively, so a
    shared axis compresses every $D_4$ interval -- each about 0.09 wide -- to
    under 2% of the panel, i.e. to a single dot.  Panels (a) and (b) therefore
    carry separate x-axes.

    The three panels sit in one row rather than a stack, and panel (c) puts both
    budgets on one row as two markers instead of doubling the row count.  Both
    choices, plus the wide-and-short canvas with fonts scaled to match, exist to
    hold the rendered height near 1.5 in: the manuscript includes the figure at
    \\textwidth, so the rendered height is 5.5 x h/w and every inch of it is paid
    for out of the nine-page budget.
    """
    fig = plt.figure(figsize=(7.6, 1.90))
    # The default margins leave a third of the canvas empty, which \\textwidth
    # then scales away along with the type.  Using the full width instead makes
    # the figure shorter on the page at the same rendered type size.
    fig.subplots_adjust(left=0.045, right=0.995, top=0.845, bottom=0.315)
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 1.12], wspace=0.58)

    contrasts = ["base", "plain", "spd_hard"]
    clabels = {"base": "vs base", "plain": "vs plain", "spd_hard": "vs SPD-hard"}
    ccol = {"base": BASE_INK, "plain": PLAIN, "spd_hard": SPD}

    def forest(ax, endpoint, mk, title, xlabel):
        """One endpoint's three paired contrasts, on its own x-axis."""
        _clean(ax, grid_axis="x")
        ypos = np.arange(len(contrasts))[::-1]
        lo_all = min(EVAL64[c][endpoint][1] for c in contrasts)
        hi_all = max(EVAL64[c][endpoint][2] for c in contrasts)
        span = hi_all - lo_all
        # A value label drops below its marker once it would otherwise sit within
        # a tenth of the panel range of the label already placed.  On $D_4$ the
        # plain and SPD-hard points are 0.04 apart and their intervals overlap
        # outright, so two labels stacked above them would collide.
        last_pt = None
        for yi, c in zip(ypos, contrasts):
            pt, lo, hi, n = EVAL64[c][endpoint]
            col = ccol[c]
            ax.plot([lo, hi], [yi, yi], color=col, lw=1.3, alpha=0.8, zorder=2,
                    solid_capstyle="round")
            ax.plot([pt], [yi], marker=mk, ms=4.8, color=col, mec="white",
                    mew=0.6, zorder=3)
            below = last_pt is not None and abs(pt - last_pt) < 0.10 * span
            ax.annotate(f"{pt:+.2f}", xy=(pt, yi),
                        xytext=(0, -5.5 if below else 5.5),
                        textcoords="offset points",
                        ha="center", va="top" if below else "baseline",
                        fontsize=7.1, color=col)
            last_pt = pt
        ax.axvline(0, color=AXIS, lw=0.9, zorder=1)
        ax.set_yticks(ypos)
        ax.set_yticklabels([clabels[c] for c in contrasts], fontsize=7.8)
        ax.set_ylim(-0.62, len(contrasts) - 0.38)
        ax.set_xlim(lo_all - 0.09 * span, hi_all + 0.09 * span)
        ax.set_xlabel(xlabel, labelpad=2, fontsize=8.4)
        ax.set_title(title, loc="left", pad=3.5, fontsize=8.8)

    # (a) and (b): coverage, one panel per endpoint -- never one axis for both.
    forest(fig.add_subplot(gs[0, 0]), "cm@4", "D",
           "(a)  $D_4$: coverage in 4 correct draws",
           "paired difference (AST classes)")
    forest(fig.add_subplot(gs[0, 1]), "cov@64", "o",
           "(b)  $C_{64}$: coverage at 64 samples",
           "paired difference (AST classes)")

    # (c) Correctness.  Both budgets ride on one row as two markers -- diamond
    # for pass@1, circle for pass@64 -- which keeps the panel three rows tall
    # like its neighbours instead of six.
    ax2 = fig.add_subplot(gs[0, 2])
    _clean(ax2, grid_axis="x")
    ypos2 = np.arange(len(contrasts))[::-1]
    pp = {c: {e: tuple(v * 100 for v in EVAL64[c][e][:3])
              for e in ("pass@1", "pass@64")} for c in contrasts}
    lo_all = min(pp[c][e][1] for c in contrasts for e in ("pass@1", "pass@64"))
    hi_all = max(pp[c][e][2] for c in contrasts for e in ("pass@1", "pass@64"))
    span = hi_all - lo_all
    for yi, c in zip(ypos2, contrasts):
        col = ccol[c]
        for e, mk in (("pass@1", "D"), ("pass@64", "o")):
            pt, lo, hi = pp[c][e]
            ax2.plot([lo, hi], [yi, yi], color=col, lw=1.3, alpha=0.8, zorder=2,
                     solid_capstyle="round")
            ax2.plot([pt], [yi], marker=mk, ms=4.8, color=col, mec="white",
                     mew=0.6, zorder=3)
        # Both labels sit above their marker: within a row the two budgets are
        # at least 1.8 pp apart, far wider than the labels themselves.
        for e in ("pass@1", "pass@64"):
            pt = pp[c][e][0]
            ax2.annotate(f"{pt:+.2f}", xy=(pt, yi), xytext=(0, 5.5),
                         textcoords="offset points", ha="center", fontsize=7.1,
                         color=col)
    ax2.axvline(0, color=AXIS, lw=0.9, zorder=1)
    ax2.axvline(NI_MARGIN_PP, color=SPD, lw=1.0, ls=(0, (3, 2)), zorder=1)
    ax2.annotate("$-1$ pp", xy=(NI_MARGIN_PP, -0.52), xytext=(3, 0),
                 textcoords="offset points", fontsize=7.1, color=SPD, ha="left",
                 va="bottom")
    ax2.set_yticks(ypos2)
    ax2.set_yticklabels([clabels[c] for c in contrasts], fontsize=7.8)
    ax2.set_ylim(-0.62, len(contrasts) - 0.38)
    ax2.set_xlim(lo_all - 0.09 * span, hi_all + 0.09 * span)
    ax2.set_xlabel("paired difference (pp)", labelpad=2, fontsize=8.4)
    ax2.set_title("(c)  Correctness", loc="left", pad=3.5, fontsize=8.8)

    # The footnote is wrapped to two lines on purpose.  As one long line it became
    # the widest object in the figure, and bbox_inches="tight" then sized the
    # canvas to the *text* rather than the plots -- 9.0 in instead of 7.0.  Since
    # the manuscript includes the figure at \textwidth, that inflated width scaled
    # every label by 0.61/0.79, rendering 7 pt type at about 4.3 pt.  Wrapped, the
    # plots set the width and the type renders at its stated size.
    # Three short lines, not one long one: a line wide enough to hold all of this
    # becomes the widest object in the figure, and bbox_inches="tight" then sizes
    # the canvas to the *text* rather than the plots.  Since the manuscript
    # includes the figure at \textwidth, that extra width scales the type down
    # without buying any height back.  Kept to the plot width instead.
    # The marker key belongs to panel (c) alone.  In (a) the diamond marks the
    # $D_4$ endpoint and in (b) the circle marks $C_{64}$, so an unqualified
    # "diamond = pass@1" would mislabel the two panels to its left.
    fig.text(0.0, 0.070,
             "(c): ◆ pass@1, ● pass@64 · 95% paired task-bootstrap CIs · "
             "$n$ = 311--318 for $D_4$, else 500",
             fontsize=7.1, color=MUTED, ha="left")
    # Not "the interval lies below the line": the SPD-hard pass@1 interval is
    # $[-1.89,-0.98]$ pp, which straddles $-1$.  What fails is the criterion on
    # its lower bound, and that is what the caption and section 5.4 both say.
    fig.text(0.0, 0.004,
             "Dashed line: the pre-declared $-1$ pp noninferiority bound for "
             "pass@1, which the SPD-hard interval straddles ($[-1.89,-0.98]$).",
             fontsize=7.1, color=MUTED, ha="left")
    _save(fig, "fig4_effects")


# =========================================================== figure 5 ========
def fig5_compounding():
    """The advantage over hard projection grows with rounds; the loss vs base saturates."""
    fig = plt.figure(figsize=(7.6, 2.10))
    # Same reasoning as fig4_effects: use the canvas width rather than the default
    # margins, which \textwidth would otherwise scale away along with the type.
    fig.subplots_adjust(left=0.055, right=0.985, top=0.86, bottom=0.205)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.0], wspace=0.30)
    x = np.arange(len(ROUNDS))

    ax = fig.add_subplot(gs[0, 0])
    _clean(ax)
    for series, col, lab, mk in (
        (CM4_DELTA_SPD, SPECTRUM, "SPECTRUM $-$ SPD-hard", "D"),
        (CM4_DELTA_BASE, PLAIN, "SPECTRUM $-$ base", "o"),
    ):
        pts = np.array([s[0] for s in series])
        lo = np.array([s[1] for s in series])
        hi = np.array([s[2] for s in series])
        ax.fill_between(x, lo, hi, color=col, alpha=0.15, lw=0)
        ax.plot(x, pts, color=col, lw=1.6, marker=mk, ms=4.6, mec="white",
                mew=0.6, zorder=3)
        ax.annotate(f"{pts[-1]:+.2f}", xy=(x[-1], pts[-1]), xytext=(5, 0),
                    textcoords="offset points", va="center", fontsize=8.2,
                    color=col, fontweight="bold", clip_on=False)
    ax.axhline(0, color=AXIS, lw=0.9, zorder=1)
    ax.annotate("SPECTRUM $-$ SPD-hard", xy=(0.03, 0.86), xycoords="axes fraction",
                fontsize=8.4, color=SPECTRUM, fontweight="bold")
    ax.annotate("SPECTRUM $-$ base", xy=(0.03, 0.14), xycoords="axes fraction",
                fontsize=8.4, color=PLAIN, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([str(r) for r in ROUNDS])
    ax.set_xlabel("self-distillation round", labelpad=2)
    ax.set_ylabel("paired $\\Delta D_4$ (AST classes)   $\\uparrow$", labelpad=2,
                  fontsize=8.6)
    ax.set_xlim(-0.2, 4.7)
    ax.set_title("(a)  The advantage over hard projection compounds",
                 loc="left", pad=4, fontsize=9.1)

    ax2 = fig.add_subplot(gs[0, 1])
    _clean(ax2)
    # Every arm on the same paired footing as panel (a); SPECTRUM last so its
    # marks sit on top of the two nearly coincident comparator series.
    for arm in ("plain", "spd_hard", "spectral_soft"):
        series = CM4_DELTA_BASE_ALL[arm]
        pts = np.array([v[0] for v in series])
        lo = np.array([v[1] for v in series])
        hi = np.array([v[2] for v in series])
        ax2.fill_between(x, lo, hi, color=COLORS[arm], alpha=0.13, lw=0)
        ax2.plot(x, pts, color=COLORS[arm], lw=1.6, marker=MARKERS[arm],
                 ms=4.2, mec="white", mew=0.6, zorder=3, label=LABELS[arm])
    # Endpoint labels are staggered vertically: plain and SPD-hard finish only
    # 0.05 AST classes apart, so a common va="center" would overlap them.
    for arm, dy in (("spectral_soft", 0), ("plain", 5.0), ("spd_hard", -5.0)):
        v = CM4_DELTA_BASE_ALL[arm][-1][0]
        ax2.annotate(f"{v:+.2f}", xy=(x[-1], v), xytext=(5, dy),
                     textcoords="offset points", va="center", fontsize=7.9,
                     color=COLORS[arm], fontweight="bold", clip_on=False)
    ax2.axhline(0, color=AXIS, lw=0.9, zorder=1)
    ax2.set_xticks(x)
    ax2.set_xticklabels([str(r) for r in ROUNDS])
    ax2.set_xlabel("self-distillation round", labelpad=2)
    ax2.set_ylabel("paired $\\Delta D_4$ vs base (AST classes)", labelpad=2,
                  fontsize=8.6)
    ax2.set_xlim(-0.2, 4.7)
    # The zero reference line spans the full width, so any legend placed against
    # the top of the panel has that line running through its last row -- and an
    # unframed legend cannot occlude it.  The lower-left corner is empty (the
    # earliest, highest series values sit at -0.02 and descend), so the legend
    # goes there and the top of the range can come down to just clear the line.
    ax2.set_ylim(-0.86, 0.12)
    ax2.legend(frameon=False, loc="lower left", fontsize=7.9, ncol=1,
               handlelength=1.3, borderpad=0.0, labelspacing=0.22,
               handletextpad=0.5)
    ax2.set_title("(b)  Coverage loss relative to the base",
                  loc="left", pad=4, fontsize=9.1)

    # The $n$ ranges differ per series and per panel, so they are given per
    # panel: 236--246 is the union over panel (b)'s three arms, while panel (a)'s
    # SPECTRUM-vs-base series alone spans 236--245 and its SPD-hard series
    # 248--254.  A single "236--246 vs base" would have described neither panel's
    # actual series.  Kept to one line so that the plots, not the text, set the
    # canvas width (see fig4_effects for what a long footnote costs).
    # A series end-label sits just above this line, and at y=0.005 the two were
    # 6.6 pt apart -- close enough that their glyph boxes overlapped by 30% of
    # the type height.  No ink met, but it reads as crowded, so the footnote is
    # dropped ~3 pt.  It is the only text below the canvas edge; bbox_inches
    # takes it into account, so nothing is clipped.
    fig.text(0.0, -0.017,
             "$D_4$ eligible $n$ for the plotted series: (a) 248--254 vs "
             "SPD-hard, 236--245 vs base; (b) 236--246, union across the three "
             "arms",
             fontsize=7.9, color=MUTED, ha="left")
    _save(fig, "fig5_compounding")


# =========================================================== figure 2 ========
def fig2_method():
    """Pipeline: temporary spectral intervention, then ordinary self-distillation."""
    fig, ax = plt.subplots(figsize=(7.0, 2.62))
    ax.set_xlim(0, 141)
    ax.set_ylim(-4, 50)
    ax.axis("off")

    def box(x, y, w, h, title, lines=(), accent=False, dashed=False):
        face = "#eef4fc" if accent else "#f7f7f5"
        edge = SPECTRUM if accent else AXIS
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.1",
            linewidth=1.2 if accent else 0.8, edgecolor=edge, facecolor=face,
            linestyle=(0, (3, 2)) if dashed else "solid", zorder=2))
        ax.text(x + w / 2, y + h - 2.3, title, ha="center", va="top",
                fontsize=7.5, fontweight="bold",
                color=SPECTRUM if accent else INK, zorder=3)
        for i, ln in enumerate(lines):
            ax.text(x + w / 2, y + 1.9 + i * 3.9, ln, ha="center", va="bottom",
                    fontsize=6.4, color="#4a4a48", zorder=3)

    def arrow(x0, y0, x1, y1, color=AXIS, lw=1.1, ls="solid", head=True):
        ax.add_patch(FancyArrowPatch(
            (x0, y0), (x1, y1), arrowstyle="-|>" if head else "-",
            mutation_scale=7, color=color, lw=lw, linestyle=ls, zorder=1,
            shrinkA=0, shrinkB=0))

    UY, UH, UC = 27, 14, 34.0
    LY, LH, LC = 7, 13, 13.5

    ax.text(1, 42.8, "GENERATION", fontsize=6.2, color=MUTED, fontweight="bold")
    ax.text(22, 21.7, "TRAINING", fontsize=6.2, color=MUTED, fontweight="bold")

    # ---- upper lane -------------------------------------------------------
    box(1, UY, 16, UH, "Native $\\theta_t$")
    box(22, UY, 30, UH, "Reference calibration",
        ["$C_\\ell=\\frac{1}{M_\\ell}\\sum g_{iu}g_{iu}^{\\top}$"])
    box(57, UY, 32, UH, "Soft spectral gain",
        ["$\\tau=1$; no direction zeroed",
         "$T_{\\ell,\\tau}=[\\mathbf{I}+\\tau(\\mathbf{I}-\\bar C_\\ell)]^{-1}$"],
        accent=True)
    box(94, UY, 19, UH, "Fold in", ["$b'=T^{\\top}b$", "$W'=T^{\\top}W$"])
    box(118, UY, 21, UH, "Generate", ["per prompt", "1 raw completion"])

    for x0, x1 in ((17, 22), (52, 57), (89, 94), (113, 118)):
        arrow(x0 + 0.4, UC, x1 - 0.4, UC)

    # ---- lower lane -------------------------------------------------------
    box(22, LY, 30, LH, "Ordinary LoRA",
        ["initialised from saved $\\theta_t$", "all nonpadding targets"])
    box(57, LY, 22, LH, "Merge", ["native $\\theta_{t+1}$"])
    box(87, LY, 24, LH, "Native evaluation", ["no spectral transform"],
        dashed=True)

    arrow(52.4, LC, 56.6, LC)
    arrow(79.4, LC, 86.6, LC, ls=(0, (3, 2)))

    # ---- corpus: generation -> training (the dominant connector) ----------
    arrow(128.5, UY - 0.3, 128.5, 22.6, color=SPECTRUM, lw=2.0, head=False)
    arrow(128.5, 22.6, 44, 22.6, color=SPECTRUM, lw=2.0, head=False)
    arrow(44, 22.6, 44, LY + LH + 0.3, color=SPECTRUM, lw=2.0)
    ax.text(86, 23.7, "raw completions — wrong and empty ones kept",
            ha="center", va="center", fontsize=6.4, color=SPECTRUM,
            fontweight="bold")

    # ---- saved-state restore gate ----------------------------------------
    arrow(9, UY - 0.3, 9, 16.5, color=BASE_INK, lw=0.9, ls=(0, (2, 2)),
          head=False)
    arrow(9, 16.5, 21.7, 16.5, color=BASE_INK, lw=0.9, ls=(0, (2, 2)))
    ax.text(10.3, 20.6, "saved\nnative $\\theta_t$", fontsize=6.3, color=BASE_INK,
            va="center", ha="left", linespacing=1.3)

    # ---- outer recurrence: native theta_{t+1} -> calibration --------------
    arrow(68, LY - 0.3, 68, 2.8, color=BASE_INK, lw=0.9, head=False)
    arrow(68, 2.8, 19, 2.8, color=BASE_INK, lw=0.9, head=False)
    arrow(19, 2.8, 19, 47, color=BASE_INK, lw=0.9, head=False)
    arrow(19, 47, 37, 47, color=BASE_INK, lw=0.9, head=False)
    arrow(37, 47, 37, UY + UH + 0.3, color=BASE_INK, lw=0.9)
    ax.text(60, 48.3,
            "next round: recalibrate $\\bar C$ from the merged native checkpoint",
            ha="center", va="center", fontsize=6.4, color=BASE_INK)

    ax.text(1, -2.6,
            "Solid = generation and training path     ·     dashed = evaluation "
            "branch     ·     dotted = saved-state restoration",
            fontsize=6.3, color=MUTED, va="center")
    _save(fig, "fig2_method")


if __name__ == "__main__":
    fig1_problem()
    fig2_method()
    fig3_operator()
    fig4_effects()
    fig5_compounding()
    for p in sorted(FIGDIR.glob("fig*")):
        print(p.name, f"{p.stat().st_size/1024:.1f} KiB")
