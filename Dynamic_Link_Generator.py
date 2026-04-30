import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Secure Access Portal", 
    page_icon="🔐", 
    layout="wide"
)

# 2. Professional UI Styling (CSS Hack)
st.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 0rem; padding-left: 2rem; padding-right: 2rem; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stAppDeployButton { display: none; }
        [data-testid="stToolbar"] { visibility: hidden; display: none; }
        iframe { border: none; }
    </style>
""", unsafe_allow_html=True)

# ... (Keep your existing Page Config and CSS) ...

# 3. Connection Setup
conn = st.connection("gsheets", type=GSheetsConnection)
user_token = st.query_params.get("token")

if not user_token:
    st.error("### Access Required\nNo security token detected.")
else:
    df = conn.read(ttl=0)
    token_data = df[df['Token'].astype(str) == str(user_token)]

    if token_data.empty:
        st.error("### Invalid Link\nThe link is not recognized by our system.")
    else:
        current_status = token_data['Status'].values[0]
        
        # --- IMPROVED LOGIC: Case-Insensitive Type Check ---
        # We look at Column F (Type). We use .upper() to avoid "Internal" vs "INTERNAL" errors.
        try:
            # We use index 5 because 'Type' is the 6th column (A=0, B=1, C=2, D=3, E=4, F=5)
            form_type = str(token_data.iloc[0, 5]).upper() 
        except:
            form_type = "EXTERNAL"

        # Define URLs
        EXTERNAL_FORM = "https://forms.office.com/r/KchEak7FWA?embed=true"
        INTERNAL_FORM = "https://forms.office.com/r/5s3GA7Df0T?embed=true"

        if current_status == "Active":
            # Burn token
            df.loc[df['Token'].astype(str) == str(user_token), 'Status'] = 'Used'
            conn.update(data=df)
            
            # Use INTERNAL if type is "INTERNAL", otherwise use EXTERNAL
            final_url = INTERNAL_FORM if form_type == "INTERNAL" else EXTERNAL_FORM
            
            st.toast(f"Identity Verified. Loading {form_type} Form...")
            
            st.components.v1.iframe(final_url, height=2000, scrolling=False)
            st.caption(f"⚠️ **Notice:** This is a one-time {form_type} access link.")

        # ... (Keep the rest of your elif/else status messages) ...

        # SCENARIO 1: Token is Active
        if current_status == "Active":
            # Update status to 'Used'
            df.loc[df['Token'].astype(str) == str(user_token), 'Status'] = 'Used'
            conn.update(data=df)
            
            # Select the correct URL based on the 'Type' column
            final_url = INTERNAL_FORM if form_type == "Internal" else EXTERNAL_FORM
            
            st.toast(f"Identity Verified ({form_type}). Loading Form...")
            
            # Embed the selected Form
            st.components.v1.iframe(
                final_url, 
                height=2000, 
                scrolling=False
            )
            
            st.caption(f"⚠️ **Notice:** This is a one-time {form_type} access link.")

        # SCENARIO 2: Token is Used or Terminated
        elif current_status in ["Used", "Terminated"]:
            st.warning("### Link Expired")
            st.write("This secure registration link has already been used or has reached its expiration date.")

        # SCENARIO 3: Token is On hold
        elif current_status == "On hold":
            st.info("### Access Pending")
            st.write("This registration link is currently **On Hold** and has not yet been activated.")

        # SCENARIO 4: Any other status
        else:
            st.error("### Access Restricted")
            st.write("There is a status issue with this token. Please contact technical support.")
