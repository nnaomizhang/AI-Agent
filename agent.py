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
def validate_industry_input(user_input: str) -> tuple[bool, str, str]:
    text = user_input.strip()
    if not text:
        return False, "", "Please enter an industry before continuing."
    if len(text) < 3:
        return False, "", "Industry input is too short. Please be more specific."
    return True, text, "Industry input accepted."


st.subheader("1) Validate Industry")
industry_input = st.text_input(
    "Enter the industry you want to research",
    placeholder="e.g., electric vehicle charging infrastructure",
)

if st.button("Validate industry"):
    is_valid, industry_name, message = validate_industry_input(industry_input)
    if is_valid:
        st.session_state["industry"] = industry_name
        st.success(message)
        st.info("Proceeding to Step 2: Wikipedia Retrieval.")
    else:
        st.warning(message)
        st.info("Please update your industry input and try again.")

# 2 Wikipedia Retrieval
if "industry" in st.session_state:
    st.subheader("2) Wikipedia Retrieval")
    st.write(f"Selected industry: **{st.session_state['industry']}**")
    if st.button("Retrieve Wikipedia data"):
        try:
            suggestions = wikipedia.search(st.session_state["industry"], results=5)
            if suggestions:
                st.success("Wikipedia retrieval completed.")
                st.write("Top related topics:")
                st.write(", ".join(suggestions[:5]))
                st.session_state["wiki_suggestions"] = suggestions
            else:
                st.warning("No matching Wikipedia topics found. Try refining the industry.")
        except Exception as e:
            st.error(f"Wikipedia retrieval failed: {e}")
else:
    st.subheader("2) Wikipedia Retrieval")
    st.caption("Waiting for a valid industry from Step 1.")

# 3 Generate Report
