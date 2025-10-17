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
    /* Overall background */
    .main { 
        background-color: #F8FAFC; /* Soft bluish white */
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #1E293B; /* Dark slate blue-gray for readability */
        text-align: center;
        font-family: 'Inter', sans-serif;
    }

    /* Text inputs, text areas, select boxes */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1; /* Soft gray border */
        border-radius: 8px;
        padding: 10px;
        color: #1E293B;
    }

    /* Primary submit button */
    .stFormSubmitButton button {
        background-color: #3B82F6; /* Medium blue */
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        width: 100%;
        transition: background-color 0.2s ease;
    }

    .stFormSubmitButton button:hover {
        background-color: #2563EB; /* Slightly darker blue on hover */
        color:white;
    }

    /* Secondary button (if any custom button is used) */
    .stButton > button {
        background-color: #E2E8F0; /* Cool gray */
        color: #1E293B;
        border-radius: 8px;
        font-weight: 500;
        border: none;
        padding: 10px 20px;
    }

    .stButton > button:hover {
        background-color: #CBD5E1; /* Slightly darker gray on hover */
    }

    /* Success message box */
    .success-box {
        background-color: #D1FAE5; /* Light green tint */
        color: #065F46; /* Deep green text */
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        margin-top: 20px;
        border: 1px solid #10B981; /* Emerald border */
    }

    /* Error / warning box */
    .error-box {
        background-color: #FEE2E2; /* Light red background */
        color: #991B1B; /* Deep red text */
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        margin-top: 20px;
        border: 1px solid #EF4444;
    }

    /* Secondary text color */
    p, label, span {
        color: #64748B;
        font-family: 'Inter', sans-serif;
    }
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

SHEET_URL = "https://docs.google.com/spreadsheets/d/1nQQXOPZiplwSBYl95F_D8cRaorUOMD3IsRJWVMZspEA/edit" 

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
        name = st.text_input("Full Name*", placeholder="e.g., Mayank Ekbote")
    with col2:
        phone = st.text_input("Phone Number*", placeholder="10 digits only", max_chars=10)

    food = st.text_input("What did you have?*", placeholder="e.g., Dahi Papdi Chat, Veg Chilly Rice")
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
            f'Your feedback has been submitted successfully.</div>',
            unsafe_allow_html=True
        )
