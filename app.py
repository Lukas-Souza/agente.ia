"""AGENTE 

Agente de chat que recebe perguntas em linguagem natural, responde usando o
Gemini (via LangChain) e mantém o contexto da conversa. Interface: Streamlit.
"""

import os

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
FALLBACK_MODEL = "gemini-3.5-flash-lite"

SYSTEM_PROMPT = (
    "Você é um assistente de IA prestativo, claro e objetivo. "
    "Responda sempre em português do Brasil, a menos que o usuário peça outro idioma. "
    "Use o histórico da conversa para manter o contexto das respostas."
    "Responda somente com noticias atuais"
)

st.set_page_config(page_title="LLM")
st.title("IA do Recife Brasileira")
st.caption(f"Modelo: {MODEL_NAME} · LangChain + Streamlit")

# A chave vem do arquivo .env ou, se não existir, é colada na barra lateral.
api_key = os.getenv("GOOGLE_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Chave da API do Gemini", type="password")
if not api_key:
    st.info(
        "Cole sua chave da API do Gemini na barra lateral "
        "(ou crie um arquivo .env) para começar."
    )
    st.stop()


@st.cache_resource
def get_llm(key: str, model_name: str) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=key,
        temperature=0.7,
        request_timeout=30,
        retries=0,
    )


def is_capacity_error(exc: Exception) -> bool:
    current: BaseException | None = exc
    visited = set()
    while current is not None and id(current) not in visited:
        visited.add(id(current))
        status = getattr(current, "status_code", None) or getattr(current, "code", None)
        if str(status) in {"429", "503", "504"}:
            return True
        message = str(current).upper()
        if any(marker in message for marker in ("RESOURCE_EXHAUSTED", "TOO MANY REQUESTS", "RATE LIMIT", "QUOTA EXCEEDED", "OVERLOADED", "DEADLINE_EXCEEDED")):
            return True
        current = current.__cause__ or current.__context__
    return False


def extract_text(content) -> str:
    """O conteúdo da resposta pode vir como texto ou como lista de blocos."""
    if isinstance(content, str):
        return content
    parts = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "".join(parts)


# INICIA A CONVERSA 

def new_conversation() -> list:
    return [SystemMessage(content=SYSTEM_PROMPT)]


llm = get_llm(api_key, MODEL_NAME)

# O histórico fica guardado na sessão: é ele que mantém o contexto da conversa.
if "messages" not in st.session_state:
    st.session_state.messages = new_conversation()

with st.sidebar:
    st.header("Opções")
    if st.button("🗑️ Nova conversa"):
        st.session_state.messages = new_conversation()
        st.rerun()
    st.caption("O agente lembra de tudo o que foi dito nesta conversa.")

# Redesenha o histórico na tela.
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# Nova pergunta do usuário.
if prompt := st.chat_input("Digite sua pergunta..."):
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                # Envia o histórico completo para o LLM (contexto da conversa).
                try:
                    response = llm.invoke(st.session_state.messages)
                except Exception as primary_error:
                    if not is_capacity_error(primary_error) or MODEL_NAME == FALLBACK_MODEL:
                        raise
                    st.warning(f"{MODEL_NAME} falou. Ativando o modelo {FALLBACK_MODEL}.")
                    fallback_llm = get_llm(api_key, FALLBACK_MODEL)
                    response = fallback_llm.invoke(st.session_state.messages)
                answer = extract_text(response.content)
            except Exception as exc:
                st.session_state.messages.pop()  # remove a pergunta que falhou
                st.error(f"Erro ao chamar o Gemini: {exc}")
                st.stop()
        st.markdown(answer)

    st.session_state.messages.append(AIMessage(content=answer))
