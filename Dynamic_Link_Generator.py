# 2. Professional UI Styling (Removes top padding and hides menus/deploy button)
st.markdown("""
    <style>
        /* Removes top padding for a cleaner look */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        
        /* Hides the Streamlit Main Menu (hamburger) */
        #MainMenu {visibility: hidden;}
        
        /* Hides the "Made with Streamlit" footer */
        footer {visibility: hidden;}
        
        /* Hides the header (top bar) */
        header {visibility: hidden;}
        
        /* Hides the "Manage app" / "Deploy" button specifically */
        .stAppDeployButton {
            display: none;
        }
        
        /* Hides the toolbar (bottom right info/status icons) */
        [data-testid="stToolbar"] {
            visibility: hidden;
            display: none;
        }
    </style>
""", unsafe_allow_html=True)
