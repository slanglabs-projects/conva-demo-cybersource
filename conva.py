import streamlit as st
from conva_ai import ConvaAI

DEBUG = False

client = ConvaAI(
    assistant_id=st.secrets.conva_assistant_id,
    api_key=st.secrets.conva_api_key,
    assistant_version="15.0.0",
)


def invoke_dev_center_qna(query, history="{}"):
    response = client.invoke_capability(query=query, history=history, stream=False, timeout=600)

    message = response.message

    answer = response.parameters.get("detailed_answer_in_markdown", "")

    code_sample = ""
    if "code_sample" in response.parameters:
        code_sample = response.parameters["code_sample"]
        if isinstance(code_sample, dict):
            code_sample = code_sample.get("code", "")

    citations = []
    if "citations" in response.parameters:
        tmp = response.parameters.get("citations", [])
        if isinstance(tmp, list):
            for citation in tmp:
                if isinstance(citation, dict):
                    citations.append(citation.get("url", ""))
                elif isinstance(citation, str):
                    citations.append(citation)

    if DEBUG:
        print("sql_query_creation response: {}\n\n".format(response))

    return message, answer, code_sample, citations, response.related_queries, response.conversation_history


def invoke_conva_capabilities(query, history="{}"):
    return invoke_dev_center_qna(query, history)
