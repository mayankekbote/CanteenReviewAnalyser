import streamlit as st
import pickle
import pandas as pd
from datetime import datetime
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ----------------------------
# CONFIG & STYLING
# ----------------------------
st.set_page_config(
    page_title="🍽️ VIT Canteen Feedback",
    page_icon="🍴",
    layout="centered"
)

st.markdown("""
<style>
    .main { background-color: #fdf6f0; }
    h1 { color: #8B4513; text-align: center; font-family: 'Georgia', serif; }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input {
        background-color: #fff8f0; border: 1px solid #d7ccc8; border-radius: 8px; padding: 10px;
    }
    .stFormSubmitButton button {
        background-color: #8B4513; color: white; border: none; border-radius: 8px; padding: 12px 24px; font-weight: bold; width: 100%;
    }
    .stFormSubmitButton button:hover { background-color: #A1887F; }
    .success-box { background-color: #e8f5e9; color: #2e7d32; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# LOAD MODELS
# ----------------------------
@st.cache_resource
def load_models():
    with open('linear_svc_model.pkl', 'rb') as f:
        classifier = pickle.load(f)
    with open('tfidf_vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    return classifier, vectorizer

classifier, vectorizer = load_models()

# ----------------------------
# GOOGLE SHEETS CONNECTION USING SECRETS
# ----------------------------
SCOPE = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

# Load GCP service account from Streamlit secrets
gcp_creds = st.secrets["gcp"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(gcp_creds, SCOPE)
client = gspread.authorize(creds)

SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"  # Replace YOUR_SHEET_ID

def append_to_gsheet(sheet_name, data_dict):
    """Append a new feedback entry to the specified Google Sheet tab."""
    try:
        sheet = client.open_by_url(SHEET_URL).worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        # create sheet if it doesn't exist
        sheet = client.open_by_url(SHEET_URL).add_worksheet(title=sheet_name, rows="1000", cols="20")
        sheet.append_row(["Name", "Phone", "Food", "Date", "Review"])
    
    # Append the new row
    sheet.append_row([data_dict["Name"], data_dict["Phone"], data_dict["Food"], data_dict["Date"], data_dict["Review"]])

# ----------------------------
# HELPERS
# ----------------------------
def is_valid_phone(phone):
    return bool(re.fullmatch(r'\d{10}', phone))

def predict_sentiment(text):
    X = vectorizer.transform([text]).toarray()
    pred = classifier.predict(X)[0]
    return "Positive" if pred == 1 else "Negative"

# ----------------------------
# MAIN APP
# ----------------------------
st.title("🍽️ VIT Canteen Feedback")
st.write("We'd love to hear about your dining experience!")

# Feedback form
with st.form("feedback_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name*", placeholder="e.g., Maria Garcia")
    with col2:
        phone = st.text_input("Phone Number*", placeholder="10 digits only", max_chars=10)

    food = st.text_input("What did you have?*", placeholder="e.g., Truffle Pasta, Tiramisu")
    date_of_visit = st.date_input("Date of Visit*", max_value=datetime.today(), min_value=datetime(2020,1,1))
    review = st.text_area("Your Review*", height=120, help="Be honest! We read every review.")

    submitted = st.form_submit_button("Submit Feedback")

# ----------------------------
# FORM HANDLING
# ----------------------------
if submitted:
    errors = []
    if not name.strip(): errors.append("❌ Full Name is required.")
    if not is_valid_phone(phone): errors.append("❌ Phone must be exactly 10 digits.")
    if not food.strip(): errors.append("❌ Please tell us what you ordered.")
    if date_of_visit > datetime.today().date(): errors.append("❌ Visit date can't be in the future.")
    if not review.strip(): errors.append("❌ We'd love to hear your thoughts!")

    if errors:
        for err in errors: st.error(err)
    else:
        sentiment = predict_sentiment(review)
        sheet_name = "positive_reviews" if sentiment == "Positive" else "negative_reviews"

        new_entry = {
            "Name": name,
            "Phone": phone,
            "Food": food,
            "Date": date_of_visit.strftime("%Y-%m-%d"),
            "Review": review
        }

        append_to_gsheet(sheet_name, new_entry)

        st.markdown(
            f'<div class="success-box">🙌 Thank you, {name.split()[0] if name else "guest"}!<br>'
            f'Your {sentiment.lower()} feedback has been submitted successfully.</div>',
            unsafe_allow_html=True
        )
