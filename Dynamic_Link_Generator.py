import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. SET TO WIDE MODE: This uses the full width of the browser window
st.set_page_config(
    page_title="Secure Access Portal", 
    page_icon="🔐", 
    layout="wide" # This is key for "full screen"
)

# 2. CSS HACK: This removes the default padding at the top of Streamlit apps
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. Connection and Logic
conn = st.connection("gsheets", type=GSheetsConnection)
user_token = st.query_params.get("token")

if not user_token:
    st.error("No access token detected. Please use the link provided by your coordinator.")
else:
    df = conn.read(ttl=0)
    token_row = df[(df['Token'].astype(str) == str(user_token)) & (df['Status'] == 'Active')]

    if not token_row.empty:
        # Update status immediately
        df.loc[df['Token'].astype(str) == str(user_token), 'Status'] = 'Used'
        conn.update(data=df)
        
        # 4. FULL SCREEN EMBED
        # We use a height of 1000 or higher to ensure the user doesn't see a double scrollbar
        form_url = "https://forms.office.com/r/KchEak7FWA?embed=true"
        
        # Small notification that disappears after a few seconds or stays subtle
        st.toast("Identity Verified. Accessing Form...")
        
        st.components.v1.iframe(form_url, height=1200, scrolling=True)
        
        st.caption("⚠️ Do not refresh this page. Your one-time access token has been consumed.")
    else:
        st.error("Invalid or Expired Link.")
        st.info("This secure link has already been used. Please request a new link if you need to resubmit.")
