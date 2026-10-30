"""Figure 80: Run 4 vs Run 5 stepped test, command confirmation p95 and Run 5 throughput by learners.

Usage: python chart_compare.py <run4_per_minute.json> <run5_per_minute.json> <out.png>
"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

full = lambda rows: [r for r in rows if r["seconds"] >= 45]
r4 = full(json.load(open(sys.argv[1])))
r5 = [r for r in json.load(open(sys.argv[2])) if r["seconds"] >= 60]
# Run 5 holds 40 learners for two minutes after the ramp; place those minutes just right of 40.
x5 = [r["learners_joined"] + 1.4 * max(0, i - 9) for i, r in enumerate(r5)]
x4 = [r["learners_joined"] for r in r4]

plt.rcParams.update({"font.family": "Arial", "font.size": 10})
fig, ax = plt.subplots(figsize=(7.2, 3.9), dpi=200)
ax2 = ax.twinx()
ax2.bar(x5, [r["rps"] for r in r5], width=1.2, color="#d99a2b", alpha=0.35, label="Run 5 throughput (requests/s)")
ax2.set_ylabel("Requests per second")
ax2.set_ylim(0, 6)
ax.plot(x4, [r["submit_p95_ms"] / 1000 for r in r4], marker="s", color="#8a8a8a", lw=1.6, ls="-",
        label="Run 4: database in Tokyo, 2 threads (p95)")
ax.plot(x5, [r["submit_p95_ms"] / 1000 for r in r5], marker="o", color="#1f4e9c", lw=2,
        label="Run 5: database in Singapore, 8 threads (p95)")
ax.axhline(1.0, color="#555555", ls="--", lw=1)
ax.text(29.5, 0.55, "NFR-PERF-01 target: 1 s", color="#333333", fontsize=9)
for xi, r in zip(x5, r5):
    ax.annotate(f"{r['submit_p95_ms'] / 1000:.1f}", (xi, r["submit_p95_ms"] / 1000), textcoords="offset points",
                xytext=(-10 if xi > 42 else (6 if xi > 41 else 0), 6), ha="center", fontsize=7.5, color="#1f4e9c")
ax.annotate("Run 4 stopped:\nhosting edge rejecting", (x4[-1], r4[-1]["submit_p95_ms"] / 1000),
            xytext=(x4[-1] - 14, 7.6), fontsize=8, arrowprops=dict(arrowstyle="->", color="#333333"))
ax.set_xlabel("Learners playing (one joined every 15 s; the last two Run 5 points hold 40)")
ax.set_ylabel("Seconds")
ax.set_ylim(0, 8.8)
ax.set_xticks([4, 8, 12, 16, 20, 24, 28, 32, 36, 40])
ax.set_zorder(ax2.get_zorder() + 1)
ax.patch.set_visible(False)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left", bbox_to_anchor=(0.0, 0.86), fontsize=8, frameon=False)
for a in (ax, ax2):
    a.spines["top"].set_visible(False)
fig.tight_layout()
fig.savefig(sys.argv[3])
print("ok")
