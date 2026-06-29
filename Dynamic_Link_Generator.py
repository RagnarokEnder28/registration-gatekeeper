import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# ======================================================
# Page Configuration
# ======================================================

st.set_page_config(
    page_title="Secure Access Portal",
    page_icon="🔐",
    layout="wide"
)

# ======================================================
# Custom CSS
# ======================================================

st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 0rem;
    padding-left: 2rem;
    padding-right: 2rem;
}
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
.stAppDeployButton {display:none;}
[data-testid="stToolbar"] {display:none;}
</style>
""", unsafe_allow_html=True)

# ======================================================
# Connection
# ======================================================

def get_connection():
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception:
        return None

conn = get_connection()

if conn is None:
    st.error("The secure gateway is taking longer than usual to respond. Please refresh.")
    st.stop()

# ======================================================
# Read Token & Data
# ======================================================

user_token = st.query_params.get("token")

if not user_token:
    st.error("### Access Required")
    st.write("No security token detected.")
    st.stop()

df = conn.read(ttl=0)
token_data = df[df["Token"].astype(str) == str(user_token)]

if token_data.empty:
    st.error("### Invalid Link")
    st.write("The link is not recognized by our system.")
    st.stop()

# ======================================================
# Logic
# ======================================================

current_status = token_data["Status"].values[0]
form_type = str(token_data.iloc[0, 5]).strip().upper()

# URLs updated to remove 'embed=true' which causes security blocks
INTERNAL_FORM = "https://forms.office.com/r/5s3GA7Df0T"
EXTERNAL_FORM = "https://forms.office.com/r/KchEak7FWA"

if current_status == "Active":

    # Mark as Used
    df.loc[df["Token"].astype(str) == str(user_token), "Status"] = "Used"
    conn.update(data=df)

    st.success("✅ Identity Verified")
    st.info("Your identity has been successfully verified.")
    
    target_url = INTERNAL_FORM if form_type == "INTERNAL" else EXTERNAL_FORM

    # Using st.link_button for reliable, non-embedded navigation
    # This bypasses iframe security blocks (X-Frame-Options: DENY)
    if hasattr(st, "link_button"):
        st.link_button("👉 Continue to Microsoft Form", url=target_url, type="primary")
    else:
        # Fallback if Streamlit version is older
        st.markdown(
            f'<a href="{target_url}" target="_blank" style="display:inline-block; padding:0.5rem 1rem; background-color:#ff4b4b; color:white; border-radius:0.25rem; text-decoration:none; font-weight:bold;">👉 Continue to Microsoft Form</a>', 
            unsafe_allow_html=True
        )

    st.caption("⚠️ This is a one-time access link.")

elif current_status in ["Used", "Terminated"]:
    st.warning("### Link Expired")
    st.write("This secure registration link has already been used or has expired.")

elif current_status == "On hold":
    st.info("### Access Pending")
    st.write("This registration link is currently On Hold.")

else:
    st.error("### Access Restricted")
    st.write("There is a status issue with this token. Please contact support.")
