"""
AI adoption in US businesses, 2025-2026 (Ramp AI Index).

Reproduces every number in the write-up:
  1. The baseline: overall AI adoption, Dec 2025 vs Oct 2026
  2. The vendor split: Anthropic vs OpenAI over the same months
  3. Robustness: the jump by company size
  4. The overlap test: a lower bound on businesses paying BOTH vendors

Data: the two CSV files in this folder, exported from the Ramp Data connector (shares in %, rounded to 0.1-0.01).
Run:  python analysis.py
"""
import pandas as pd
import matplotlib.pyplot as plt

START, END = "2025-12", "2026-10"

vendors = pd.read_csv("ai_adoption_by_vendor_monthly.csv").set_index("month")
sizes = pd.read_csv("ai_adoption_by_size.csv")

# 1. Baseline
overall_start = vendors.loc[START, "all_ai_vendors_pct"]
overall_end = vendors.loc[END, "all_ai_vendors_pct"]
overall_gain = overall_end - overall_start
print(f"Overall AI adoption: {overall_start:.1f}% -> {overall_end:.1f}% ({overall_gain:+.1f} pts)")

# 2. Vendor split
for col, name in [("anthropic_pct", "Anthropic"), ("openai_pct", "OpenAI")]:
    a, b = vendors.loc[START, col], vendors.loc[END, col]
    print(f"{name}: {a:.1f}% -> {b:.1f}% ({b - a:+.1f} pts)")
crossover = vendors[vendors["anthropic_pct"] > vendors["openai_pct"]].index.min()
print(f"Anthropic first passes OpenAI in: {crossover}")

# 3. Robustness by company size
wide = sizes.pivot(index="size", columns="month", values="ai_adoption_pct")
wide["change_pts"] = wide[END] - wide[START]
print("\nBy company size:\n", wide.round(1))

# 4. Overlap test.
# For any two sets A and B inside a population: |A and B| >= |A| + |B| - |A or B|.
# |A or B| can be at most the overall AI adoption share, so
#   both_vendors >= openai + anthropic - overall
def min_overlap(month):
    r = vendors.loc[month]
    return r["openai_pct"] + r["anthropic_pct"] - r["all_ai_vendors_pct"]

anthropic_gain = vendors.loc[END, "anthropic_pct"] - vendors.loc[START, "anthropic_pct"]
print(f"\nAt least {min_overlap(START):.1f}% paid both vendors in {START}; at least {min_overlap(END):.1f}% in {END}")
print(f"Anthropic gained {anthropic_gain:.1f} pts but overall adoption only {overall_gain:.1f} pts,")
print(f"so at least {anthropic_gain - overall_gain:.1f} pts of Anthropic's gain came from businesses already paying for AI.")

# Chart
fig, ax = plt.subplots(figsize=(10, 5))
x = pd.to_datetime(vendors.index)
ax.plot(x, vendors["all_ai_vendors_pct"], color="#9a9a9a", lw=2.5, label="All AI vendors")
ax.plot(x, vendors["openai_pct"], color="#c8c8c8", lw=2, label="OpenAI")
ax.plot(x, vendors["anthropic_pct"], color="#2a6fdb", lw=3, label="Anthropic")
ax.axvline(pd.to_datetime(START), color="#777", ls="--", lw=1)
ax.set_ylim(0, 60)
ax.set_ylabel("Share of US businesses on Ramp (%)")
ax.set_title("AI adoption rose 12 points in 2026 as Anthropic gained 27 and OpenAI held flat", loc="left")
ax.legend(frameon=False)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig("ai_adoption_chart_matplotlib.png", dpi=150)
print("\nSaved ai_adoption_chart_matplotlib.png")
