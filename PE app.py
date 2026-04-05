import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide", page_title="PE Valuation Terminal")

# ---------- CUSTOM IRR FUNCTION (NO DEPENDENCY) ----------
def compute_irr(cashflows, guess=0.1):
    rate = guess
    for _ in range(1000):
        npv = sum(cf / (1 + rate) ** i for i, cf in enumerate(cashflows))
        d_npv = sum(-i * cf / (1 + rate) ** (i + 1) for i, cf in enumerate(cashflows))
        rate -= npv / d_npv
    return rate

# ---------- CUSTOM CSS ----------
st.markdown("""
    <style>
    body {
        background-color: #0b0f14;
        color: #e6e6e6;
    }
    .stMetric {
        background-color: #111827;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #1f2937;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.title("📊 Private Equity Valuation Terminal")
st.caption("DCF + LBO | Bloomberg Style Dashboard")

# ---------- SIDEBAR ----------
st.sidebar.header("⚙️ Model Inputs")

revenue = st.sidebar.number_input("Initial Revenue", value=1000.0)
growth = st.sidebar.slider("Growth %", 0.0, 0.30, 0.10)
ebitda_margin = st.sidebar.slider("EBITDA %", 0.0, 0.50, 0.25)
tax_rate = st.sidebar.slider("Tax %", 0.0, 0.40, 0.25)
wacc = st.sidebar.slider("WACC %", 0.0, 0.20, 0.10)
terminal_growth = st.sidebar.slider("Terminal Growth", 0.0, 0.05, 0.03)

capex_pct = st.sidebar.slider("Capex %", 0.0, 0.20, 0.05)
wc_pct = st.sidebar.slider("WC %", 0.0, 0.20, 0.05)

entry_multiple = st.sidebar.number_input("Entry Multiple", value=10.0)
exit_multiple = st.sidebar.number_input("Exit Multiple", value=12.0)
debt_pct = st.sidebar.slider("Debt %", 0.0, 0.80, 0.60)
interest_rate = st.sidebar.slider("Interest %", 0.0, 0.15, 0.08)

years = st.sidebar.slider("Projection Years", 3, 10, 5)

# ---------- CALCULATIONS ----------
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

# ---------- EXIT ----------
exit_ebitda = df["EBITDA"].iloc[-1]
exit_ev = exit_ebitda * exit_multiple
exit_equity = exit_ev - debt_balance

cash_flows.append(exit_equity)

# ---------- RETURNS ----------
irr = compute_irr(cash_flows)
moic = exit_equity / equity

# ---------- KPI ----------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Enterprise Value", f"${enterprise_value:,.0f}")
col2.metric("Entry EV", f"${entry_ev:,.0f}")
col3.metric("IRR", f"{irr*100:.2f}%")
col4.metric("MOIC", f"{moic:.2f}x")

# ---------- LAYOUT ----------
left, right = st.columns([2, 1])

with left:
    st.subheader("📈 Financial Performance")
    st.line_chart(df.set_index("Year")[["Revenue", "EBITDA", "FCF"]])

    st.subheader("📊 Detailed Projections")
    st.dataframe(df, use_container_width=True)

with right:
    st.subheader("💰 Deal Summary")
    st.write(f"**Entry Equity:** ${equity:,.0f}")
    st.write(f"**Exit Equity:** ${exit_equity:,.0f}")
    st.write(f"**Debt Remaining:** ${debt_balance:,.0f}")

    st.subheader("📉 Cash Flows")
    cf_df = pd.DataFrame({
        "Year": list(range(0, years + 1)),
        "Cash Flow": cash_flows
    })
    st.bar_chart(cf_df.set_index("Year"))

st.success("✅ App Running Successfully")
