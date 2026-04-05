import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide", page_title="PE Valuation Terminal")

# ---------- IRR FUNCTION ----------
def compute_irr(cashflows, guess=0.1):
    rate = guess
    for _ in range(1000):
        npv = sum(cf / (1 + rate) ** i for i, cf in enumerate(cashflows))
        d_npv = sum(-i * cf / (1 + rate) ** (i + 1) for i, cf in enumerate(cashflows))
        rate -= npv / d_npv
    return rate

# ---------- SENSITIVITY FUNCTION ----------
def calculate_ev_sensitivity(base_fcf, wacc_range, g_range, years):
    heatmap = []

    for w in wacc_range:
        row = []
        for g in g_range:
            if w <= g:
                row.append(np.nan)
            else:
                tv = (base_fcf * (1 + g)) / (w - g)
                pv_tv = tv / ((1 + w) ** years)
                row.append(pv_tv)
        heatmap.append(row)

    return pd.DataFrame(
        heatmap,
        index=[f"{round(w*100,1)}%" for w in wacc_range],
        columns=[f"{round(g*100,1)}%" for g in g_range]
    )

# ---------- UI STYLE ----------
st.markdown("""
<style>
body {background-color:#0b0f14; color:#e6e6e6;}
.stMetric {background:#111827; padding:15px; border-radius:10px;}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.title("📊 Private Equity Valuation Terminal")
st.caption("DCF + LBO + Sensitivity | Bloomberg Style")

# ---------- SIDEBAR ----------
st.sidebar.header("⚙️ Inputs")

revenue = st.sidebar.number_input("Initial Revenue", value=1000.0)
growth = st.sidebar.slider("Growth %", 0.0, 0.30, 0.10)
ebitda_margin = st.sidebar.slider("EBITDA %", 0.0, 0.50, 0.25)
tax_rate = st.sidebar.slider("Tax %", 0.0, 0.40, 0.25)
wacc = st.sidebar.slider("WACC %", 0.01, 0.20, 0.10)
terminal_growth = st.sidebar.slider("Terminal Growth", 0.0, 0.05, 0.03)

capex_pct = st.sidebar.slider("Capex %", 0.0, 0.20, 0.05)
wc_pct = st.sidebar.slider("WC %", 0.0, 0.20, 0.05)

entry_multiple = st.sidebar.number_input("Entry Multiple", value=10.0)
exit_multiple = st.sidebar.number_input("Exit Multiple", value=12.0)
debt_pct = st.sidebar.slider("Debt %", 0.0, 0.80, 0.60)
interest_rate = st.sidebar.slider("Interest %", 0.0, 0.15, 0.08)

years = st.sidebar.slider("Projection Years", 3, 10, 5)

# ---------- PROJECTIONS ----------
data = []
rev = revenue

for i in range(1, years + 1):
    rev *= (1 + growth)
    ebitda = rev * ebitda_margin
    capex = rev * capex_pct
    wc = rev * wc_pct

    ebit = ebitda
    tax = ebit * tax_rate
    fcf = ebit - tax - capex - wc
    pv = fcf / ((1 + wacc) ** i)

    data.append([i, rev, ebitda, fcf, pv])

df = pd.DataFrame(data, columns=["Year", "Revenue", "EBITDA", "FCF", "PV"])

# ---------- TERMINAL VALUE ----------
terminal_value = (df["FCF"].iloc[-1] * (1 + terminal_growth)) / (wacc - terminal_growth)
pv_terminal = terminal_value / ((1 + wacc) ** years)
enterprise_value = df["PV"].sum() + pv_terminal

# ---------- LBO ----------
entry_ebitda = df["EBITDA"].iloc[0]
entry_ev = entry_ebitda * entry_multiple

debt = entry_ev * debt_pct
equity = entry_ev - debt

debt_balance = debt
cash_flows = [-equity]

for i in range(years):
    interest = debt_balance * interest_rate
    repayment = df["FCF"].iloc[i] - interest
    debt_balance -= max(repayment, 0)

exit_ebitda = df["EBITDA"].iloc[-1]
exit_ev = exit_ebitda * exit_multiple
exit_equity = exit_ev - debt_balance

cash_flows.append(exit_equity)

# ---------- RETURNS ----------
irr = compute_irr(cash_flows)
moic = exit_equity / equity

# ---------- KPI ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Enterprise Value", f"${enterprise_value:,.0f}")
c2.metric("Entry EV", f"${entry_ev:,.0f}")
c3.metric("IRR", f"{irr*100:.2f}%")
c4.metric("MOIC", f"{moic:.2f}x")

# ---------- LAYOUT ----------
left, right = st.columns([2, 1])

with left:
    st.subheader("📈 Financials")
    st.line_chart(df.set_index("Year")[["Revenue", "EBITDA", "FCF"]])
    st.dataframe(df, use_container_width=True)

with right:
    st.subheader("💰 Deal Summary")
    st.write(f"Entry Equity: ${equity:,.0f}")
    st.write(f"Exit Equity: ${exit_equity:,.0f}")
    st.write(f"Debt Remaining: ${debt_balance:,.0f}")

    st.subheader("📉 Cash Flows")
    cf_df = pd.DataFrame({
        "Year": list(range(len(cash_flows))),
        "Cash Flow": cash_flows
    })
    st.bar_chart(cf_df.set_index("Year"))

# ---------- SENSITIVITY ----------
st.subheader("🔥 Sensitivity Analysis (WACC vs Growth)")

wacc_range = np.linspace(wacc - 0.02, wacc + 0.02, 5)
g_range = np.linspace(terminal_growth - 0.01, terminal_growth + 0.01, 5)

base_fcf = df["FCF"].iloc[-1]
heatmap_df = calculate_ev_sensitivity(base_fcf, wacc_range, g_range, years)

heatmap_df = heatmap_df / 1e6  # convert to millions

st.dataframe(
    heatmap_df.style.background_gradient(cmap="Blues"),
    use_container_width=True
)

st.success("✅ App Running Successfully")
