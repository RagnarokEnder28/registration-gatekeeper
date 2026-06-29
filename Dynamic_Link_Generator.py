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
# UI Styling
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

iframe {
    border:none;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# Google Sheets Connection
# ======================================================

@st.cache_resource
def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)

conn = get_connection()

# ======================================================
# Read Token
# ======================================================

token = st.query_params.get("token")

if not token:
    st.error("### Access Required")
    st.write("No security token detected.")
    st.stop()

# ======================================================
# Read Sheet
# ======================================================

try:
    df = conn.read(ttl=0)
except Exception:
    st.error("Unable to connect to the registration database.")
    st.stop()

record = df[df["Token"].astype(str) == str(token)]

if record.empty:
    st.error("### Invalid Link")
    st.write("This link is not recognized.")
    st.stop()

# ======================================================
# Get Values
# ======================================================

status = str(record.iloc[0]["Status"]).strip()

try:
    form_type = str(record.iloc[0,5]).strip().upper()
except Exception:
    form_type = "EXTERNAL"

EXTERNAL_FORM = "https://forms.office.com/r/KchEak7FWA?embed=true"

# IMPORTANT:
# No ?embed=true for INTERNAL
INTERNAL_FORM = "https://forms.office.com/r/5s3GA7Df0T"

# ======================================================
# Status Logic
# ======================================================

if status == "Active":

    # Mark token as used
    df.loc[df["Token"].astype(str)==str(token),"Status"] = "Used"
    conn.update(data=df)

    st.success("✅ Identity Verified")

    if form_type == "INTERNAL":

        st.info("""
Your identity has been verified.

Microsoft requires your organization's sign-in page to open outside of embedded pages.

Click the button below to continue.
""")

        st.link_button(
            "Continue to Internal Microsoft Form",
            INTERNAL_FORM,
            use_container_width=True
        )

    else:

        st.toast("Loading External Registration Form...")

        st.components.v1.iframe(
            EXTERNAL_FORM,
            height=1800,
            scrolling=False
        )

        st.caption("⚠️ This is a one-time access link.")

elif status in ["Used", "Terminated"]:

    st.warning("### Link Expired")
    st.write("This registration link has already been used or has expired.")

elif status == "On hold":

    st.info("### Access Pending")
    st.write("This registration link is currently on hold.")

else:

    st.error("### Access Restricted")
    st.write("There is an issue with this registration token.")
