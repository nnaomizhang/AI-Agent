import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import anthropic
import wikipedia
import re
import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Page Layout
st.set_page_config(page_title="Market Research Assistant")
st.title("Market Research Assistant")

# Sidebar Settings
st.sidebar.header("Settings")

api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Please enter your OpenAI API key", type="password")

temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2)

model = st.sidebar.selectbox(
    "Model",
    ["gpt-4o-mini", "gpt-4o"]  
)

llm = ChatOpenAI(
    model=model,
    temperature=temperature,
    api_key=api_key
) if api_key else None

# 1 Validate the Industry
def validate_industry_input(user_input: str) -> tuple[bool, str, str]:
    text = user_input.strip()
    if llm is None:
        return False, "", "Missing OpenAI API key."
    if not text:
        return False, "", "Please enter an industry before continuing."
    
    # Basic empty check first (no need to call LLM)
    if not text:
        return False, "", "Please enter an industry before continuing."
    
    # Use LLM to check if input is a real industry
    messages = [
        SystemMessage(content="""You are a validation assistant. 
        Determine if the user input is a legitimate industry or business sector.
        Reply with ONLY 'YES' or 'NO' followed by a colon and a brief reason.
        Example: 'YES: Healthcare is a recognised industry.'
        Example: 'NO: \"blue\" is a color, not an industry.'"""),
        HumanMessage(content=f"Is this a real industry? '{text}'")
    ]
    
    response = llm.invoke(messages).content.strip()
    is_valid = response.upper().startswith("YES")
    reason = response.split(":", 1)[-1].strip() if ":" in response else response
    
    if is_valid:
        return True, text, f"Industry accepted: {reason}"
    else:
        return False, "", f"Not recognised as an industry: {reason}"
    
# Streamlit
st.subheader("Step 1: Industry Validation")

industry_input = st.text_input(
    "Enter the industry you want to research",
    placeholder="e.g. Healthcare and Biotech",
)

if st.button("Industry Validation"):
    with st.spinner("Validating..."):
        is_valid, industry_name, message = validate_industry_input(industry_input)
    
    if is_valid:
        st.session_state["industry"] = industry_name
        st.success(message)
        st.info("Proceeding to Step 2: Wikipedia Retrieval.")
    
    else:
        st.warning(message)
        st.info("Please update your industry input and try again.")  
    
# 2 Wikipedia Retrieval

# 3 Generate Report
