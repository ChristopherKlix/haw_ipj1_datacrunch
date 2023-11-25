import streamlit as st
import streamlit.components.v1 as components


class Navbar:
    def render():
        st.markdown("""
                <style>
                    [data-testid="collapsedControl"] {
                        display: none;
                    }

                    [data-testid="stSidebar"] {
                        display: none;
                    }

                    [data-testid="stHeader"] {
                        background: none;
                        background: linear-gradient(to bottom, white, transparent);
                    }
                </style>
            """,
                unsafe_allow_html=True,
            )

        with open('./static/navbar.html', 'r') as f:
            st.markdown(f.read(), unsafe_allow_html=True)

        with open('./static/navbar.css', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
