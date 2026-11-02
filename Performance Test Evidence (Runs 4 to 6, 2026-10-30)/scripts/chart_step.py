import json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
rows = json.load(open(sys.argv[1]))
x = [r["learners_joined"] for r in rows]
p50 = [r["submit_p50_ms"] / 1000 for r in rows]
p95 = [r["submit_p95_ms"] / 1000 for r in rows]
rps = [r["rps"] for r in rows]
plt.rcParams.update({"font.family": "Arial", "font.size": 10})
fig, ax = plt.subplots(figsize=(7.2, 3.9), dpi=200)
ax.plot(x, p95, marker="o", color="#1f4e9c", lw=2, label="Command confirmation, 95th percentile")
ax.plot(x, p50, marker="o", color="#6f9fd8", lw=2, label="Command confirmation, median")
ax.axhline(1.0, color="#555555", ls="--", lw=1)
ax.text(x[2] + 0.6, 0.62, "NFR-PERF-01 target: 1 s", color="#333333", fontsize=9)
ax.set_xlabel("Learners playing (one joined every 15 s)")
ax.set_ylabel("Seconds")
ax.set_ylim(0, 8.5); ax.set_xticks(x)
ax2 = ax.twinx()
ax2.bar(x, rps, width=1.6, color="#d99a2b", alpha=0.35, label="Throughput (requests/s)")
ax2.set_ylabel("Requests per second"); ax2.set_ylim(0, 4.5)
ax.set_zorder(ax2.get_zorder() + 1); ax.patch.set_visible(False)
for xi, yi in zip(x, p95):
    ax.annotate(f"{yi:.1f}", (xi, yi), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=8, color="#1f4e9c")
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8, frameon=False)
ax.annotate("Hosting edge starts\nrejecting (503, 429)", (x[-1], p95[-1]), xytext=(x[-1] - 11, 8.0), fontsize=8,
            arrowprops=dict(arrowstyle="->", color="#333333"))
for s in ("top",): ax.spines[s].set_visible(False); ax2.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(sys.argv[2])
print("ok")
