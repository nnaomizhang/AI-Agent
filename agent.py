import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.retrievers import WikipediaRetriever

retriever = WikipediaRetriever()

# Page Layout
st.set_page_config(page_title="Market Research Assistant")
st.title("Market Research Assistant")
st.caption("This report is based on Wikipedia sources and should be used for preliminary research only")

# Sidebar Settings
st.sidebar.header("Settings")

# API Key
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2)
model = st.sidebar.selectbox(
    "Model",
    ["gpt-4o-mini", "gpt-4o"] # mini for development, gpt-4o for performance evaluation
)

if not api_key:
    api_key = st.sidebar.text_input("Please enter your OpenAI API key", type="password")

llm = ChatOpenAI(
    model=model,
    temperature=temperature,
    api_key=api_key
) if api_key else None

# 1 Industry Validation
def validate_industry_input(user_input: str) -> tuple[bool, str, str]:
    text = user_input.strip()
    if llm is None:
        return False, "", "Missing OpenAI API key"
    if not text:
        return False, "", "Please provide a valid industry to proceed"
    
    
    # Validating with LLM
    messages = [
        SystemMessage(content="""You are a validation assistant. 
        Determine whether the user input is a real industry/business sector.
        Reply with ONLY 'YES' or 'NO' followed by a colon with a brief reason.
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

    
    else:
        st.warning(message)
        st.info("Please update your industry input and try again")  
    
# 2 Wikipedia Retrieval

def retrieve_wikipedia_pages(industry: str, llm) -> list:
    retriever = WikipediaRetriever(
        top_k_results=10,       # fetch more initially so we have room to filter
        doc_content_chars_max=5000
    )
    docs = retriever.invoke(industry)
    
    # Filter for relevance using LLM
    relevant_docs = []
    for doc in docs:
        title = doc.metadata.get("title", "")
        messages = [
            SystemMessage(content="""You are a relevance checker. 
            Determine if a Wikipedia page is relevant to the given industry.
            Reply with ONLY 'YES' or 'NO'."""),
            HumanMessage(content=f"Is the Wikipedia page titled '{title}' relevant to the '{industry}' industry?")
        ]
        response = llm.invoke(messages).content.strip().upper()
        if response.startswith("YES"):
            relevant_docs.append(doc)
        
        if len(relevant_docs) == 5:   # stop once we have 5 relevant pages
            break
    
    return relevant_docs

# Streamlit
st.subheader("Step 2: Wikipedia Retrieval")

if "industry" not in st.session_state:
    st.warning("Incomplete Step 1: Industry Validation")
else:
    if st.button("Retrieve Relevant Wikipedia Pages"):
        with st.spinner("Searching Wikipedia..."):
            docs = retrieve_wikipedia_pages(st.session_state["industry"], llm)
            st.session_state["docs"] = docs

    if "docs" in st.session_state:
        docs = st.session_state["docs"]
        if docs:
            st.success(f"Here are the {len(docs)} most relevant Wikipedia pages:")
            for i, doc in enumerate(docs, 1):
                title = doc.metadata.get("title", "Unknown")
                url = doc.metadata.get("source", "No URL available")
                st.markdown(f"**{i}. [{title}]({url})**")
            if len(docs) < 5:
                st.warning(f"Warning: Only {len(docs)}/5 relevant pages found. The following report may be less comprehensive.")
        else:
            st.error("No relevant Wikipedia pages were found. Please try a different industry.")
            
# 3 Industry Report Generation

def generate_industry_report(industry: str, docs: list, llm) -> str:
    context = "\n\n".join([
        f"Source: {doc.metadata.get('title', 'Unknown')}\n{doc.page_content}"
        for doc in docs
    ])
    
    messages = [
        SystemMessage(content="""You are a professional market research analyst. 
        Generate a concise but COMPLETE industry report based ONLY on the provided Wikipedia sources.
        The report must:
        - Be a full, complete report — do not cut off mid-sentence or leave sections incomplete
        - Be STRICTLY under 500 words — plan your response to fit within this limit
        - Be structured with clear sections: Overview, Key Players, Market Trends, Challenges
        - Be written for a business analyst audience
        - Only use information from the provided sources
        - Budget your words: ~100 words per section to stay under 500 words total"""),
        HumanMessage(content=f"""Industry: {industry}
        
Wikipedia Sources:
{context}

Write a complete, professional industry report under 500 words.""")
    ]
    
    response = llm.invoke(messages).content.strip()
    return response

# Streamlit
st.subheader("Step 3: Industry Report")

if "docs" not in st.session_state:
    st.warning("Incomplete Step 2: Wikipedia Retrieval ")
else:
    if st.button("Generate Industry Report"):
        with st.spinner("Generating report..."):
            report = generate_industry_report(
                st.session_state["industry"],
                st.session_state["docs"],
                llm
            )
            st.session_state["report"] = report

if "report" in st.session_state:
    st.markdown(st.session_state["report"])
    
    st.markdown(report)
      
    word_count = len(st.session_state["report"].split())
    if word_count <= 500:
           st.caption(f"Word count: {word_count}/500")
    else:
           st.warning(f"Report exceeds 500 words ({word_count} words).")
           
    st.download_button(
        label="Download Report",
        data=report,
        file_name=f"{st.session_state['industry']}_market_report.txt",
        mime="text/plain"
    )