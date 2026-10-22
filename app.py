import os

import streamlit as st
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

st.set_page_config(
    page_title="Azure AI Chat",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0b1020 0%, #111827 55%, #17152b 100%);
        color: #f1f5f9;
    }
    [data-testid="stSidebar"] {
        background: #0a0f1c;
        border-right: 1px solid #263044;
    }
    .hero {
        padding: 1.4rem 0 1rem 0;
    }
    .hero h1 {
        font-size: 2.5rem;
        font-weight: 750;
        letter-spacing: -1.5px;
        margin-bottom: 0.25rem;
    }
    .hero p {
        color: #a5b4cf;
        font-size: 1rem;
    }
    .stChatMessage {
        border: 1px solid rgba(148, 163, 184, .14);
        border-radius: 16px;
        background: rgba(255, 255, 255, .035);
    }
    div[data-testid="stChatInput"] {
        border-color: #475569;
    }
    .status {
        color: #a5b4cf;
        font-size: .9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Azure client ----------
@st.cache_resource
def get_client():
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
    key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
    api_version = os.getenv(
        "AZURE_OPENAI_API_VERSION", ""
    ).strip()

    if not endpoint or not key or not api_version:
        raise ValueError(
            "Configure AZURE_OPENAI_ENDPOINT, "
            "AZURE_OPENAI_API_KEY, and "
            "AZURE_OPENAI_API_VERSION in .env."
        )

    return AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=key,
        api_version=api_version,
        timeout=60.0,
        max_retries=2,
    )


deployment = os.getenv(
    "AZURE_OPENAI_DEPLOYMENT", ""
).strip()

# ---------- Session state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = (
        "You are a helpful, clear, and friendly AI assistant. "
        "Use Markdown formatting when it improves readability."
    )

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## ✦ Azure AI")
    st.caption("Powered by your Azure deployment")
    st.divider()

    st.markdown("### Assistant settings")
    st.session_state.system_prompt = st.text_area(
        "System instructions",
        value=st.session_state.system_prompt,
        height=150,
        help="Set the assistant's behavior and response style.",
    )

    st.markdown(
        f"**Deployment:** `{deployment or 'Not configured'}`"
    )
    st.markdown(
        f"**Messages:** {len(st.session_state.messages)}"
    )

    if st.button("＋ New chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Chat history is stored in this session only.")
    st.caption("Keep your Azure API key private.")

# ---------- Main interface ----------
st.markdown(
    """
    <div class="hero">
        <h1>✦ What can I help with?</h1>
        <p>Your personal AI assistant, connected to Azure.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    st.markdown("#### Start a conversation")
    c1, c2, c3 = st.columns(3)

    suggestions = [
        ("💡 Learn something", "Explain how large language models work."),
        ("🐍 Write Python", "Write a Python function to check prime numbers."),
        ("🧠 Brainstorm", "Suggest five useful AI project ideas for students."),
    ]

    for col, (label, prompt) in zip(
        [c1, c2, c3], suggestions
    ):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.pending_prompt = prompt
                st.rerun()

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Process either a typed message or a suggestion
typed_prompt = st.chat_input("Message your AI assistant...")
prompt = typed_prompt

if not prompt and st.session_state.get("pending_prompt"):
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            if not deployment:
                raise ValueError(
                    "Set AZURE_OPENAI_DEPLOYMENT in your .env file."
                )

            client = get_client()

            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model=deployment,
                    messages=[
                        {
                            "role": "system",
                            "content": st.session_state.system_prompt,
                        },
                        *st.session_state.messages,
                    ],
                    temperature=0.7,
                    max_tokens=1500,
                )

            answer = response.choices[0].message.content
            answer = answer or "The model returned an empty response."

            st.markdown(answer)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

        except Exception as exc:
            # Avoid printing environment variables or secrets.
            st.error(
                "I couldn't get a response from Azure. "
                "Check your endpoint, deployment name, API version, "
                "key, quota, and network connection."
            )
            st.caption(f"Error details: {type(exc).__name__}: {exc}")
            # Remove the failed turn so the user can retry.
            st.session_state.messages.pop()

