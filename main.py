import json
import os
import streamlit as st
from conva import invoke_conva_capabilities


# Initialize session state variables
def init_session_state():
    if "sources" not in st.session_state:
        st.session_state.sources = []
    if "history" not in st.session_state:
        st.session_state.history = "{}"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "processing_query" not in st.session_state:
        st.session_state.processing_query = False
    if "current_query" not in st.session_state:
        st.session_state.current_query = None
    # Only initialize related queries if they haven't been set yet
    if "related" not in st.session_state:
        st.session_state.related = []
        # Load initial related queries from file
        if os.path.exists("data/related.json"):
            with open("data/related.json", "r") as f:
                st.session_state.related = json.load(f)


# Custom CSS for button styling
def load_custom_css():
    st.markdown(
        """
        <style>
        button * {
            height: auto;
        }
        button p {
            font-size: .8em;
        }
        .stButton > button {
            width: 100%;
            white-space: normal;
            height: auto;
            min-height: 45px;
        }
        .related-queries {
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# Get response from the bot
def get_bot_response(user_input, pb):
    try:
        pb.progress(100, "Done")
        message, code_sample, sources = invoke_conva_capabilities(user_input, pb, st.session_state.history)
        return message, code_sample, sources
    except Exception as e:
        st.error(f"Error getting response: {str(e)}")
        return "Sorry, there was an error processing your request.", None, None


# Handle related query button click
def handle_related_query(query):
    if not st.session_state.processing_query:
        st.session_state.current_query = query
        st.session_state.processing_query = True
        # st.rerun()


# Display related query buttons
def show_related_queries():
    if st.session_state.related:
        # st.markdown("##### Related Queries")
        related = sorted(st.session_state.related, key=lambda l: len(l))[:3]
        cols = st.columns(len(related))

        for idx, query in enumerate(related):
            with cols[idx]:
                st.button(
                    query,
                    key=f"related_{idx}_{query}",
                    on_click=handle_related_query,
                    args=[query],
                    use_container_width=True,
                )


# Process and display chat messages
def process_query(prompt):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "message": prompt})

    # Display assistant response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        _, col1, _ = placeholder.columns([1, 3, 1])
        pb = col1.progress(0, "Understanding your query...")

        message, code_sample, sources = get_bot_response(prompt, pb)

        placeholder.empty()

        if not message:
            message = "Sorry, I couldn't find any information on that."

        st.markdown(message)

        if code_sample:
            with st.expander("Code Sample"):
                st.code(code_sample, language="python")

        if sources:
            with st.expander("Sources"):
                for index, url in enumerate(sources):
                    st.markdown(
                        f"{index + 1}. <a href='{url}'>{url}</a>",
                        unsafe_allow_html=True,
                    )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "message": message,
                "code_sample": code_sample,
                "sources": sources,
            }
        )

    # Show related queries after processing
    show_related_queries()
    st.session_state.processing_query = False


def main():
    try:
        # Initialize session state
        init_session_state()
        load_custom_css()

        st.title("VISA Cybersource Developer Q&A")
        st.divider()

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["message"])
                if "code_sample" in message and message["code_sample"]:
                    with st.expander("Code Sample"):
                        st.code(message["code_sample"], language="python")
                if "sources" in message and message["sources"]:
                    with st.expander("Sources"):
                        for index, url in enumerate(message["sources"]):
                            st.markdown(
                                f"{index + 1}. <a href='{url}'>{url}</a>",
                                unsafe_allow_html=True,
                            )

        # Process any pending query
        if st.session_state.current_query and st.session_state.processing_query:
            prompt = st.session_state.current_query
            st.session_state.current_query = None
            process_query(prompt)
        else:
            # Show related queries if not processing a query
            show_related_queries()

        # Handle chat input
        if prompt := st.chat_input("What would you like to know?"):
            st.session_state.current_query = prompt
            st.session_state.processing_query = True
            st.rerun()

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
