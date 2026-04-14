# 📊 Private Equity Valuation Terminal

A Streamlit-based **Private Equity Valuation Dashboard** that combines **DCF (Discounted Cash Flow)** and **LBO (Leveraged Buyout)** analysis in an interactive terminal-style interface.

This project is built for **educational purposes** to demonstrate how private equity professionals evaluate a company using projected financial performance, terminal value assumptions, leverage structure, and return metrics such as **IRR** and **MOIC**.

---

## 🚀 Features

- Interactive **Streamlit dashboard**
- **DCF valuation** using projected free cash flows
- **Terminal value calculation**
- **LBO deal modeling**
- Entry and exit valuation using **EBITDA multiples**
- Debt and equity structuring
- Investor return metrics:
  - **IRR (Internal Rate of Return)**
  - **MOIC (Multiple on Invested Capital)**
- Financial charts and projection tables
- Clean dark-themed valuation terminal layout

---

## 🛠 Tech Stack

- **Python**
- **Streamlit**
- **Pandas**
- **NumPy**

---

## 📌 Project Overview

This app allows users to adjust key private equity deal assumptions from the sidebar and instantly see how valuation and returns change.

The model includes:

### 1. DCF Analysis
Projects:
- Revenue growth
- EBITDA
- Taxes
- Capex
- Working capital
- Free cash flow

Then discounts projected cash flows using **WACC** and calculates **enterprise value** including terminal value.

### 2. LBO Analysis
Simulates a leveraged buyout by:
- Applying an **entry EBITDA multiple**
- Financing part of the deal with **debt**
- Repaying debt using free cash flow
- Applying an **exit EBITDA multiple**
- Calculating sponsor returns at exit

---

## 📷 Dashboard Sections

- **Model Inputs Sidebar**
- **Key Metrics**
  - Enterprise Value
  - Entry EV
  - IRR
  - MOIC
- **Financial Performance Chart**
- **Detailed Projection Table**
- **Deal Summary**
- **Cash Flow Visualization**

---

## ⚙️ User Inputs

The dashboard allows you to control the following assumptions:

- Initial Revenue
- Revenue Growth %
- EBITDA Margin %
- Tax Rate %
- WACC %
- Terminal Growth %
- Capex %
- Working Capital %
- Entry Multiple
- Exit Multiple
- Debt %
- Interest Rate %
- Projection Years

---

## 🧮 Key Financial Logic

### Free Cash Flow
The app estimates free cash flow as:

FCF = EBIT - Tax - Capex - Working Capital

### Terminal Value
Terminal value is calculated using the Gordon Growth formula:

Terminal Value = Final Year FCF × (1 + Terminal Growth) / (WACC - Terminal Growth)

### Entry EV
Entry enterprise value is based on:

Entry EV = Entry EBITDA × Entry Multiple

### Exit EV
Exit enterprise value is based on:

Exit EV = Exit EBITDA × Exit Multiple

### MOIC
MOIC is calculated as:

MOIC = Exit Equity / Entry Equity

### IRR
IRR is estimated using a custom iterative function based on projected cash flows
