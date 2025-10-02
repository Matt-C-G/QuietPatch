from __future__ import annotations
import io
import matplotlib
matplotlib.use("Agg")  # headless, offline
import matplotlib.pyplot as plt

def _svg_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="svg", bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()

def sparkline(values, title=""):
    fig = plt.figure(figsize=(3.2, 0.9), dpi=160)
    ax = fig.add_subplot(111)
    ax.plot(values, linewidth=2)
    ax.set_title(title, fontsize=8)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return _svg_bytes(fig)

def sev_bar(vulns_by_sev):
    order = ["critical","high","medium","low"]
    vals = [vulns_by_sev.get(s,0) for s in order]
    fig = plt.figure(figsize=(3.6, 2.0), dpi=160)
    ax = fig.add_subplot(111)
    ax.bar(order, vals)
    ax.set_title("Findings by Severity", fontsize=9)
    return _svg_bytes(fig)

def heatmap(table_2d, row_labels, col_labels, title="Heatmap"):
    import numpy as np
    data = [[table_2d.get(r,{}).get(c,0) for c in col_labels] for r in row_labels]
    arr = np.array(data)
    fig = plt.figure(figsize=(3.6, 2.6), dpi=160)
    ax = fig.add_subplot(111)
    im = ax.imshow(arr, aspect="auto")
    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels, fontsize=7, rotation=45, ha="right")
    ax.set_yticks(range(len(row_labels)))
    ax.set_yticklabels(row_labels, fontsize=7)
    ax.set_title(title, fontsize=9)
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            ax.text(j, i, str(int(arr[i, j])), ha="center", va="center", fontsize=6)
    return _svg_bytes(fig)
