import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# ----------------------------
# 1. Page Configuration
# ----------------------------
st.set_page_config(
    page_title="Secure Access Portal",
    page_icon="🔐",
    layout="wide"
)

# ----------------------------
# 2. UI Styling
# ----------------------------
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
iframe {border:none;}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# 3. Google Sheets Connection
# ----------------------------
def get_connection():
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception:
        return None

conn = get_connection()

if conn is None:
    st.error("The secure gateway is taking longer than usual to respond. Please refresh.")
    st.stop()

# ----------------------------
# 4. Get Token
# ----------------------------
user_token = st.query_params.get("token")

if not user_token:
    st.error("### Access Required")
    st.write("No security token detected.")
    st.stop()

# ----------------------------
# 5. Read Sheet
# ----------------------------
df = conn.read(ttl=0)

token_data = df[df["Token"].astype(str) == str(user_token)]

if token_data.empty:
    st.error("### Invalid Link")
    st.write("The link is not recognized by our system.")
    st.stop()

# ----------------------------
# 6. Read Values
# ----------------------------
current_status = token_data["Status"].values[0]

try:
    form_type = str(token_data.iloc[0, 5]).upper().strip()
except Exception:
    form_type = "EXTERNAL"

# ----------------------------
# 7. Forms
# ----------------------------
EXTERNAL_FORM = "https://forms.office.com/r/KchEak7FWA?embed=true"

# Removed ?embed=true
INTERNAL_FORM = "https://forms.office.com/r/5s3GA7Df0T"

# ----------------------------
# 8. Status Logic
# ----------------------------
if current_status == "Active":

    # Mark token as used
    df.loc[df["Token"].astype(str) == str(user_token), "Status"] = "Used"
    conn.update(data=df)

    if form_type == "INTERNAL":

        st.success("✅ Identity Verified")
        st.info("Redirecting you to the Microsoft Sign-In page...")

        # Automatic redirect
        st.markdown(
            f"""
            <meta http-equiv="refresh" content="0; url={INTERNAL_FORM}">
            """,
            unsafe_allow_html=True,
        )

        # Backup button in case redirect is blocked
        st.link_button(
            "Continue to Microsoft Form",
            INTERNAL_FORM,
            use_container_width=True,
        )

    else:

        st.success("✅ Identity Verified")
        st.toast("Loading External Form...")

        st.components.v1.iframe(
            EXTERNAL_FORM,
            height=2000,
            scrolling=False,
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
