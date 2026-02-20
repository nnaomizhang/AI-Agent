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

# Initialise client
api_key = st.sidebar.text_input("Please enter your Anthropic API key", type="password")
client = anthropic.Anthropic(api_key=api_key) if api_key else None

# 1 Validate the Industry
def validate_industry(user_input: str) -> tuple[bool, str, str]:
    """Use Claude to check if the user provided a valid industry."""
    if client is None:
        return False, user_input, "Missing ANTHROPIC_API_KEY."

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": (
                f"Does the following text clearly identify a specific industry or market sector? "
                f"Reply with JSON: {{\"valid\": true/false, \"industry\": \"extracted industry name or empty string\", \"reason\": \"brief reason\"}}.\n\n"
                f"Text: {user_input}"
            )
        }]
    )
    text = response.content[0].text.strip()
    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        text = match.group(0)
    data = json.loads(text)
    return data["valid"], data.get("industry", user_input), data.get("reason", "")

st.subheader("1) Validate Industry")
industry_input = st.text_input(
    "Enter the industry or market you want to research",
    placeholder="e.g., electric vehicle charging infrastructure",
)

if st.button("Validate industry"):
    if not industry_input.strip():
        st.error("Please enter an industry first.")
    else:
        with st.spinner("Validating with Claude..."):
            try:
                is_valid, industry_name, reason = validate_industry(industry_input.strip())
                if is_valid:
                    st.success(f"Valid industry: {industry_name}")
                else:
                    st.warning(f"Not a clear industry yet. {reason}")
            except Exception as e:
                st.error(f"Validation failed: {e}")

# 2 Wikipedia Retrieval

# 3 Generate Report
