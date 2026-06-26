import streamlit as st
from streamlit_gsheets import GSheetsConnection
import time
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Secure Access Portal", 
    page_icon="🔐", 
    layout="wide"
)

# 2. UI Styling
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

# 3. Connection Setup
def get_connection():
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception:
        return None

conn = get_connection()
user_token = st.query_params.get("token")

if conn is None:
    st.error("The secure gateway is taking longer than usual to respond. Please refresh.")
    st.stop()

if not user_token:
    st.error("### Access Required\nNo security token detected.")
else:
    df = conn.read(ttl=0)
    token_data = df[df['Token'].astype(str) == str(user_token)]

    if token_data.empty:
        st.error("### Invalid Link\nThe link is not recognized by our system.")
    else:
        current_status = token_data['Status'].values[0]
        
        # Determine Form Type (Column F / Index 5)
        try:
            form_type_raw = str(token_data.iloc[0, 5]).upper()
        except:
            form_type_raw = "EXTERNAL"

        EXTERNAL_FORM = "https://forms.office.com/r/KchEak7FWA?embed=true"
        INTERNAL_FORM = "https://forms.office.com/r/5s3GA7Df0T?embed=true"

        # --- SINGLE LOGIC GATEWAY ---
        if current_status == "Active":
            # 1. Update status to 'Used' in the dataframe and sheet
            df.loc[df['Token'].astype(str) == str(user_token), 'Status'] = 'Used'
            conn.update(data=df)
            
            # 2. Select the URL
            final_url = INTERNAL_FORM if form_type_raw == "INTERNAL" else EXTERNAL_FORM
            
            # 3. Display UI elements ONCE
            st.toast(f"Identity Verified. Loading {form_type_raw} Form...")
            
            # Handle Internal vs External routing due to Microsoft iframe restrictions
            if form_type_raw == "INTERNAL":
                st.success("### Identity Verified")
                st.write(
                    "This internal registration requires organization authentication. "
                    "To sign in securely, please click the button below to open the form."
                )
                st.link_button("👉 Open Internal Microsoft Form", final_url, type="primary")
            else:
                # External forms usually allow embedding since they skip the organization login screen
                st.components.v1.iframe(final_url, height=1200, scrolling=True)
                
            st.caption(f"⚠️ **Notice:** This is a one-time {form_type_raw} access link.")

        elif current_status in ["Used", "Terminated"]:
            st.warning("### Link Expired")
            st.write("This secure registration link has already been used or has expired.")

        elif current_status == "On hold":
            st.info("### Access Pending")
            st.write("This registration link is currently **On Hold**.")

        else:
            st.error("### Access Restricted")
            st.write("There is a status issue with this token. Please contact support.")
