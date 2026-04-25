"""
╔══════════════════════════════════════════════════════════════════════════╗
║  NSE Multibagger Screener  v2.0  ·  Powered by Upstox API               ║
║  RS Resilience · 52W High · 21MA · EPS Acceleration · Surprise Factor   ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import warnings
warnings.filterwarnings("ignore")

import time, math, datetime, requests
from typing import Optional

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PAGE CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="Multibagger Screener",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CSS  — Refined dark quantitative terminal aesthetic
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Familjen+Grotesk:wght@400;600;700&display=swap');

:root {
    --bg:       #05090f;
    --surface:  #090f1a;
    --card:     #0d1624;
    --card2:    #111e30;
    --border:   #1a2d45;
    --border2:  #243d5a;
    --accent:   #00d4ff;
    --green:    #06ffa5;
    --red:      #ff4560;
    --gold:     #ffcc00;
    --orange:   #ff8c00;
    --purple:   #b06bff;
    --muted:    #3d5a78;
    --text:     #b8cfe0;
    --texthi:   #ddeeff;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text);
    font-family: 'Familjen Grotesk', sans-serif;
}

/* ── Header ─────────────────────────────────────────────────────── */
.app-header {
    position: relative;
    background: linear-gradient(135deg, #080f1e 0%, #0b1830 60%, #060d18 100%);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 30px 40px 24px;
    margin-bottom: 22px;
    overflow: hidden;
}
.app-header::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent 0%, var(--accent) 30%, var(--green) 70%, transparent 100%);
}
.app-header::after {
    content: 'MULTIBAGGER SCREENER';
    position: absolute; right: 40px; top: 50%; transform: translateY(-50%);
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem; letter-spacing: 4px;
    color: var(--border2); pointer-events: none;
}
.app-header h1 {
    font-family: 'Familjen Grotesk', sans-serif;
    font-weight: 700; font-size: 1.9rem;
    color: var(--texthi); margin: 0; letter-spacing: -0.5px;
}
.app-header .tagline {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem; color: var(--accent);
    margin-top: 7px; letter-spacing: 1.5px; text-transform: uppercase;
}

/* ── Section label ───────────────────────────────────────────────── */
.sec-label {
    font-family: 'DM Mono', monospace; font-size: 0.68rem;
    color: var(--accent); text-transform: uppercase; letter-spacing: 2.5px;
    border-left: 3px solid var(--accent); padding-left: 10px;
    margin: 22px 0 12px;
}

/* ── Metric strip ────────────────────────────────────────────────── */
.kpi-strip { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
.kpi {
    flex: 1; min-width: 120px;
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 14px 18px; text-align: center;
}
.kpi .v { font-family: 'Familjen Grotesk', sans-serif; font-weight: 700; font-size: 1.9rem; line-height: 1; }
.kpi .l { font-family: 'DM Mono', monospace; font-size: 0.63rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1.5px; margin-top: 5px; }
.c-accent  { color: var(--accent); }
.c-green   { color: var(--green); }
.c-gold    { color: var(--gold); }
.c-red     { color: var(--red); }
.c-orange  { color: var(--orange); }
.c-purple  { color: var(--purple); }

/* ── Signal badges ───────────────────────────────────────────────── */
.badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 9px; border-radius: 4px;
    font-family: 'DM Mono', monospace; font-size: 0.67rem; letter-spacing: 0.5px;
}
.b-accel  { background: rgba(255,204,0,0.12);  color: var(--gold);   border: 1px solid rgba(255,204,0,0.3); }
.b-surp   { background: rgba(176,107,255,0.12);color: var(--purple); border: 1px solid rgba(176,107,255,0.3); }
.b-sales  { background: rgba(6,255,165,0.10);  color: var(--green);  border: 1px solid rgba(6,255,165,0.3); }
.b-rs     { background: rgba(0,212,255,0.10);  color: var(--accent); border: 1px solid rgba(0,212,255,0.3); }
.b-bz     { background: rgba(255,140,0,0.12);  color: var(--orange); border: 1px solid rgba(255,140,0,0.3); }
.b-star   { background: rgba(255,69,96,0.12);  color: #ff8c69;       border: 1px solid rgba(255,100,70,0.4); }
.b-perf   { background: rgba(6,255,165,0.10);  color: var(--green);  border: 1px solid rgba(6,255,165,0.3); }

/* ── "Perfect Setup" card ────────────────────────────────────────── */
.perfect-card {
    background: linear-gradient(135deg, #0d1f10, #0a1a1f);
    border: 1px solid rgba(6,255,165,0.25);
    border-radius: 12px; padding: 20px 24px; margin-bottom: 20px;
    position: relative;
}
.perfect-card::before {
    content: '★ PERFECT SETUP';
    position: absolute; top: -10px; left: 20px;
    font-family: 'DM Mono', monospace; font-size: 0.62rem;
    letter-spacing: 2px; color: var(--green);
    background: #0d1f10; padding: 0 8px;
}
.perfect-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }
.perfect-item {
    flex: 1; min-width: 140px;
    background: rgba(0,0,0,0.3); border: 1px solid var(--border);
    border-radius: 8px; padding: 10px 14px;
}
.perfect-item .pi-label { font-family: 'DM Mono', monospace; font-size: 0.62rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; }
.perfect-item .pi-val   { font-size: 0.88rem; font-weight: 600; color: var(--texthi); margin-top: 3px; }

/* ── EPS staircase visual ────────────────────────────────────────── */
.staircase {
    display: flex; align-items: flex-end; gap: 6px;
    height: 56px; padding: 0 4px;
}
.stair {
    flex: 1; border-radius: 4px 4px 0 0; min-width: 28px;
    display: flex; align-items: flex-end; justify-content: center;
    padding-bottom: 3px;
    font-family: 'DM Mono', monospace; font-size: 0.62rem; color: #000;
    font-weight: 600;
}

/* ── Expander ────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
[data-testid="stExpanderDetails"] { background: var(--card) !important; }

/* ── Sidebar ─────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Inputs ──────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background: var(--card) !important; border: 1px solid var(--border) !important;
    color: var(--texthi) !important; border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important; font-size: 0.85rem !important;
}
.stButton > button {
    background: linear-gradient(135deg, #009bb5, #007a90) !important;
    color: #000 !important; font-family: 'Familjen Grotesk', sans-serif !important;
    font-weight: 700 !important; border: none !important; border-radius: 8px !important;
    padding: 11px 24px !important; width: 100% !important;
    letter-spacing: 0.3px !important; transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #00d4ff, #009bb5) !important;
    box-shadow: 0 4px 24px rgba(0,212,255,0.25) !important;
    transform: translateY(-1px) !important;
}
div[data-baseweb="slider"] > div { background: var(--border) !important; }
.stProgress > div > div { background: var(--accent) !important; }
.stTabs [role="tablist"] {
    background: var(--card); border-radius: 10px; padding: 4px;
    border: 1px solid var(--border);
}
.stTabs [role="tab"]         { color: var(--muted) !important; border-radius: 8px; font-family: 'Familjen Grotesk', sans-serif; font-weight: 600; }
.stTabs [aria-selected=true] { background: var(--border2) !important; color: var(--accent) !important; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  FUNDAMENTAL DATA  (Quarterly EPS + Sales — TTM, last 4 quarters)
#  Format: symbol → { "eps": [Q4_oldest→Q1_latest], "sales": [...same],
#                     "eps_est": analyst consensus for upcoming quarter }
#  All ₹ Crore for sales, ₹ per share for EPS.
#  *** UPDATE QUARTERLY after each earnings season ***
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FUNDAMENTALS = {
    # IT
    "TCS":       {"eps": [29.1, 30.9, 32.1, 34.0], "sales": [59162, 60583, 61237, 63973], "eps_est": 35.5},
    "INFY":      {"eps": [14.8, 16.3, 17.5, 20.1], "sales": [37923, 38994, 40135, 40953], "eps_est": 21.2},
    "WIPRO":     {"eps": [5.2,  5.5,  5.9,  6.5],  "sales": [22205, 22208, 22319, 22437], "eps_est": 6.8},
    "HCLTECH":   {"eps": [15.4, 16.2, 18.9, 22.8], "sales": [26700, 27607, 28057, 29890], "eps_est": 23.5},
    "TECHM":     {"eps": [9.2,  10.1, 11.8, 14.2], "sales": [13261, 13510, 13510, 14130], "eps_est": 15.0},
    "LTIM":      {"eps": [42.3, 45.1, 50.2, 58.9], "sales": [8748,  9264,  9435,  9804],  "eps_est": 62.0},
    "MPHASIS":   {"eps": [20.1, 21.3, 23.5, 26.4], "sales": [3461,  3524,  3612,  3838],  "eps_est": 27.5},
    "COFORGE":   {"eps": [17.8, 20.2, 23.9, 28.1], "sales": [1695,  1862,  2106,  2429],  "eps_est": 30.0},
    "PERSISTENT":{"eps": [21.4, 24.8, 30.1, 36.7], "sales": [2143,  2367,  2693,  3039],  "eps_est": 39.5},
    # BANK
    "HDFCBANK":  {"eps": [19.3, 19.8, 21.4, 23.6], "sales": [51729, 55905, 55799, 61642], "eps_est": 24.8},
    "ICICIBANK": {"eps": [12.6, 13.7, 15.1, 17.2], "sales": [32558, 34825, 36039, 38803], "eps_est": 18.5},
    "KOTAKBANK": {"eps": [17.2, 18.1, 19.8, 22.1], "sales": [15321, 16450, 16878, 18201], "eps_est": 23.0},
    "AXISBANK":  {"eps": [14.2, 15.0, 16.8, 18.5], "sales": [26124, 28100, 29069, 31497], "eps_est": 19.5},
    "SBIN":      {"eps": [15.4, 17.2, 19.8, 22.5], "sales": [96519,102000,107500,114000], "eps_est": 23.8},
    "INDUSINDBK":{"eps": [31.2, 33.8, 36.5, 40.2], "sales": [13621, 14521, 15239, 16312], "eps_est": 42.0},
    "BANDHANBNK":{"eps": [3.8,  4.2,  5.1,  5.9],  "sales": [5012,  5234,  5569,  6012],  "eps_est": 6.5},
    "FEDERALBNK":{"eps": [2.9,  3.3,  3.6,  4.1],  "sales": [7124,  7812,  8234,  8912],  "eps_est": 4.5},
    # FMCG
    "HINDUNILVR":{"eps": [9.8,  10.2, 10.8, 11.4], "sales": [15059, 15166, 15283, 15619], "eps_est": 11.8},
    "ITC":       {"eps": [4.2,  4.3,  4.5,  4.7],  "sales": [19601, 18921, 19500, 20100], "eps_est": 4.9},
    "NESTLEIND": {"eps": [68.4, 70.2, 73.1, 77.8], "sales": [5274,  5379,  5478,  5818],  "eps_est": 80.0},
    "BRITANNIA": {"eps": [19.1, 20.5, 22.4, 24.8], "sales": [4019,  4131,  4298,  4512],  "eps_est": 26.0},
    "DABUR":     {"eps": [2.7,  2.8,  2.9,  3.1],  "sales": [3265,  2844,  3019,  3378],  "eps_est": 3.3},
    "MARICO":    {"eps": [2.3,  2.5,  2.7,  2.9],  "sales": [2597,  2367,  2498,  2681],  "eps_est": 3.1},
    # AUTO
    "MARUTI":    {"eps": [96.4, 108.2,128.5,148.3], "sales": [34032, 38001, 39905, 44032], "eps_est": 158.0},
    "TATAMOTORS":{"eps": [11.2, 14.8, 19.4, 25.1], "sales": [104324,108512,112034,119821],"eps_est": 28.0},
    "M&M":       {"eps": [19.4, 22.8, 27.1, 32.4], "sales": [37001, 38124, 41022, 45891], "eps_est": 35.5},
    "BAJAJ-AUTO":{"eps": [55.4, 60.1, 67.8, 76.2], "sales": [11194, 11802, 12410, 13224], "eps_est": 82.0},
    "EICHERMOT": {"eps": [32.1, 35.4, 39.8, 44.2], "sales": [3906,  4124,  4389,  4712],  "eps_est": 47.0},
    "HEROMOTOCO":{"eps": [45.2, 49.8, 55.1, 61.4], "sales": [9212,  9601, 10124, 10891],  "eps_est": 65.0},
    # PHARMA
    "SUNPHARMA": {"eps": [10.4, 11.8, 13.2, 15.1], "sales": [12312, 13012, 13587, 14812], "eps_est": 16.5},
    "DRREDDY":   {"eps": [61.2, 68.5, 77.4, 88.1], "sales": [7021,  7312,  7801,  8234],  "eps_est": 94.0},
    "CIPLA":     {"eps": [11.2, 12.5, 14.1, 16.2], "sales": [6123,  6512,  6891,  7312],  "eps_est": 17.5},
    "DIVISLAB":  {"eps": [17.2, 18.9, 21.4, 24.8], "sales": [1969,  2034,  2201,  2389],  "eps_est": 26.5},
    "AUROPHARMA":{"eps": [12.1, 13.2, 14.8, 16.9], "sales": [6201,  6512,  6891,  7189],  "eps_est": 18.0},
    # ENERGY
    "RELIANCE":  {"eps": [23.8, 24.2, 25.1, 26.8], "sales": [238397,225787,215120,249657],"eps_est": 28.0},
    "ONGC":      {"eps": [7.8,  8.2,  9.1,  10.4], "sales": [147201,152000,143000,158000], "eps_est": 11.0},
    "IOC":       {"eps": [3.8,  4.1,  5.2,  6.1],  "sales": [208000,197000,201000,219000], "eps_est": 6.8},
    "BPCL":      {"eps": [8.4,  9.2,  10.8, 12.1], "sales": [131000,124000,128000,142000], "eps_est": 13.0},
    "POWERGRID": {"eps": [5.4,  5.6,  5.9,  6.3],  "sales": [11210, 11534, 11891, 12312],  "eps_est": 6.6},
    "NTPC":      {"eps": [4.2,  4.5,  4.9,  5.4],  "sales": [42103, 43219, 45012, 47891],  "eps_est": 5.8},
    # METAL
    "TATASTEEL": {"eps": [1.8,  2.4,  3.1,  4.2],  "sales": [58312, 57891, 59012, 62341],  "eps_est": 5.0},
    "HINDALCO":  {"eps": [7.2,  8.1,  9.4,  11.2], "sales": [59124, 57234, 61023, 65891],  "eps_est": 12.5},
    "JSWSTEEL":  {"eps": [8.4,  9.2,  10.8, 12.5], "sales": [43219, 44012, 46891, 49234],  "eps_est": 13.8},
    "SAIL":      {"eps": [1.4,  1.6,  1.9,  2.3],  "sales": [28234, 27891, 29012, 31234],  "eps_est": 2.7},
    "NMDC":      {"eps": [3.2,  3.5,  3.9,  4.5],  "sales": [5912,  5234,  6012,  6891],   "eps_est": 5.0},
}

# Quarter labels (oldest → newest)
Q_LABELS = ["Q1", "Q2", "Q3", "Q4 (Latest)"]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  UNIVERSE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
UNIVERSE = [
    ("TCS",          "TCS",        "NSE_EQ|INE467B01029", "NSE_INDEX|Nifty IT"),
    ("Infosys",      "INFY",       "NSE_EQ|INE009A01021", "NSE_INDEX|Nifty IT"),
    ("Wipro",        "WIPRO",      "NSE_EQ|INE075A01022", "NSE_INDEX|Nifty IT"),
    ("HCL Tech",     "HCLTECH",    "NSE_EQ|INE860A01027", "NSE_INDEX|Nifty IT"),
    ("Tech Mahindra","TECHM",      "NSE_EQ|INE669C01036", "NSE_INDEX|Nifty IT"),
    ("LTIMindtree",  "LTIM",       "NSE_EQ|INE214T01019", "NSE_INDEX|Nifty IT"),
    ("Mphasis",      "MPHASIS",    "NSE_EQ|INE356A01018", "NSE_INDEX|Nifty IT"),
    ("Coforge",      "COFORGE",    "NSE_EQ|INE591G01017", "NSE_INDEX|Nifty IT"),
    ("Persistent",   "PERSISTENT", "NSE_EQ|INE262H01021", "NSE_INDEX|Nifty IT"),
    ("HDFC Bank",    "HDFCBANK",   "NSE_EQ|INE040A01034", "NSE_INDEX|Nifty Bank"),
    ("ICICI Bank",   "ICICIBANK",  "NSE_EQ|INE090A01021", "NSE_INDEX|Nifty Bank"),
    ("Kotak Bank",   "KOTAKBANK",  "NSE_EQ|INE237A01028", "NSE_INDEX|Nifty Bank"),
    ("Axis Bank",    "AXISBANK",   "NSE_EQ|INE238A01034", "NSE_INDEX|Nifty Bank"),
    ("SBI",          "SBIN",       "NSE_EQ|INE062A01020", "NSE_INDEX|Nifty Bank"),
    ("IndusInd Bk",  "INDUSINDBK", "NSE_EQ|INE095A01012", "NSE_INDEX|Nifty Bank"),
    ("Bandhan Bk",   "BANDHANBNK", "NSE_EQ|INE545U01014", "NSE_INDEX|Nifty Bank"),
    ("Federal Bk",   "FEDERALBNK", "NSE_EQ|INE171A01029", "NSE_INDEX|Nifty Bank"),
    ("HUL",          "HINDUNILVR", "NSE_EQ|INE030A01027", "NSE_INDEX|Nifty FMCG"),
    ("ITC",          "ITC",        "NSE_EQ|INE154A01025", "NSE_INDEX|Nifty FMCG"),
    ("Nestle India", "NESTLEIND",  "NSE_EQ|INE239A01016", "NSE_INDEX|Nifty FMCG"),
    ("Britannia",    "BRITANNIA",  "NSE_EQ|INE216A01030", "NSE_INDEX|Nifty FMCG"),
    ("Dabur",        "DABUR",      "NSE_EQ|INE016A01026", "NSE_INDEX|Nifty FMCG"),
    ("Marico",       "MARICO",     "NSE_EQ|INE196A01026", "NSE_INDEX|Nifty FMCG"),
    ("Maruti",       "MARUTI",     "NSE_EQ|INE585B01010", "NSE_INDEX|Nifty Auto"),
    ("Tata Motors",  "TATAMOTORS", "NSE_EQ|INE155L01022", "NSE_INDEX|Nifty Auto"),
    ("M&M",          "M&M",        "NSE_EQ|INE101A01026", "NSE_INDEX|Nifty Auto"),
    ("Bajaj Auto",   "BAJAJ-AUTO", "NSE_EQ|INE917I01010", "NSE_INDEX|Nifty Auto"),
    ("Eicher Motors","EICHERMOT",  "NSE_EQ|INE066A01021", "NSE_INDEX|Nifty Auto"),
    ("Hero MotoCorp","HEROMOTOCO", "NSE_EQ|INE158A01026", "NSE_INDEX|Nifty Auto"),
    ("Sun Pharma",   "SUNPHARMA",  "NSE_EQ|INE044A01036", "NSE_INDEX|Nifty Pharma"),
    ("Dr Reddy's",   "DRREDDY",    "NSE_EQ|INE089A01023", "NSE_INDEX|Nifty Pharma"),
    ("Cipla",        "CIPLA",      "NSE_EQ|INE059A01026", "NSE_INDEX|Nifty Pharma"),
    ("Divi's Labs",  "DIVISLAB",   "NSE_EQ|INE361B01024", "NSE_INDEX|Nifty Pharma"),
    ("Aurobindo",    "AUROPHARMA", "NSE_EQ|INE406A01037", "NSE_INDEX|Nifty Pharma"),
    ("Reliance",     "RELIANCE",   "NSE_EQ|INE002A01018", "NSE_INDEX|Nifty Energy"),
    ("ONGC",         "ONGC",       "NSE_EQ|INE213A01029", "NSE_INDEX|Nifty Energy"),
    ("IOC",          "IOC",        "NSE_EQ|INE242A01010", "NSE_INDEX|Nifty Energy"),
    ("BPCL",         "BPCL",       "NSE_EQ|INE029A01011", "NSE_INDEX|Nifty Energy"),
    ("Power Grid",   "POWERGRID",  "NSE_EQ|INE752E01010", "NSE_INDEX|Nifty Energy"),
    ("NTPC",         "NTPC",       "NSE_EQ|INE733E01010", "NSE_INDEX|Nifty Energy"),
    ("Tata Steel",   "TATASTEEL",  "NSE_EQ|INE081A01020", "NSE_INDEX|Nifty Metal"),
    ("Hindalco",     "HINDALCO",   "NSE_EQ|INE038A01020", "NSE_INDEX|Nifty Metal"),
    ("JSW Steel",    "JSWSTEEL",   "NSE_EQ|INE019A01038", "NSE_INDEX|Nifty Metal"),
    ("SAIL",         "SAIL",       "NSE_EQ|INE114A01011", "NSE_INDEX|Nifty Metal"),
    ("NMDC",         "NMDC",       "NSE_EQ|INE584A01023", "NSE_INDEX|Nifty Metal"),
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  UPSTOX API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BASE = "https://api.upstox.com/v2"

def _hdr(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}


def upstox_hist(ikey: str, from_d: str, to_d: str, token: str) -> Optional[pd.DataFrame]:
    url = f"{BASE}/historical-candle/{ikey}/day/{to_d}/{from_d}"
    try:
        r = requests.get(url, headers=_hdr(token), timeout=15)
        r.raise_for_status()
        candles = r.json().get("data", {}).get("candles", [])
        if not candles:
            return None
        df = pd.DataFrame(candles,
                          columns=["timestamp","open","high","low","close","volume","oi"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)
        df.rename(columns={"open":"Open","high":"High","low":"Low",
                            "close":"Close","volume":"Volume"}, inplace=True)
        return df
    except Exception as e:
        return None


def upstox_ltp(ikey: str, token: str) -> Optional[float]:
    try:
        r = requests.get(f"{BASE}/market-quote/quotes",
                         headers=_hdr(token),
                         params={"instrument_key": ikey}, timeout=8)
        r.raise_for_status()
        data = r.json().get("data", {})
        for v in data.values():
            ltp = v.get("last_price") or v.get("ltp")
            if ltp:
                return float(ltp)
    except Exception:
        pass
    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  EPS INTELLIGENCE ENGINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def eps_qoq_growths(eps_list: list) -> list[float]:
    """Quarter-on-quarter growth rates (Q1→Q2, Q2→Q3, Q3→Q4)."""
    growths = []
    for i in range(1, len(eps_list)):
        prev = eps_list[i - 1]
        curr = eps_list[i]
        if prev and prev > 0:
            growths.append((curr - prev) / prev * 100)
        else:
            growths.append(0.0)
    return growths


def eps_yoy_growth(eps_list: list) -> Optional[float]:
    """YoY growth: Q4 vs Q1 (approximately one year apart for 4-quarter data)."""
    if len(eps_list) < 4:
        return None
    q1, q4 = eps_list[0], eps_list[-1]
    if q1 and q1 > 0:
        return (q4 - q1) / q1 * 100
    return None


def eps_acceleration_score(growths: list[float]) -> dict:
    """
    Detect staircase pattern: each QoQ growth should be HIGHER than previous.
    Returns score 0-100 and human verdict.
    """
    if len(growths) < 2:
        return {"score": 0, "verdict": "Insufficient data", "accelerating": False}

    staircase_steps = sum(1 for i in range(1, len(growths)) if growths[i] > growths[i-1])
    max_steps = len(growths) - 1
    score = round(staircase_steps / max_steps * 100) if max_steps else 0

    # Check if latest growth is highest
    is_latest_peak = growths[-1] == max(growths)
    all_positive    = all(g > 0 for g in growths)
    accelerating    = score >= 50 and is_latest_peak and all_positive

    if accelerating and score == 100:
        verdict = "🚀 Perfect Staircase — Parabolic Risk!"
    elif accelerating:
        verdict = "📈 Accelerating EPS"
    elif all_positive:
        verdict = "✅ Consistent Growth"
    elif staircase_steps > 0:
        verdict = "⚠️ Mixed Acceleration"
    else:
        verdict = "❌ Decelerating"

    return {"score": score, "verdict": verdict, "accelerating": accelerating,
            "is_latest_peak": is_latest_peak, "all_positive": all_positive}


def surprise_factor(actual_latest: float, estimate: Optional[float]) -> dict:
    """How much did actual beat analyst estimate?"""
    if not estimate or estimate <= 0:
        return {"beat_pct": None, "verdict": "No estimate", "positive": False}
    beat = (actual_latest - estimate) / abs(estimate) * 100
    if beat >= 20:
        verdict = "🎯 Massive Beat (>20%)"
        positive = True
    elif beat >= 10:
        verdict = "✅ Strong Beat (>10%)"
        positive = True
    elif beat >= 3:
        verdict = "👍 Beat (>3%)"
        positive = True
    elif beat >= -3:
        verdict = "≈ In Line"
        positive = False
    else:
        verdict = "❌ Miss"
        positive = False
    return {"beat_pct": round(beat, 1), "verdict": verdict, "positive": positive}


def sales_vs_eps_quality(eps_list: list, sales_list: list) -> dict:
    """
    Rule: EPS growth AND Sales growth together = quality.
    EPS up + Sales flat = cost-cutting (low quality).
    """
    if len(eps_list) < 4 or len(sales_list) < 4:
        return {"grade": "N/A", "verdict": "Insufficient data", "quality": False}

    eps_growth   = (eps_list[-1]   - eps_list[0])   / abs(eps_list[0])   * 100 if eps_list[0]   else 0
    sales_growth = (sales_list[-1] - sales_list[0]) / abs(sales_list[0]) * 100 if sales_list[0] else 0

    # Determine quality grade
    if eps_growth >= 20 and sales_growth >= 15:
        grade   = "A+"
        verdict = "🏆 Organic Growth — EPS + Sales both expanding"
        quality = True
    elif eps_growth >= 15 and sales_growth >= 8:
        grade   = "A"
        verdict = "✅ Strong Organic Growth"
        quality = True
    elif eps_growth >= 10 and sales_growth >= 5:
        grade   = "B"
        verdict = "👍 Decent Growth Quality"
        quality = True
    elif eps_growth >= 10 and sales_growth < 3:
        grade   = "C"
        verdict = "⚠️ Cost Cutting — EPS up but Sales flat"
        quality = False
    elif eps_growth < 0:
        grade   = "D"
        verdict = "❌ EPS Declining"
        quality = False
    else:
        grade   = "B-"
        verdict = "↗ Moderate — monitor revenue trend"
        quality = False

    return {
        "grade": grade, "verdict": verdict, "quality": quality,
        "eps_growth_pct": round(eps_growth, 1),
        "sales_growth_pct": round(sales_growth, 1)
    }


def analyse_fundamentals(sym: str, current_price: float) -> dict:
    """Full EPS intelligence block for one symbol."""
    fd = FUNDAMENTALS.get(sym)
    if not fd:
        return {"available": False}

    eps   = fd["eps"]    # list of 4 quarterly EPS (oldest first)
    sales = fd["sales"]  # list of 4 quarterly Sales
    est   = fd.get("eps_est")

    ttm_eps = sum(eps)
    pe      = round(current_price / ttm_eps, 1) if ttm_eps > 0 else None

    qoq   = eps_qoq_growths(eps)
    yoy   = eps_yoy_growth(eps)
    accel = eps_acceleration_score(qoq)
    surp  = surprise_factor(eps[-1], est)
    qual  = sales_vs_eps_quality(eps, sales)

    # "Perfect Setup" fundamental score (0-100)
    score = 0
    if yoy and yoy >= 20:          score += 35
    elif yoy and yoy >= 10:        score += 20
    if accel["accelerating"]:      score += 25
    if surp["positive"]:           score += 20
    if qual["quality"]:            score += 20
    score = min(score, 100)

    return {
        "available": True, "eps": eps, "sales": sales,
        "ttm_eps": round(ttm_eps, 2), "pe": pe,
        "qoq_growths": [round(g, 1) for g in qoq],
        "yoy_growth": round(yoy, 1) if yoy else None,
        "accel": accel, "surprise": surp, "quality": qual,
        "eps_estimate": est,
        "fundamental_score": score,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TECHNICAL HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def perf_n(series: pd.Series, n: int) -> Optional[float]:
    if len(series) < n + 1:
        return None
    s, e = float(series.iloc[-(n+1)]), float(series.iloc[-1])
    return (e - s) / s * 100 if s else None


def rsi14(series: pd.Series) -> float:
    d = series.diff()
    g = d.clip(lower=0).rolling(14).mean()
    l = (-d.clip(upper=0)).rolling(14).mean()
    rs = g / l.replace(0, np.nan)
    r = 100 - (100 / (1 + rs))
    return float(r.iloc[-1]) if not r.empty else float("nan")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN SCREENER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_screen(token: str, cfg: dict, prog=None) -> pd.DataFrame:
    today   = datetime.date.today()
    to_d    = today.strftime("%Y-%m-%d")
    from_d  = (today - datetime.timedelta(days=420)).strftime("%Y-%m-%d")

    sec_cache = {}
    rows = []
    n = len(UNIVERSE)

    for i, (name, sym, ikey, skey) in enumerate(UNIVERSE):
        if prog:
            prog(i / n, f"[{i+1}/{n}]  {name}  ({sym})")

        df = upstox_hist(ikey, from_d, to_d, token)
        if df is None or len(df) < 30:
            continue

        avg_vol = df["Volume"].tail(20).mean()
        if avg_vol < cfg["min_vol"]:
            continue

        live = upstox_ltp(ikey, token)
        price = live if live else float(df["Close"].iloc[-1])

        # F1: 52W High
        h52   = df["High"].tail(252).max()
        d_h52 = (price - h52) / h52 * 100
        if d_h52 < -cfg["high_prox"]:
            continue

        # Sector
        if skey not in sec_cache:
            sec_cache[skey] = upstox_hist(skey, from_d, to_d, token)
            time.sleep(0.15)
        sec_df = sec_cache[skey]
        if sec_df is None or len(sec_df) < cfg["rs_days"] + 2:
            continue

        # F2: RS Resilience
        sp  = perf_n(df["Close"],  cfg["rs_days"])
        xp  = perf_n(sec_df["Close"], cfg["rs_days"])
        if sp is None or xp is None:
            continue
        rs_leader = xp < cfg["sec_drop"] and sp >= cfg["stk_min"]

        # F3: 21MA
        sma21  = float(df["Close"].tail(21).mean())
        d_sma  = (price - sma21) / sma21 * 100
        in_bz  = cfg["bz_lo"] <= d_sma <= cfg["bz_hi"]

        rsi_v  = rsi14(df["Close"])

        # F4: EPS Intelligence
        fund   = analyse_fundamentals(sym, price)
        ttm    = fund.get("ttm_eps") or 0
        pe     = fund.get("pe")
        yoy_g  = fund.get("yoy_growth")
        fscore = fund.get("fundamental_score", 0)

        eps_ok   = ttm >= cfg["min_eps"]
        yoy_ok   = yoy_g is not None and yoy_g >= cfg["min_yoy"]
        accel_ok = fund.get("accel", {}).get("accelerating", False) if fund["available"] else False
        surp_ok  = fund.get("surprise", {}).get("positive", False)  if fund["available"] else False
        qual_ok  = fund.get("quality",  {}).get("quality",  False)  if fund["available"] else False

        # Perfect Setup: all signals green
        perfect = (rs_leader and in_bz and eps_ok and yoy_ok and accel_ok)

        rows.append({
            "Name": name, "Symbol": sym,
            "Sector": skey.replace("NSE_INDEX|Nifty ", ""),
            "Price (₹)": round(price, 2),
            "52W High": round(h52, 2),
            "Dist 52W %": round(d_h52, 2),
            f"Stk {cfg['rs_days']}d %": round(sp, 2),
            f"Sec {cfg['rs_days']}d %": round(xp, 2),
            "RS Leader": rs_leader,
            "21 SMA": round(sma21, 2),
            "Dist 21SMA %": round(d_sma, 2),
            "Buy Zone": in_bz,
            "RSI": round(rsi_v, 1) if not math.isnan(rsi_v) else None,
            "EPS TTM ₹": fund.get("ttm_eps"),
            "P/E": pe,
            "YoY EPS %": yoy_g,
            "EPS Accel": accel_ok,
            "Surp Beat": surp_ok,
            "Sales+EPS": qual_ok,
            "Fund Score": fscore,
            "⭐ Perfect": perfect,
            "_fund": fund,
            "_eps_list": fund.get("eps", []),
            "_sales_list": fund.get("sales", []),
            "_qoq": fund.get("qoq_growths", []),
            "_accel": fund.get("accel", {}),
            "_surp": fund.get("surprise", {}),
            "_qual": fund.get("quality", {}),
        })
        time.sleep(0.12)

    if prog:
        prog(1.0, "Scan complete ✓")
    return pd.DataFrame(rows)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CHART HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BG  = "#05090f"
PBG = "#090f1a"
GRD = "#1a2d45"
ACC = "#00d4ff"
GRN = "#06ffa5"
RED = "#ff4560"
GLD = "#ffcc00"
ORG = "#ff8c00"
PUR = "#b06bff"
MUT = "#3d5a78"
TXT = "#b8cfe0"

def _base(title=""):
    return dict(
        title=dict(text=title, font=dict(color=TXT, size=13, family="Familjen Grotesk")),
        paper_bgcolor=PBG, plot_bgcolor=BG,
        font=dict(color=TXT, family="DM Mono"),
        xaxis=dict(gridcolor=GRD, tickcolor=MUT, linecolor=GRD, tickfont=dict(size=10)),
        yaxis=dict(gridcolor=GRD, tickcolor=MUT, linecolor=GRD, tickfont=dict(size=10)),
        margin=dict(l=44, r=16, t=48, b=40),
    )


def chart_eps_staircase(row: pd.Series) -> go.Figure:
    eps   = row["_eps_list"]
    sales = row["_sales_list"]
    qoq   = row["_qoq"]

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["EPS Staircase (₹/share)", "Sales Trend (₹ Cr)"],
                        horizontal_spacing=0.12)

    # EPS bars with gradient coloring
    colors = [GRN if i == len(eps)-1 else ACC for i in range(len(eps))]
    fig.add_trace(go.Bar(
        x=Q_LABELS, y=eps,
        marker_color=colors,
        text=[f"₹{v:.1f}" for v in eps],
        textposition="outside", textfont=dict(size=10, color=TXT),
        name="EPS",
    ), row=1, col=1)

    # QoQ growth annotations
    for i, g in enumerate(qoq):
        color = GRN if g > 0 else RED
        arrow = "↑" if g > 0 else "↓"
        fig.add_annotation(
            x=Q_LABELS[i+1], y=eps[i+1],
            text=f"{arrow}{abs(g):.0f}%",
            showarrow=False, yshift=22,
            font=dict(size=9, color=color, family="DM Mono"),
            row=1, col=1,
        )

    # Sales line
    s_colors = [GLD if i == len(sales)-1 else ORG for i in range(len(sales))]
    fig.add_trace(go.Bar(
        x=Q_LABELS, y=sales,
        marker_color=[f"rgba(255,140,0,{0.4+0.15*i})" for i in range(len(sales))],
        name="Sales",
        text=[f"₹{v/1000:.0f}K Cr" if v > 10000 else f"₹{v:.0f} Cr" for v in sales],
        textposition="outside", textfont=dict(size=9, color=TXT),
    ), row=1, col=2)

    fig.update_layout(**_base(f"{row['Name']} — EPS & Sales Trend"))
    fig.update_layout(showlegend=False, height=320)
    for i in [1, 2]:
        fig.update_xaxes(gridcolor=GRD, linecolor=GRD, tickfont=dict(size=9), row=1, col=i)
        fig.update_yaxes(gridcolor=GRD, linecolor=GRD, tickfont=dict(size=9), row=1, col=i)
    return fig


def chart_rs_scatter(df: pd.DataFrame, stk_col: str, sec_col: str) -> go.Figure:
    def clr(row):
        if row["⭐ Perfect"]:   return GLD
        if row["RS Leader"]:    return GRN
        return MUT

    def sym(row):
        if row["⭐ Perfect"]:   return "star"
        if row["RS Leader"]:    return "diamond"
        return "circle"

    fig = go.Figure()
    fig.add_vline(x=0,              line=dict(color=GRD, dash="dot", width=1))
    fig.add_hline(y=-3,             line=dict(color=RED, dash="dot", width=1))
    fig.add_shape(type="rect", x0=0, x1=50, y0=-50, y1=-3,
                  fillcolor="rgba(6,255,165,0.03)", line_width=0)

    fig.add_trace(go.Scatter(
        x=df[stk_col], y=df[sec_col],
        mode="markers+text",
        marker=dict(size=11, color=[clr(r) for _, r in df.iterrows()],
                    symbol=[sym(r) for _, r in df.iterrows()],
                    line=dict(color="#000", width=0.5),
                    opacity=0.9),
        text=df["Symbol"],
        textposition="top center",
        textfont=dict(size=8, color=TXT),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Stock: %{x:.1f}%<br>Sector: %{y:.1f}%<br><extra></extra>"
        ),
    ))
    lay = _base("RS Map: Stock vs Sector Performance")
    lay["xaxis"]["title"] = dict(text=f"Stock {stk_col}", font=dict(size=11))
    lay["yaxis"]["title"] = dict(text=f"Sector {sec_col}", font=dict(size=11))
    lay["height"] = 480
    fig.update_layout(**lay)
    return fig


def chart_fund_scores(df: pd.DataFrame) -> go.Figure:
    dv = df.sort_values("Fund Score", ascending=True).tail(20)
    colors = [GLD if p else (GRN if s >= 60 else (ACC if s >= 40 else MUT))
              for p, s in zip(dv["⭐ Perfect"], dv["Fund Score"])]
    fig = go.Figure(go.Bar(
        y=dv["Symbol"], x=dv["Fund Score"],
        orientation="h",
        marker_color=colors,
        text=[f"{s}" for s in dv["Fund Score"]],
        textposition="outside", textfont=dict(size=9, color=TXT),
        hovertemplate="<b>%{y}</b><br>Fund Score: %{x}<extra></extra>",
    ))
    fig.add_vline(x=60, line=dict(color=GRN, dash="dot", width=1))
    lay = _base("Fundamental Quality Score (0–100)")
    lay["height"] = 480
    lay["xaxis"]["range"] = [0, 115]
    fig.update_layout(**lay)
    return fig


def chart_pe_bubble(df: pd.DataFrame) -> go.Figure:
    dv = df.dropna(subset=["P/E", "YoY EPS %"])
    colors = [GLD if p else (GRN if q else MUT)
              for p, q in zip(dv["⭐ Perfect"], dv["Sales+EPS"])]
    fig = go.Figure(go.Scatter(
        x=dv["YoY EPS %"], y=dv["P/E"],
        mode="markers+text",
        marker=dict(size=10, color=colors, line=dict(color="#000", width=0.5)),
        text=dv["Symbol"],
        textposition="top center", textfont=dict(size=8, color=TXT),
        hovertemplate="<b>%{text}</b><br>YoY EPS: %{x:.1f}%<br>P/E: %{y:.1f}x<extra></extra>",
    ))
    lay = _base("P/E vs YoY EPS Growth — Value vs Growth Map")
    lay["xaxis"]["title"] = dict(text="YoY EPS Growth %", font=dict(size=11))
    lay["yaxis"]["title"] = dict(text="P/E Ratio", font=dict(size=11))
    lay["height"] = 420
    fig.update_layout(**lay)
    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  EPS STAIRCASE HTML MINI-WIDGET
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def staircase_html(eps: list, qoq: list) -> str:
    if not eps:
        return ""
    max_e = max(eps) if max(eps) > 0 else 1
    bars  = ""
    for i, (e, label) in enumerate(zip(eps, Q_LABELS)):
        pct     = max(int(e / max_e * 100), 8)
        is_last = i == len(eps) - 1
        clr     = "#06ffa5" if is_last else "#00d4ff"
        if i > 0:
            g = qoq[i-1]
            arrow = f"<span style='color:{'#06ffa5' if g>0 else '#ff4560'};font-size:9px;'>{'▲' if g>0 else '▼'}{abs(g):.0f}%</span>"
        else:
            arrow = ""
        bars += (
            f"<div style='display:flex;flex-direction:column;align-items:center;flex:1;'>"
            f"  {arrow}"
            f"  <div style='height:{pct}%;background:{clr};width:100%;border-radius:4px 4px 0 0;"
            f"              display:flex;align-items:center;justify-content:center;"
            f"              font-family:DM Mono,monospace;font-size:9px;color:#000;font-weight:600;'>"
            f"    ₹{e:.1f}"
            f"  </div>"
            f"  <div style='font-size:8px;color:#3d5a78;margin-top:2px;white-space:nowrap;'>{label}</div>"
            f"</div>"
        )
    return (
        f"<div style='display:flex;align-items:flex-end;gap:4px;height:72px;"
        f"background:rgba(0,0,0,0.2);border-radius:6px;padding:4px 6px 0;'>"
        f"{bars}</div>"
    )


def badge_row(row: pd.Series) -> str:
    badges = []
    if row.get("RS Leader"):
        badges.append('<span class="badge b-rs">RS LEADER</span>')
    if row.get("Buy Zone"):
        badges.append('<span class="badge b-bz">BUY ZONE</span>')
    if row.get("EPS Accel"):
        badges.append('<span class="badge b-accel">EPS ACCEL</span>')
    if row.get("Surp Beat"):
        badges.append('<span class="badge b-surp">BEAT EST</span>')
    if row.get("Sales+EPS"):
        badges.append('<span class="badge b-sales">SALES+EPS</span>')
    if row.get("⭐ Perfect"):
        badges.append('<span class="badge b-star">⭐ PERFECT SETUP</span>')
    return " ".join(badges)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN APP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    # Header
    st.markdown("""
    <div class="app-header">
      <h1>🚀 NSE Multibagger Screener</h1>
      <div class="tagline">
        EPS Acceleration · Surprise Factor · Sales Quality · RS Resilience · 21MA Buy Zone
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ───────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="sec-label">🔑 Upstox Token</div>', unsafe_allow_html=True)
        token = st.text_input("Access Token", type="password",
                              placeholder="Bearer token from Upstox Developer Console…")
        st.markdown("""
        <div style='font-family:DM Mono,monospace;font-size:0.68rem;color:#3d5a78;
                    line-height:1.7;margin-top:-6px;margin-bottom:14px;'>
        ① upstox.com/developer → Your App<br>
        ② Complete OAuth2 auth flow<br>
        ③ Copy the access_token value<br>
        ④ Token valid for 1 trading day
        </div>""", unsafe_allow_html=True)

        st.divider()
        st.markdown('<div class="sec-label">📊 EPS Filters</div>', unsafe_allow_html=True)
        min_eps   = st.number_input("Min TTM EPS (₹)", 0.0, value=8.0, step=2.0)
        min_yoy   = st.slider("Min YoY EPS Growth (%)", 0, 100, 20)
        req_accel = st.checkbox("Must have EPS Acceleration", value=True)
        req_surp  = st.checkbox("Must have Analyst Beat", value=False)
        req_qual  = st.checkbox("Must have Sales + EPS growth", value=True)

        st.divider()
        st.markdown('<div class="sec-label">📈 Technical Filters</div>', unsafe_allow_html=True)
        rs_days   = st.slider("RS Lookback (days)", 5, 30, 20)
        high_prox = st.slider("Max Dist 52W High (%)", 1.0, 10.0, 2.0, 0.5)
        sec_drop  = st.slider("Sector Drop Threshold (%)", -10.0, -1.0, -3.0, 0.5)
        stk_min   = st.slider("Stock Min Return (%)", -2.0, 5.0, 0.0, 0.5)
        bz_lo     = st.slider("21MA BuyZone Lower (%)", -3.0, 0.0, 0.0, 0.5)
        bz_hi     = st.slider("21MA BuyZone Upper (%)", 0.5, 5.0, 1.5, 0.5)
        min_vol   = st.number_input("Min Avg Volume", 10000, value=100000, step=10000)

        st.divider()
        run_btn   = st.button("🚀  RUN FULL SCAN", use_container_width=True)

    cfg = dict(
        rs_days=rs_days, high_prox=high_prox, sec_drop=sec_drop,
        stk_min=stk_min, bz_lo=bz_lo, bz_hi=bz_hi,
        min_eps=min_eps, min_yoy=min_yoy,
        req_accel=req_accel, req_surp=req_surp, req_qual=req_qual,
        min_vol=int(min_vol),
    )

    if "df" not in st.session_state:
        st.session_state.df = None

    # ── No token ──────────────────────────────────────────────────────
    if not token and not st.session_state.df:
        st.markdown('<div class="sec-label">📖 The Three EPS Rules for Multibaggers</div>',
                    unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
            <div style='background:#0d1624;border:1px solid #1a2d45;border-radius:10px;padding:18px;height:100%;'>
            <div style='font-family:DM Mono,monospace;font-size:0.62rem;color:#ffcc00;
                        letter-spacing:2px;margin-bottom:8px;'>RULE 1</div>
            <div style='font-size:1rem;font-weight:700;color:#ddeeff;margin-bottom:8px;'>
              📈 EPS Acceleration</div>
            <div style='font-size:0.82rem;color:#b8cfe0;line-height:1.6;'>
              Look for a <strong>staircase pattern</strong>. If Q1 growth was 10%, Q2 was 20%, Q3 is 40% — 
              the stock is likely to enter a <strong>parabolic run</strong>. Each quarter should beat the last.
            </div>
            <div style='margin-top:12px;font-family:DM Mono,monospace;font-size:0.7rem;color:#06ffa5;'>
              10% → 20% → 40% = 🚀 Parabolic signal
            </div>
            </div>""", unsafe_allow_html=True)

        with c2:
            st.markdown("""
            <div style='background:#0d1624;border:1px solid #1a2d45;border-radius:10px;padding:18px;height:100%;'>
            <div style='font-family:DM Mono,monospace;font-size:0.62rem;color:#b06bff;
                        letter-spacing:2px;margin-bottom:8px;'>RULE 2</div>
            <div style='font-size:1rem;font-weight:700;color:#ddeeff;margin-bottom:8px;'>
              🎯 The Surprise Factor</div>
            <div style='font-size:0.82rem;color:#b8cfe0;line-height:1.6;'>
              The biggest multibaggers occur when a company reports EPS <strong>much higher 
              than analysts expected</strong>. A 20%+ beat forces a swift institutional re-rating.
            </div>
            <div style='margin-top:12px;font-family:DM Mono,monospace;font-size:0.7rem;color:#b06bff;'>
              Actual > Estimate by 20% = 🎯 Re-rating fuel
            </div>
            </div>""", unsafe_allow_html=True)

        with c3:
            st.markdown("""
            <div style='background:#0d1624;border:1px solid #1a2d45;border-radius:10px;padding:18px;height:100%;'>
            <div style='font-family:DM Mono,monospace;font-size:0.62rem;color:#06ffa5;
                        letter-spacing:2px;margin-bottom:8px;'>RULE 3</div>
            <div style='font-size:1rem;font-weight:700;color:#ddeeff;margin-bottom:8px;'>
              🏆 Sales vs EPS Quality</div>
            <div style='font-size:0.82rem;color:#b8cfe0;line-height:1.6;'>
              If EPS grows but Sales are flat — it's just <strong>cost cutting</strong>, not real growth. 
              True multibaggers have <strong>both Sales and EPS expanding together</strong>.
            </div>
            <div style='margin-top:12px;font-family:DM Mono,monospace;font-size:0.7rem;color:#06ffa5;'>
              Sales ↑ + EPS ↑ = 🏆 Organic growth
            </div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sec-label" style="margin-top:28px;">⭐ The Perfect Setup</div>',
                    unsafe_allow_html=True)
        st.markdown("""
        <div class="perfect-card">
          <div class="perfect-row">
            <div class="perfect-item">
              <div class="pi-label">Sector</div>
              <div class="pi-val">Sideways / Falling 4–5%</div>
            </div>
            <div class="perfect-item">
              <div class="pi-label">Stock Price</div>
              <div class="pi-val">Holding near 52W High, hugging 21MA</div>
            </div>
            <div class="perfect-item">
              <div class="pi-label">EPS Growth</div>
              <div class="pi-val">&gt;20% YoY, Accelerating</div>
            </div>
            <div class="perfect-item">
              <div class="pi-label">Sales Quality</div>
              <div class="pi-val">Revenue expanding with EPS</div>
            </div>
            <div class="perfect-item">
              <div class="pi-label">Trigger / Action</div>
              <div class="pi-val">When sector turns up → Buy the breakout</div>
            </div>
          </div>
          <div style='margin-top:14px;font-family:DM Mono,monospace;font-size:0.72rem;color:#3d5a78;'>
            This is the highest probability setup in the stock market. 
            The stock holds because smart money is already loaded. The sector weakness is the entry gift.
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.info("🔑 Paste your **Upstox Access Token** in the sidebar, then click **RUN FULL SCAN**.")
        return

    # ── Run scan ──────────────────────────────────────────────────────
    if run_btn:
        if not token.strip():
            st.error("⚠️  Please enter your Upstox access token.")
            return
        pb  = st.progress(0.0)
        ptx = st.empty()

        def prog(pct, msg):
            pb.progress(min(pct, 1.0))
            ptx.markdown(
                f'<p style="font-family:DM Mono,monospace;font-size:0.72rem;'
                f'color:#3d5a78;">{msg}</p>', unsafe_allow_html=True)

        with st.spinner("Connecting to Upstox API…"):
            df = run_screen(token.strip(), cfg, prog)

        pb.empty(); ptx.empty()
        if df.empty:
            st.warning("No stocks passed the filters. Try relaxing the thresholds.")
            return
        st.session_state.df  = df
        st.session_state.cfg = cfg

    df = st.session_state.get("df")
    if df is None:
        return
    cfg_u   = st.session_state.get("cfg", cfg)
    sc      = f"Stk {cfg_u['rs_days']}d %"
    xc      = f"Sec {cfg_u['rs_days']}d %"

    # ── KPI strip ─────────────────────────────────────────────────────
    tot   = len(df)
    rs_n  = int(df["RS Leader"].sum())
    bz_n  = int(df["Buy Zone"].sum())
    ac_n  = int(df["EPS Accel"].sum())
    su_n  = int(df["Surp Beat"].sum())
    pf_n  = int(df["⭐ Perfect"].sum())

    st.markdown(
        f'<div class="kpi-strip">'
        f'<div class="kpi"><div class="v c-accent">{tot}</div><div class="l">Screened</div></div>'
        f'<div class="kpi"><div class="v c-green">{rs_n}</div><div class="l">RS Leaders</div></div>'
        f'<div class="kpi"><div class="v c-accent">{bz_n}</div><div class="l">Buy Zone</div></div>'
        f'<div class="kpi"><div class="v c-gold">{ac_n}</div><div class="l">EPS Accel</div></div>'
        f'<div class="kpi"><div class="v c-purple">{su_n}</div><div class="l">Analyst Beat</div></div>'
        f'<div class="kpi"><div class="v c-orange">{pf_n}</div><div class="l">⭐ Perfect</div></div>'
        f'</div>',
        unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "⭐ Perfect Setups", "🔬 EPS Deep Dive",
        "📋 Full Results", "📈 RS Map",
        "📊 Fundamental Charts", "💾 Export"
    ])

    # ── TAB 1: Perfect Setups ─────────────────────────────────────────
    with tab1:
        st.markdown('<div class="sec-label">⭐ Perfect Setups — All 5 Signals Green</div>',
                    unsafe_allow_html=True)
        perfects = df[df["⭐ Perfect"] == True]

        if perfects.empty:
            st.info("No Perfect Setups today. The best RS Leaders with strong fundamentals are shown below.")
            # Show best partial signals
            partial = df.sort_values("Fund Score", ascending=False).head(5)
        else:
            partial = perfects

        for _, row in partial.iterrows():
            is_perf = row["⭐ Perfect"]
            border  = "rgba(255,204,0,0.3)" if is_perf else "rgba(26,45,69,1)"
            bg      = "linear-gradient(135deg,#0d1a10,#0a1520)" if is_perf else "#0d1624"

            with st.expander(
                f"{'⭐' if is_perf else '📌'}  {row['Name']}  ({row['Symbol']})  "
                f"·  ₹{row['Price (₹)']:.2f}  "
                f"·  Fund Score: {row['Fund Score']}/100",
                expanded=is_perf
            ):
                # Badge row
                st.markdown(badge_row(row), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

                # Metrics
                mc1, mc2, mc3, mc4, mc5 = st.columns(5)
                mc1.metric("Price", f"₹{row['Price (₹)']:.2f}")
                mc2.metric("Dist 52W High", f"{row['Dist 52W %']:.2f}%")
                mc3.metric("21SMA Distance", f"{row['Dist 21SMA %']:.2f}%")
                mc4.metric("RSI (14)", f"{row['RSI']}" if row['RSI'] else "—")
                mc5.metric("Fund Score", f"{row['Fund Score']}/100")

                mc6, mc7, mc8, mc9, mc10 = st.columns(5)
                mc6.metric(f"Stock {cfg_u['rs_days']}d Perf", f"{row[sc]:.2f}%")
                mc7.metric(f"Sector {cfg_u['rs_days']}d Perf", f"{row[xc]:.2f}%")
                mc8.metric("EPS TTM", f"₹{row['EPS TTM ₹']}" if row['EPS TTM ₹'] else "—")
                mc9.metric("P/E", f"{row['P/E']}x" if row['P/E'] else "—")
                mc10.metric("YoY EPS Growth", f"{row['YoY EPS %']:.1f}%" if row['YoY EPS %'] else "—")

                # EPS staircase mini-chart
                eps  = row["_eps_list"]
                qoq  = row["_qoq"]
                if eps:
                    st.markdown('<div style="margin-top:8px;">' +
                                staircase_html(eps, qoq) + '</div>',
                                unsafe_allow_html=True)

                # EPS Intelligence panel
                accel = row["_accel"]
                surp  = row["_surp"]
                qual  = row["_qual"]

                ic1, ic2, ic3 = st.columns(3)
                with ic1:
                    st.markdown(f"""
                    <div style='background:#0a1225;border:1px solid #1a2d45;
                                border-radius:8px;padding:12px;'>
                    <div style='font-family:DM Mono,monospace;font-size:0.62rem;
                                color:#ffcc00;letter-spacing:2px;'>EPS ACCELERATION</div>
                    <div style='font-size:0.88rem;margin-top:6px;color:#ddeeff;'>
                      {accel.get('verdict','—')}</div>
                    <div style='font-family:DM Mono,monospace;font-size:0.72rem;
                                color:#3d5a78;margin-top:4px;'>
                      Score: {accel.get('score',0)}/100</div>
                    </div>""", unsafe_allow_html=True)

                with ic2:
                    beat_pct = surp.get('beat_pct')
                    beat_str = f"+{beat_pct}% vs estimate" if beat_pct is not None else "No estimate"
                    st.markdown(f"""
                    <div style='background:#0a1225;border:1px solid #1a2d45;
                                border-radius:8px;padding:12px;'>
                    <div style='font-family:DM Mono,monospace;font-size:0.62rem;
                                color:#b06bff;letter-spacing:2px;'>SURPRISE FACTOR</div>
                    <div style='font-size:0.88rem;margin-top:6px;color:#ddeeff;'>
                      {surp.get('verdict','—')}</div>
                    <div style='font-family:DM Mono,monospace;font-size:0.72rem;
                                color:#3d5a78;margin-top:4px;'>{beat_str}</div>
                    </div>""", unsafe_allow_html=True)

                with ic3:
                    eg = qual.get('eps_growth_pct', 0)
                    sg = qual.get('sales_growth_pct', 0)
                    st.markdown(f"""
                    <div style='background:#0a1225;border:1px solid #1a2d45;
                                border-radius:8px;padding:12px;'>
                    <div style='font-family:DM Mono,monospace;font-size:0.62rem;
                                color:#06ffa5;letter-spacing:2px;'>SALES vs EPS QUALITY</div>
                    <div style='font-size:0.88rem;margin-top:6px;color:#ddeeff;'>
                      {qual.get('verdict','—')}</div>
                    <div style='font-family:DM Mono,monospace;font-size:0.72rem;
                                color:#3d5a78;margin-top:4px;'>
                      EPS: +{eg}%  ·  Sales: +{sg}%</div>
                    </div>""", unsafe_allow_html=True)

    # ── TAB 2: EPS Deep Dive ──────────────────────────────────────────
    with tab2:
        st.markdown('<div class="sec-label">🔬 EPS Deep Dive — All Screened Stocks</div>',
                    unsafe_allow_html=True)

        # Sort by fundamental score descending
        sorted_df = df.sort_values("Fund Score", ascending=False)

        # EPS filter mini-options
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            show_accel = st.checkbox("EPS Accelerating only", value=False)
        with fc2:
            show_beat  = st.checkbox("Analyst Beat only", value=False)
        with fc3:
            show_qual  = st.checkbox("Sales + EPS Quality only", value=False)

        view = sorted_df.copy()
        if show_accel: view = view[view["EPS Accel"] == True]
        if show_beat:  view = view[view["Surp Beat"] == True]
        if show_qual:  view = view[view["Sales+EPS"] == True]

        for _, row in view.iterrows():
            eps   = row["_eps_list"]
            if not eps:
                continue
            accel = row["_accel"]
            surp  = row["_surp"]
            qual  = row["_qual"]

            label = (
                f"{row['Symbol']}  ·  "
                f"YoY EPS: {row['YoY EPS %']:.1f}%  ·  "
                f"Fund: {row['Fund Score']}/100  ·  "
                f"{accel.get('verdict','')}"
            )
            with st.expander(label):
                fig = chart_eps_staircase(row)
                st.plotly_chart(fig, use_container_width=True)

                cc1, cc2, cc3, cc4 = st.columns(4)
                cc1.metric("TTM EPS", f"₹{row['EPS TTM ₹']}")
                cc2.metric("P/E Ratio", f"{row['P/E']}x" if row['P/E'] else "—")
                cc3.metric("Accel Score", f"{accel.get('score',0)}/100")
                cc4.metric("Sales Growth",
                           f"+{qual.get('sales_growth_pct',0):.1f}%")

                # QoQ growth staircase text
                qoq = row["_qoq"]
                if qoq:
                    growing = all(qoq[i] < qoq[i+1] for i in range(len(qoq)-1))
                    arrows  = " → ".join([f"{'↑' if g>0 else '↓'}{abs(g):.0f}%" for g in qoq])
                    color   = "#06ffa5" if growing else "#ff8c00"
                    st.markdown(
                        f'<p style="font-family:DM Mono,monospace;font-size:0.76rem;'
                        f'color:{color};">QoQ: {arrows}</p>',
                        unsafe_allow_html=True)

    # ── TAB 3: Full Results ───────────────────────────────────────────
    with tab3:
        st.markdown('<div class="sec-label">📋 Complete Scan Results</div>',
                    unsafe_allow_html=True)
        display_cols = [
            "Symbol", "Sector", "Price (₹)", "Dist 52W %",
            sc, xc, "RS Leader", "Dist 21SMA %", "Buy Zone",
            "RSI", "EPS TTM ₹", "P/E", "YoY EPS %",
            "EPS Accel", "Surp Beat", "Sales+EPS",
            "Fund Score", "⭐ Perfect"
        ]
        disp = df[display_cols].copy()
        for col in ["RS Leader","Buy Zone","EPS Accel","Surp Beat","Sales+EPS","⭐ Perfect"]:
            disp[col] = disp[col].map({True:"✅", False:"—"})
        disp = disp.sort_values("Fund Score", ascending=False)
        st.dataframe(disp, use_container_width=True, hide_index=True,
                     column_config={
                         "Price (₹)":    st.column_config.NumberColumn(format="₹%.2f"),
                         "EPS TTM ₹":    st.column_config.NumberColumn(format="₹%.1f"),
                         "Fund Score":   st.column_config.ProgressColumn(min_value=0, max_value=100),
                     })

    # ── TAB 4: RS Map ─────────────────────────────────────────────────
    with tab4:
        st.plotly_chart(chart_rs_scatter(df, sc, xc), use_container_width=True)
        st.markdown("""
        <p style='font-family:DM Mono,monospace;font-size:0.7rem;color:#3d5a78;text-align:center;'>
        ⭐ GOLD STAR = Perfect Setup &nbsp;|&nbsp;
        🟢 GREEN = RS Leader &nbsp;|&nbsp;
        Red dashed = Sector –3% threshold &nbsp;|&nbsp;
        Green zone = RS Leader quadrant
        </p>""", unsafe_allow_html=True)

    # ── TAB 5: Fundamental Charts ─────────────────────────────────────
    with tab5:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(chart_fund_scores(df), use_container_width=True)
        with c2:
            st.plotly_chart(chart_pe_bubble(df), use_container_width=True)

    # ── TAB 6: Export ─────────────────────────────────────────────────
    with tab6:
        st.markdown('<div class="sec-label">💾 Export</div>', unsafe_allow_html=True)
        export_cols = [c for c in df.columns if not c.startswith("_")]
        csv = df[export_cols].to_csv(index=False).encode("utf-8")
        ts  = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button("⬇️  Download Full CSV", csv,
                           f"multibagger_scan_{ts}.csv", "text/csv",
                           use_container_width=True)
        perfects = df[df["⭐ Perfect"] == True]
        if not perfects.empty:
            pc = perfects[export_cols].to_csv(index=False).encode("utf-8")
            st.download_button("⭐  Download Perfect Setups Only", pc,
                               f"perfect_setups_{ts}.csv", "text/csv",
                               use_container_width=True)

    # Footer
    st.markdown(
        f'<p style="font-family:DM Mono,monospace;font-size:0.62rem;'
        f'color:#1a2d45;text-align:right;margin-top:32px;">'
        f'Scan: {datetime.datetime.now().strftime("%d %b %Y %H:%M IST")} '
        f'· Upstox V2 · NSE Real-Time · v2.0</p>',
        unsafe_allow_html=True)


if __name__ == "__main__":
    main()
