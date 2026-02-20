import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import anthropic
import wikipedia
import re

# Page Layout
st.set_page_config(page_title="Market Research Assistant")
st.title("Market Research Assistant")

# 1 Validate the Industry
def validate_industry(user_input: str) -> tuple[bool, str]:
    """Use Claude to check if the user provided a valid industry."""
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
    import json
    text = response.content[0].text.strip()
    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    data = json.loads(text)
    return data["valid"], data.get("industry", user_input), data.get("reason", "")

# 2 Wikipedia Retrieval


# 3 Generate Report
