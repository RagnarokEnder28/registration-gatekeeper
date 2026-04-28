import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

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
    # We convert both to strings to avoid errors if the sheet treats tokens as numbers
    token_row = df[(df['Token'].astype(str) == str(user_token)) & (df['Status'] == 'Active')]

    if not token_row.empty:
        # SUCCESS: Update the status to 'Used' in the dataframe
        df.loc[df['Token'].astype(str) == str(user_token), 'Status'] = 'Used'
        
        # Save the updated sheet back to Google
        conn.update(data=df)
        
        st.success("Identity Verified! Your one-time link is ready.")
        
        # The actual Microsoft Form link
        form_url = "https://forms.office.com/r/KchEak7FWA"
        
        # Corrected Markdown block
        st.markdown(f"""
            <a href="{form_url}" target="_blank">
                <button style="
                    background-color: #0078d4; 
                    color: white; 
                    padding: 15px 32px; 
                    border: none; 
                    border-radius: 4px; 
                    cursor: pointer; 
                    font-size: 18px;">
                    Open Registration Form
                </button>
            </a>
        """, unsafe_allow_html=True)
        
        st.info("Note: This access link has now expired and cannot be used again.")
    else:
        st.error("Invalid or Expired Link.")
        st.write("This secure link has already been used or does not exist. Please request a new link.")
