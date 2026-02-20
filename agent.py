import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import anthropic
import wikipedia
import re
import json
import os

# Page Layout
st.set_page_config(page_title="Market Research Assistant")
st.title("Market Research Assistant")

# Sidebar Settings
st.sidebar.header("Settings")
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
model = st.sidebar.selectbox(
    "Model",
    ["claude-3-5-haiku-latest", "claude-3-5-sonnet-latest"]
)

api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Please enter your Anthropic API key", type="password")

client = anthropic.Anthropic(api_key=api_key) if api_key else None


# 1 Validate the Industry

# 2 Wikipedia Retrieval

# 3 Generate Report
