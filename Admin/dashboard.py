import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets API scope
SCOPE = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

# Load credentials from Streamlit secrets
gcp_creds = st.secrets["gcp"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(gcp_creds, SCOPE)
client = gspread.authorize(creds)

# Open your Google Sheet by URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1nQQXOPZiplwSBYl95F_D8cRaorUOMD3IsRJWVMZspEA/edit"
spreadsheet = client.open_by_url(SHEET_URL)

# Access each worksheet
pos_sheet = spreadsheet.worksheet("positive_reviews")
neg_sheet = spreadsheet.worksheet("negative_reviews")

# Convert to DataFrame
df_pos = pd.DataFrame(pos_sheet.get_all_records())
df_neg = pd.DataFrame(neg_sheet.get_all_records())

# Streamlit UI
st.title("Customer Reviews Dashboard")

tab1, tab2 = st.tabs(["🟩 Positive Reviews", "🟥 Negative Reviews"])

with tab1:
    st.subheader("Positive Reviews")
    st.dataframe(df_pos)

with tab2:
    st.subheader("Negative Reviews")
    st.dataframe(df_neg)
