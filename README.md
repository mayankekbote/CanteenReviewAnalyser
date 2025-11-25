

# 🍽️ VIT Canteen Feedback Analyzer

A smart, sentiment-powered feedback collection system for VIT students and staff.
This Streamlit app collects feedback, analyzes sentiment using a **Linear SVC model**, and stores all entries in **Google Sheets** for real-time monitoring.

🔗 **Live App:** [https://canteenreviewanalyser.streamlit.app/](https://canteenreviewanalyser.streamlit.app/)

---

# 🚀 How to Run This Project Locally

### **1️⃣ Clone the repository**

```bash
git clone <your-repo-url>
cd <repo-folder>
```

### **2️⃣ Create & activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### **3️⃣ Install dependencies**

```bash
pip install -r requirements.txt
```

### **4️⃣ Add Google Cloud credentials**

Create a `secrets.toml` file inside `.streamlit/`:

```
# .streamlit/secrets.toml
[gcp]
type = "service_account"
project_id = "your-project"
private_key_id = "xxxx"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "xxxx@xxxx.gserviceaccount.com"
client_id = "xxxx"
...
```

Make sure the service account has **Editor** access to the target Google Sheet.

### **5️⃣ Ensure required ML files are present**

The root folder must contain:

```
linear_svc_model.pkl  
tfidf_vectorizer.pkl  
```

### **6️⃣ Run the app**

```bash
streamlit run app.py
```

The site will open automatically at:

```
http://localhost:8501
```

---

# 🌟 Project Overview

This project empowers VIT students to submit canteen reviews while automatically analyzing their sentiment—**Positive** or **Negative**—using a trained machine learning model.

Every review is categorized and stored in separate Google Sheet tabs:

* `positive_reviews`
* `negative_reviews`

It helps food management teams understand student satisfaction, track trends, and improve service quality.

---

# 🧠 Machine Learning Details

### ✔ **Model Used: Linear SVC (Support Vector Classifier)**

* Effective for text classification
* Works well with TF-IDF feature vectors
* High accuracy for short review sentences

### ✔ **NLP Pipeline**

* **TF-IDF Vectorizer** converts text into numerical features
* **Linear SVC** predicts sentiment (Positive / Negative)

### ✔ Skills Used

* Text preprocessing and cleaning
* Vectorization with TF-IDF
* Sentiment classification
* Model serialization using `pickle`
* Real-time inference in Streamlit

---

# 🗂️ Google Sheets Integration (Live Database)

The app connects to Google Sheets using:

* `gspread`
* `oauth2client.service_account.ServiceAccountCredentials`
* Streamlit **secrets** for secure credential handling

Each feedback entry includes:

| Field     | Description           |
| --------- | --------------------- |
| Name      | User’s full name      |
| Phone     | Valid 10-digit number |
| Food      | Item ordered          |
| Date      | Visit date            |
| Review    | Feedback text         |
| Sentiment | Computed internally   |

Entries are automatically saved to the correct sheet tab.

---

# 🎨 UI/UX Features (Streamlit)

### Rich Custom Styling

The app includes a modern theme:

* Clean pastel backgrounds
* Slate-colored headings
* Soft borders & rounded inputs
* Beautiful success/error message boxes

### Smooth User Experience

* Validations for required fields
* Real-time sentiment analysis
* Auto-routing of feedback to correct sheet
* Mobile-friendly design

### Form Inputs

Users provide:

* Name
* Phone
* Food item
* Date of visit
* Review text

The app handles validation, prediction, and storage.

---

# 📁 Project Structure

```
📂 project-root
│── app.py                          # Main Streamlit application
│── linear_svc_model.pkl            # Sentiment ML model
│── tfidf_vectorizer.pkl            # TF-IDF vectorizer
│── requirements.txt
│── README.md
│── .streamlit/
│     └── secrets.toml              # GCP service account credentials
```

---

# 🛠 Tech Stack

### **Frontend/UI**

* Streamlit
* Custom CSS
* Responsive layout

### **Backend**

* Python
* Regex validation
* GSpread API

### **ML/NLP**

* Scikit-learn
* Linear SVC
* TF-IDF Vectorizer
* Pickle

### **Cloud Services**

* Google Sheets API
* GCP Service Account integration

---

# 📌 Future Improvements

* Dashboard for feedback analytics
* Review filtering & search
* Admin-only moderation system
* Multi-class sentiment (positive/neutral/negative)
* Add food-item satisfaction rating charts

---

# 🤝 Contributing

Contributions, bug reports, and feature ideas are welcome!


