import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Working Capital Forecast",
    page_icon="📊",
    layout="centered",
)

st.title("تطبيق التنبؤ برأس المال العامل")
st.caption("Working Capital Forecasting App")

default_df = pd.DataFrame({
    "period": ["2023", "2024", "2025"],
    "revenue": [1000000.0, 1120000.0, 1250000.0],
    "cogs": [600000.0, 672000.0, 750000.0],
    "accounts_receivable": [120000.0, 140000.0, 155000.0],
    "inventory": [95000.0, 110000.0, 125000.0],
    "accounts_payable": [80000.0, 92000.0, 105000.0],
})

st.subheader("1. البيانات التاريخية")
hist_df = st.data_editor(default_df, num_rows="dynamic", width="stretch")

st.subheader("2. إعدادات التنبؤ")
col1, col2, col3 = st.columns(3)
with col1:
    growth_rate = st.number_input("نسبة نمو الإيرادات (%)", value=10.0, step=1.0) / 100.0
with col2:
    cogs_ratio = st.number_input("نسبة التكلفة من الإيرادات (%)", value=60.0, step=1.0) / 100.0
with col3:
    periods = st.number_input("عدد فترات التنبؤ", min_value=1, max_value=10, value=3, step=1)

days_in_period = st.selectbox(
    "نوع الفترة",
    options=[365, 91.25, 30],
    format_func=lambda x: {
        365: "سنوي (365 يوم)",
        91.25: "فصلي (91.25 يوم)",
        30: "شهري (30 يوم)",
    }[x],
)

df = hist_df.copy()
df["dso"] = (df["accounts_receivable"] / df["revenue"]) * days_in_period
df["dio"] = (df["inventory"] / df["cogs"]) * days_in_period
df["dpo"] = (df["accounts_payable"] / df["cogs"]) * days_in_period
df["nwc"] = df["accounts_receivable"] + df["inventory"] - df["accounts_payable"]
df["nwc_change"] = df["nwc"].diff()
df["is_forecast"] = False

avg_dso = df["dso"].mean()
avg_dio = df["dio"].mean()
avg_dpo = df["dpo"].mean()

last_row = df.iloc[-1]
base_revenue = float(last_row["revenue"])
prev_nwc_exact = float(last_row["nwc"])

proj_rows = []
for i in range(1, int(periods) + 1):
    proj_rev = base_revenue * ((1 + growth_rate) ** i)
    proj_cogs = proj_rev * cogs_ratio
    proj_ar = (avg_dso / days_in_period) * proj_rev
    proj_inv = (avg_dio / days_in_period) * proj_cogs
    proj_ap = (avg_dpo / days_in_period) * proj_cogs
    proj_nwc = proj_ar + proj_inv - proj_ap
    nwc_chg = proj_nwc - prev_nwc_exact
    prev_nwc_exact = proj_nwc

    proj_rows.append({
        "period": f"Forecast_{i}",
        "revenue": proj_rev,
        "cogs": proj_cogs,
        "accounts_receivable": proj_ar,
        "inventory": proj_inv,
        "accounts_payable": proj_ap,
        "dso": avg_dso,
        "dio": avg_dio,
        "dpo": avg_dpo,
        "nwc": proj_nwc,
        "nwc_change": nwc_chg,
        "is_forecast": True,
    })

final_df = pd.concat([df, pd.DataFrame(proj_rows)], ignore_index=True)

money_cols = ["revenue", "cogs", "accounts_receivable", "inventory", "accounts_payable", "nwc", "nwc_change"]
day_cols = ["dso", "dio", "dpo"]
display_df = final_df.copy()
display_df[money_cols] = display_df[money_cols].round(2)
display_df[day_cols] = display_df[day_cols].round(1)

st.subheader("3. جدول النتائج")
st.dataframe(display_df, width="stretch")

st.subheader("4. الرسم البياني")
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(final_df["period"], final_df["nwc"], marker="o", label="NWC")
ax.bar(final_df["period"], final_df["nwc_change"].fillna(0), alpha=0.35, label="NWC Change")
ax.legend()
ax.grid(True, alpha=0.25)
st.pyplot(fig)
