import streamlit as st
import pandas as pd
import numpy as np
import shap
import sqlite3
import bcrypt
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ----------------------------
# DATABASE SETUP
# ----------------------------
conn = sqlite3.connect("academic_ai.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password BLOB
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    attendance INTEGER,
    internal_marks INTEGER,
    gpa REAL,
    backlogs INTEGER,
    risk TEXT,
    timestamp TEXT
)
""")

conn.commit()

# ----------------------------
# CREATE DEFAULT ADMIN USER
# ----------------------------
def create_admin():
    c.execute("SELECT * FROM users WHERE username=?", ("admin",))
    if not c.fetchone():
        hashed_pw = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())
        c.execute("INSERT INTO users VALUES (?,?)", ("admin", hashed_pw))
        conn.commit()

create_admin()

# ----------------------------
# LOGIN SYSTEM
# ----------------------------
def login():
    st.title("🔐 Login to Academic AI System")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        c.execute("SELECT password FROM users WHERE username=?", (username,))
        result = c.fetchone()
        if result and bcrypt.checkpw(password.encode(), result[0]):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid Credentials")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()

# ----------------------------
# AI MODEL
# ----------------------------
st.title("🎓 AI-Enabled Academic Decision Support System")

np.random.seed(42)
data = pd.DataFrame({
    "attendance": np.random.randint(40, 100, 200),
    "internal_marks": np.random.randint(30, 100, 200),
    "gpa": np.random.uniform(4, 10, 200),
    "backlogs": np.random.randint(0, 5, 200),
})

conditions = [
    (data["attendance"] > 75) & (data["gpa"] > 7),
    (data["attendance"] > 60) & (data["gpa"] > 6),
]
choices = [0, 1]
data["risk"] = np.select(conditions, choices, default=2)

X = data.drop("risk", axis=1)
y = data["risk"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestClassifier()
model.fit(X_train, y_train)

accuracy = accuracy_score(y_test, model.predict(X_test))
st.write(f"Model Accuracy: {accuracy:.2f}")

# ----------------------------
# INPUT SECTION
# ----------------------------
st.sidebar.header("Enter Student Details")

attendance = st.sidebar.slider("Attendance (%)", 40, 100, 70)
internal_marks = st.sidebar.slider("Internal Marks", 30, 100, 60)
gpa = st.sidebar.slider("GPA", 4.0, 10.0, 7.0)
backlogs = st.sidebar.slider("Backlogs", 0, 5, 1)

input_data = pd.DataFrame({
    "attendance": [attendance],
    "internal_marks": [internal_marks],
    "gpa": [gpa],
    "backlogs": [backlogs]
})

if st.sidebar.button("Predict"):
    prediction = model.predict(input_data)[0]
    risk_label = ["Low Risk", "Medium Risk", "High Risk"]
    risk = risk_label[prediction]

    st.subheader("Prediction Result")
    st.write(f"Student is: **{risk}**")

    # SAVE TO DATABASE
    c.execute("""
    INSERT INTO predictions 
    (username, attendance, internal_marks, gpa, backlogs, risk, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        st.session_state.username,
        attendance,
        internal_marks,
        gpa,
        backlogs,
        risk,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()

    # SHAP
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(input_data)

    st.subheader("Explainability (Feature Importance)")
    fig, ax = plt.subplots()
    shap.summary_plot(shap_values, input_data, plot_type="bar", show=False)
    st.pyplot(fig)

# ----------------------------
# VIEW HISTORY
# ----------------------------
st.subheader("📜 Prediction History")

c.execute("SELECT * FROM predictions WHERE username=?", (st.session_state.username,))
rows = c.fetchall()

if rows:
    df_history = pd.DataFrame(rows, columns=[
        "ID", "Username", "Attendance", "Internal Marks", "GPA",
        "Backlogs", "Risk", "Timestamp"
    ])
    st.dataframe(df_history)
else:
    st.write("No prediction history found.")

# ----------------------------
# LOGOUT
# ----------------------------
if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()