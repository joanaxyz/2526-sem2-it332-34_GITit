"""Figure 81: Run 6 by minute - command confirmation p50/p95 against the SRS 1.4 targets, and throughput.

Usage: python chart_run6.py <r6_step_per_minute.json> <out.png>
"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rows = [r for r in json.load(open(sys.argv[1])) if r["seconds"] >= 60]
x = [r["minute"] for r in rows]
p95 = [r["submit_p95_ms"] / 1000 for r in rows]
p50 = [r["submit_p50_ms"] / 1000 for r in rows]

plt.rcParams.update({"font.family": "Arial", "font.size": 10})
fig, ax = plt.subplots(figsize=(7.2, 3.9), dpi=200)
ax2 = ax.twinx()
ax2.bar(x, [r["rps"] for r in rows], width=0.7, color="#d99a2b", alpha=0.35, label="Throughput (requests/s)")
ax2.axhline(4, color="#b07a1a", ls=":", lw=1)
ax2.text(20.6, 4.05, "≥ 4/s", color="#8a5d10", fontsize=8, va="bottom", ha="right")
ax2.set_ylabel("Requests per second")
ax2.set_ylim(0, 8)
ax.plot(x, p95, marker="o", color="#1f4e9c", lw=2, label="Command confirmation, 95th percentile")
ax.plot(x, p50, marker="o", color="#6f9fd8", lw=1.6, label="Command confirmation, median")
ax.hlines(1.5, 0.6, 5.4, color="#555555", ls="--", lw=1)
ax.text(0.7, 1.6, "≤ 1.5 s up to 20 learners", fontsize=8, color="#333333")
ax.hlines(4.0, 10.6, 20.4, color="#555555", ls="--", lw=1)
ax.text(10.7, 4.1, "≤ 4 s with 40 learners", fontsize=8, color="#333333")
ax.axvspan(10.5, 20.5, color="#1f4e9c", alpha=0.05)
ax.text(15.5, 5.15, "10-minute hold at 40 learners", ha="center", fontsize=8.5, color="#1f4e9c")
ax.text(5.5, 5.15, "Joining, one learner every 15 s", ha="center", fontsize=8.5, color="#333333")
ax.set_xlabel("Minute of Run 6 (learners joined: 4 per minute until 40 at minute 10)")
ax.set_ylabel("Seconds")
ax.set_ylim(0, 5.6)
ax.set_xticks(x)
ax.set_zorder(ax2.get_zorder() + 1)
ax.patch.set_visible(False)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left", bbox_to_anchor=(0.0, 0.9), fontsize=8, frameon=False)
for a in (ax, ax2):
    a.spines["top"].set_visible(False)
fig.tight_layout()
fig.savefig(sys.argv[2])
print("ok")
