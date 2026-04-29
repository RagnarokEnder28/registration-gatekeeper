import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Page Configuration for Full Screen
st.set_page_config(
    page_title="Secure Access Portal", 
    page_icon="🔐", 
    layout="wide"
)

# 2. Professional UI Styling (Removes top padding and hides menus)
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. Connection Setup
conn = st.connection("gsheets", type=GSheetsConnection)
user_token = st.query_params.get("token")

if not user_token:
    st.error("### Access Required\nNo security token detected. Please use the unique link provided in your official correspondence.")
else:
    # Read freshest data
    df = conn.read(ttl=0)
    
    # Locate the specific row for this token
    token_data = df[df['Token'].astype(str) == str(user_token)]

    if token_data.empty:
        st.error("### Invalid Link\nThe link you are using is not recognized by our system. Please verify the URL or contact your coordinator.")
    
    else:
        # Get the status from the first matching row
        current_status = token_data['Status'].values[0]

        # SCENARIO 1: Token is Active (Proceed to Form)
        if current_status == "Active":
            # Burn the token immediately
            df.loc[df['Token'].astype(str) == str(user_token), 'Status'] = 'Used'
            conn.update(data=df)
            
            st.toast("Identity Verified. Loading Registration Form...")
            
            # Embed MS Form
            form_url = "https://forms.office.com/r/KchEak7FWA?embed=true"
            st.components.v1.iframe(form_url, height=1200, scrolling=True)
            
            st.caption("⚠️ **Notice:** This is a one-time access link. Your session will expire if this page is refreshed or closed.")

        # SCENARIO 2: Token is Used or Terminated
        elif current_status in ["Used", "Terminated"]:
            st.warning("### Link Expired")
            st.write("""
                Our records indicate that this secure registration link has already been used or has reached its expiration date. 
                
                For security reasons, access tokens are restricted to a single use. If you encountered an error during your previous session and need to resubmit your information, please request a new link from your coordinator.
            """)

        # SCENARIO 3: Token is On hold
        elif current_status == "On hold":
            st.info("### Access Pending")
            st.write("""
                This registration link is currently **On Hold** and has not yet been activated for use. 
                
                Please wait for further instructions from your coordinator. You will be notified once your specific access window is open.
            """)

        # SCENARIO 4: Any other status
        else:
            st.error("### Access Restricted")
            st.write("There is a status issue with this token. Please contact technical support for further assistance.")
