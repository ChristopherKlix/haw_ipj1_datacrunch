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

        with open("./static/navbar.html", "r") as file:
            navbar = file.read()
            st.markdown(navbar, unsafe_allow_html=True)

        with open("./static/navbar.js", "r") as file:
            navbar_script = file.read()
            components.html(f'<script defer id="navbar-js">{navbar_script}</script>', height=0)
