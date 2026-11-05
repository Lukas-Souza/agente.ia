# Agente de IA com o Google Gemini

Agente de Inteligência Artificial que recebe perguntas em linguagem natural e responde usando um LLM (Google Gemini), mantendo o contexto da conversa.

**Disciplina:** Inteligência Artificial (2026.2-NSIN-0104) — Quiz 03

## Tecnologias

- Python 3.10+
- [LangChain](https://python.langchain.com/) (`langchain-google-genai`)
- Google Gemini (API gratuita do Google AI Studio)
- [Streamlit](https://streamlit.io/) (interface de chat)

## Como funciona

1. O usuário digita uma pergunta na interface de chat.
2. O histórico completo da conversa (mensagens do usuário e do agente) é enviado ao Gemini a cada pergunta, o que mantém o contexto.
3. A resposta do modelo aparece na tela e é adicionada ao histórico.

## Como rodar

```bash
# 1. Criar e ativar o ambiente virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. Configurar a chave da API (duas opções)
# Opção A: colar a chave na barra lateral do app, ao abrir.
# Opção B: criar um arquivo .env na raiz do projeto com:
# GOOGLE_API_KEY=sua_chave_aqui

# 4. Executar
streamlit run app.py
```

A chave gratuita é gerada em https://aistudio.google.com/apikey

Opcional: para trocar o modelo, adicione `GEMINI_MODEL=nome-do-modelo` no `.env` (padrão: `gemini-2.5-flash`).

## Exemplo de uso (teste de contexto)

1. "Meu nome é Miguel e estou estudando IA."
2. "Qual é o meu nome e o que estou estudando?" → o agente responde com base no histórico.
