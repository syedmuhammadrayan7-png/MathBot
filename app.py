import streamlit as st
from utils import query_collection, build_prompt
from openai import OpenAI
import os
import re

# Setup OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page config
st.set_page_config(page_title="📘 MathBot", page_icon="🤖", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
        /* Background */
        .stApp {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            font-family: 'Segoe UI', sans-serif;
            color: #f8f9fa;
        }

        /* Title */
        h1 {
            color: #00e6e6;
            text-align: center;
            font-weight: bold;
            text-shadow: 0px 0px 10px #00e6e6;
        }

        /* Chat bubbles */
        .user-bubble {
            background: #1e3c72;
            color: white;
            padding: 12px;
            border-radius: 15px;
            margin: 8px 0;
            max-width: 80%;
            word-wrap: break-word;
            box-shadow: 0px 0px 8px #00bfff;
        }
        .bot-bubble {
            background: #2c5364;
            color: #f1f1f1;
            padding: 12px;
            border-radius: 15px;
            margin: 8px 0;
            max-width: 80%;
            word-wrap: break-word;
            box-shadow: 0px 0px 8px #00ffcc;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: #111827;
            color: #e5e7eb;
            border-right: 2px solid #374151;
        }
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #00e6e6;
        }

        /* Buttons */
        button {
            background-color: #00bcd4 !important;
            color: white !important;
            border-radius: 12px !important;
            font-weight: bold !important;
            border: none !important;
            box-shadow: 0px 0px 10px #00e6e6;
        }
        button:hover {
            background-color: #0097a7 !important;
            box-shadow: 0px 0px 15px #00ffff;
        }

        /* Input box */
        input {
            background-color: #1f2937 !important;
            color: #f8f9fa !important;
            border-radius: 10px !important;
            padding: 10px !important;
            border: 1px solid #00e6e6 !important;
        }
        /* === GLOBAL BACKGROUND === */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: #f0f0f0;
    font-family: 'Segoe UI', sans-serif;
}

/* === TITLES === */
h1, h2, h3 {
    color: #00e6e6;
    text-shadow: 0px 0px 8px rgba(0, 230, 230, 0.6);
    font-weight: bold;
}

/* === CHAT BUBBLES === */
.user-bubble {
    background: rgba(0, 230, 230, 0.15);
    border: 1px solid rgba(0, 230, 230, 0.4);
    border-radius: 12px;
    padding: 12px 16px;
    margin: 8px 0;
    box-shadow: 0 4px 12px rgba(0, 230, 230, 0.2);
    transition: transform 0.2s ease-in-out;
}
.user-bubble:hover {
    transform: scale(1.02);
}

.bot-bubble {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 12px;
    padding: 12px 16px;
    margin: 8px 0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    transition: transform 0.2s ease-in-out, box-shadow 0.3s ease-in-out;
}
.bot-bubble:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.6);
}

/* === INPUT BOX === */
input, textarea {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #fff !important;
    border-radius: 10px !important;
    border: 1px solid rgba(0, 230, 230, 0.4) !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3) inset !important;
    padding: 10px !important;
}

/* === BUTTONS === */
button {
    background: linear-gradient(45deg, #00e6e6, #007a7a) !important;
    color: #fff !important;
    font-weight: bold !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 8px 14px !important;
    box-shadow: 0 4px 10px rgba(0, 230, 230, 0.4) !important;
    transition: all 0.2s ease-in-out !important;
}
button:hover {
    background: linear-gradient(45deg, #00ffff, #00b3b3) !important;
    transform: scale(1.05);
    box-shadow: 0 6px 14px rgba(0, 230, 230, 0.6) !important;
}

/* === SIDEBAR === */
[data-testid="stSidebar"] {
    background: rgba(15, 32, 39, 0.95);
    border-right: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 4px 0px 15px rgba(0, 0, 0, 0.6);
}

/* === CARD STYLING (for chunks) === */
.chunk-box {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 12px;
    transition: all 0.2s ease-in-out;
}
.chunk-box:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: translateX(3px);
}
/* === GLOBAL BACKGROUND === */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: #f0f0f0;
    font-family: 'Segoe UI', sans-serif;
}

/* === TITLES === */
h1, h2, h3 {
    color: #00e6e6;
    text-shadow: 0px 0px 8px rgba(0, 230, 230, 0.6);
    font-weight: bold;
}

/* === CHAT BUBBLES WITH ANIMATION === */
@keyframes fadeSlideIn {
    0% { opacity: 0; transform: translateY(20px); }
    100% { opacity: 1; transform: translateY(0); }
}

.user-bubble, .bot-bubble {
    border-radius: 12px;
    padding: 12px 16px;
    margin: 8px 0;
    animation: fadeSlideIn 0.4s ease-in-out;
    transition: transform 0.2s ease-in-out, box-shadow 0.3s ease-in-out;
}

/* User bubble style */
.user-bubble {
    background: rgba(0, 230, 230, 0.15);
    border: 1px solid rgba(0, 230, 230, 0.4);
    box-shadow: 0 4px 12px rgba(0, 230, 230, 0.2);
}
.user-bubble:hover {
    transform: scale(1.02);
}

/* Bot bubble style */
.bot-bubble {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}
.bot-bubble:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.6);
}

/* === INPUT BOX === */
input, textarea {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #fff !important;
    border-radius: 10px !important;
    border: 1px solid rgba(0, 230, 230, 0.4) !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3) inset !important;
    padding: 10px !important;
}

/* === BUTTONS === */
button {
    background: linear-gradient(45deg, #00e6e6, #007a7a) !important;
    color: #fff !important;
    font-weight: bold !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 8px 14px !important;
    box-shadow: 0 4px 10px rgba(0, 230, 230, 0.4) !important;
    transition: all 0.2s ease-in-out !important;
}
button:hover {
    background: linear-gradient(45deg, #00ffff, #00b3b3) !important;
    transform: scale(1.05);
    box-shadow: 0 6px 14px rgba(0, 230, 230, 0.6) !important;
}

/* === SIDEBAR === */
[data-testid="stSidebar"] {
    background: rgba(15, 32, 39, 0.95);
    border-right: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 4px 0px 15px rgba(0, 0, 0, 0.6);
}

/* === CARD STYLING (for chunks) === */
.chunk-box {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 12px;
    transition: all 0.2s ease-in-out;
    animation: fadeSlideIn 0.5s ease-in-out;
}
.chunk-box:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: translateX(3px);
}


    </style>
""", unsafe_allow_html=True)

# Title
st.title("🤖 MathBot - Your AI Math Tutor")

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "You are a helpful math tutor. Explain concepts step by step in a simple way."}
    ]

# Sidebar: Options + relevant chunks
with st.sidebar:
    st.header("⚙️ Options")
    if st.button("🗑️ Clear Chat"):
        st.session_state["messages"] = [
            {"role": "system", "content": "You are a helpful math tutor. Explain concepts step by step in a simple way."}
        ]
        st.success("Chat cleared!")

    st.subheader("📄 Relevant Chunks")
    if "last_docs" in st.session_state:
        for i, doc in enumerate(st.session_state["last_docs"], start=1):
            st.markdown(f"**Chunk {i}:**")
            st.caption(doc["document"][:300] + "...")
            st.caption(f"📌 Source: {doc['metadata']} | 🔎 Distance: {doc['distance']:.3f}")

# Function: Render text with LaTeX
def render_with_latex(text: str):
    parts = re.split(r"(\$.*?\$|\\\\\[.*?\\\\\])", text)
    for part in parts:
        if part.startswith("$") or part.startswith("\\["):
            st.latex(part.strip("$").strip("\\[").strip("\\]"))
        else:
            if part.strip():
                st.markdown(part)

# Display chat history
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-bubble'><b>You:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f"<div class='bot-bubble'><b>MathBot:</b></div>", unsafe_allow_html=True)
        render_with_latex(msg["content"])

# User input
question = st.text_input("💬 Ask me a math question from your book:")

if st.button("Get Answer"):
    if not question.strip():
        st.warning("Please type a question first.")
    else:
        st.session_state["messages"].append({"role": "user", "content": question})

        # Retrieve relevant chunks
        docs = query_collection(question, k=3)
        st.session_state["last_docs"] = docs

        if not docs:
            st.error("No relevant context found in your PDFs.")
        else:
            prompt = build_prompt(question, docs)
            st.session_state["messages"].append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state["messages"]
            )

            answer = response.choices[0].message.content
            st.session_state["messages"].append({"role": "assistant", "content": answer})

            st.markdown("### ✨ Answer:")
            render_with_latex(answer)
