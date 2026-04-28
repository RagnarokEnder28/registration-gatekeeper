import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Basic Page Setup
st.set_page_config(page_title="Secure Access Portal", page_icon="🔐")

st.title("Service Registration Access")
st.write("Verifying your secure access token...")

# 1. Connect to Google Sheets
# Connection details are pulled from your Streamlit Cloud Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Get the token from the URL (?token=xxxx)
user_token = st.query_params.get("token")

if not user_token:
    st.error("No access token detected. Please use the link provided by your coordinator.")
else:
    # Read the current sheet data
    # ttl=0 ensures we don't use a cached version of the spreadsheet
    df = conn.read(ttl=0)

    # 3. Check if token exists and is still 'Active'
    # We use .astype(str) to ensure a perfect match regardless of data type
    token_row = df[(df['Token'].astype(str) == str(user_token)) & (df['Status'] == 'Active')]

    if not token_row.empty:
        # SUCCESS: Update the status to 'Used' immediately (the "Burn")
        df.loc[df['Token'].astype(str) == str(user_token), 'Status'] = 'Used'
        
        # Save the updated sheet back to Google
        conn.update(data=df)
        
        st.success("Identity Verified! Please complete the registration below.")

        # 4. EMBED THE FORM (This hides the direct URL from the address bar)
        # The ?embed=true makes the Microsoft Form fit the Streamlit window
        form_url = "https://forms.office.com/r/KchEak7FWA?embed=true"
        
        st.components.v1.iframe(form_url, height=800, scrolling=True)
        
        st.info("⚠️ IMPORTANT: Do not refresh or close this page until you have clicked 'Submit' on the form above.")
    else:
        # This handles tokens that are already 'Used' or don't exist
        st.error("Invalid or Expired Link.")
        st.write("This secure link has already been used. If you need to register again, please request a new link.")
