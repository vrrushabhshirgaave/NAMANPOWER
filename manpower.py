import streamlit as st
import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid
import time
import random
import string
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
import os
import shutil
import plotly.express as px
import base64
from datetime import datetime, date
import qrcode
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Connection to Aiven MySQL
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            ssl_ca=os.getenv("MYSQL_SSL_CA"),
        )
        return connection
    except mysql.connector.Error as err:
        st.error(f"Failed to connect to database: {err}")
        return None

def get_base64_image(image_path):
    try:
        ext = os.path.splitext(image_path)[1].lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".avif": "image/avif",
        }
        mime_type = mime_types.get(ext, "image/jpeg")
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        return f"data:{mime_type};base64,{encoded}"
    except FileNotFoundError:
        st.warning(f"Image not found: {image_path}. Using a placeholder instead.")
        placeholder_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        return f"data:image/jpeg;base64,{placeholder_base64}"

# Secure Email Sender Function using smtplib with STARTTLS
def send_email(receiver_email, subject, body):
    sender_email = "namanpowerservices1@outlook.com"
    sender_password = "fizsmbrwdmhjppve"  # Replace with your Outlook app-specific password
    
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    try:
        server = smtplib.SMTP("smtp-mail.outlook.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        st.success("Email sent successfully!")
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

# Generate a Random Password (Plain Text)
def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Generate a Receipt PDF
def generate_receipt(full_name, email, transaction_id, amount):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica", 12)
    
    c.drawString(100, 750, "NA Manpower Services")
    c.drawString(100, 730, "Payment Receipt")
    c.drawString(100, 710, "----------------------------------------")
    
    c.drawString(100, 680, f"Name: {full_name}")
    c.drawString(100, 660, f"Email: {email}")
    c.drawString(100, 640, f"Transaction ID: {transaction_id}")
    c.drawString(100, 620, f"Amount Paid: 150 Rupees")
    c.drawString(100, 600, f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(100, 580, "----------------------------------------")
    c.drawString(100, 560, "Thank you for your payment!")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# Save Resume to Branch-wise Folder
def save_resume(resume, branch, email):
    if resume is None:
        return None
    
    base_dir = "resumes"
    branch_dir = os.path.join(base_dir, branch.replace(" ", "_"))
    
    if not os.path.exists(branch_dir):
        os.makedirs(branch_dir)
    
    filename = f"{email.replace('@', '_')}_{resume.name}"
    file_path = os.path.join(branch_dir, filename)
    
    with open(file_path, "wb") as f:
        f.write(resume.read())
    
    return file_path

# Generate QR Code for Payment
def generate_qr_code(transaction_id):
    upi_id = "9731728337@okbizaxis"
    amount = 150
    transaction_note = f"Job Application Fee - {transaction_id}"
    upi_link = f"upi://pay?pa={upi_id}&pn=NA%20Manpower%20Services&am={amount}&cu=INR&tn={transaction_note}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(upi_link)
    qr.make(fit=True)
    qr_img = qr.make_image(fill="black", back_color="white")
    
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# Placeholder Payment Verification Function (Simulated)
def verify_payment_screenshot(screenshot, transaction_id):
    our_upi_id = "9731728337@okbizaxis"
    expected_amount = 150
    
    extracted_data = {
        "sender_upi": "user@upi",
        "receiver_upi": our_upi_id,
        "amount": 150,
        "transaction_id": transaction_id,
        "utr_id": "123456789012",
        "status": "Payment Completed"
    }
    
    if (extracted_data["receiver_upi"] == our_upi_id and
        extracted_data["amount"] == expected_amount and
        extracted_data["transaction_id"] == transaction_id and
        extracted_data["status"] == "Payment Completed"):
        return True, "Payment Verified"
    else:
        return False, "Payment verification failed: Details do not match."

# Streamlit UI
def main():
    st.set_page_config(page_title="Manpower Management", layout="wide")
    st.markdown(
        """
        <style>
            header {visibility: hidden;}
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stApp {
                margin: 0;
                padding: 0;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.sidebar:
        st.image("images/NA_Logo.png", width=150)
        st.markdown("---")
        menu = ["Home", "Job Application Form", "Services & Companies", "About Us", "Feedback & Testimonials", "Login"]
        for item in menu:
            if st.button(item, key=f"menu_{item}"):
                st.session_state["page"] = item

    if "page" not in st.session_state:
        st.session_state["page"] = "Home"

    if st.session_state["page"] == "Home":
        home_page()
    elif st.session_state["page"] == "Job Application Form":
        careers_page()
    elif st.session_state["page"] == "Services & Companies":
        servicesandcomapnies_page()
    elif st.session_state["page"] == "About Us":
        about_page()
    elif st.session_state["page"] == "Feedback & Testimonials":
        feedback_page()
    elif st.session_state["page"] == "Login":
        login_page()

def home_page():
    background_image_base64 = get_base64_image("images/bg_home_page.avif")
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-color: white;
            }}
            .card-container {{
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 20px;
                padding: 20px;
            }}
            .card {{
                border: 1px solid #ddd;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                width: 100%;
                height: 250px;
                background-color: #FFAC1C;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                margin-top: 70px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                transition: transform 0.3s ease-in-out;
            }}
            .card:hover {{
                transform: translateY(-10px) scale(1.05);
                box-shadow: 4px 4px 15px rgba(0,0,0,0.2);
            }}
            .card img {{
                width: 170px;
                height: 120px;
                margin: 0 auto;
            }}
            .card h4, .card p {{
                color: black;
                margin: 10px 0;
            }}
            .card h4 {{
                font-size: 1.2rem;
                font-weight: bold;
            }}
            .card p {{
                font-size: 0.9rem;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                background-color: blue;
                color: white;
                position: fixed;
                bottom: 0;
                left: 0;
                width: 100%;
            }}
            .footer a {{
                color: white;
                text-decoration: none;
                margin: 0 10px;
            }}
            .header-container {{
                display: flex;
                justify-content: center;
                align-items: center;
                width: 100vw;
                height: 50vh;
                background-image: url('{background_image_base64}');
                background-size: cover;
                background-position: left center;
                background-repeat: no-repeat;
                position: relative;
                margin-left: calc(-50vw + 50%);
                margin-right: calc(-50vw + 50%);
                margin-top: 0 !important;
                padding-top: 0 !important;
            }}
            .header-text {{
                position: relative;
                text-align: center !important;
                color: #ffffff !important;
                margin: 0 auto !important;
                font-size: 3rem !important;
                font-weight: 700 !important;
                text-transform: uppercase !important;
                letter-spacing: 2px !important;
                padding: 20px 40px 20px 80px !important;
                z-index: 1 !important;
                display: inline-block !important;
            }}
            .header-text::before {{
                content: '';
                position: absolute;
                top: 0;
                left: -30px;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.7) !important;
                backdrop-filter: blur(5px) !important;
                -webkit-backdrop-filter: blur(5px) !important;
                z-index: -1;
            }}
            .description-text {{
                text-align: center !important;
                color: black !important;
                margin: 40px auto 20px auto !important;
                font-size: 1rem !important;
                width: 100% !important;
                max-width: 100% !important;
            }}
            @media (max-width: 768px) {{
                .header-container {{
                    height: 40vh !important;
                    background-position: left center !important;
                }}
                .header-text {{
                    font-size: 2rem !important;
                    padding: 15px 30px 15px 60px !important;
                }}
                .header-text::before {{
                    left: -60px !important;
                }}
                .description-text {{
                    font-size: 0.9rem !important;
                    margin: 30px auto 15px auto !important;
                }}
                .card {{
                    width: 100%;
                    height: 230px;
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="header-container">
            <h1 class="header-text"><b> NA Manpower Services </b></h1>
        </div>
        <p class="description-text"><b>Connecting the right talent with the right opportunities!</b></p>
        """,
        unsafe_allow_html=True
    )

    card_data = [
        {"title": "Job Opportunities", "desc": "Find the best job opportunities across industries.", "image": get_base64_image("images/job_opportunities_homepage_card1.png")},
        {"title": "Resume Services", "desc": "Get professional resume building services.", "image": get_base64_image("images/resume_services_homepage_card2.jpg")},
        {"title": "Career Counseling", "desc": "Expert advice to shape your career path.", "image": get_base64_image("images/career_counseling_homepage_card3.png")},
        {"title": "Employee Hiring", "desc": "We help companies hire the right talent.", "image": get_base64_image("images/Employee_hiring_homepage_card4.avif")},
        {"title": "Training & Development", "desc": "Skill enhancement programs for job seekers.", "image": get_base64_image("images/training_and_development_homepage_card5.jpg")},
        {"title": "Industry Connect", "desc": "Network with industry experts and recruiters.", "image": get_base64_image("images/industry_connect_homepage_card6.avif")}
    ]

    cols = st.columns(3)
    for i in range(3):
        with cols[i]:
            card = card_data[i]
            st.markdown(
                f"""
                <div class="card">
                    <img src="{card['image']}" alt="Icon">
                    <h4>{card['title']}</h4>
                    <p>{card['desc']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    cols = st.columns(3)
    for i in range(3, 6):
        with cols[i - 3]:
            card = card_data[i]
            st.markdown(
                f"""
                <div class="card">
                    <img src="{card['image']}" alt="Icon">
                    <h4>{card['title']}</h4>
                    <p>{card['desc']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        """
        <div class="footer">
            <p> Contact Us : <a href="mailto:namanpowerservices1@outlook.com">namanpowerservices1@outlook.com</a></p>
            <p>
                <a href="https://www.facebook.com/share/15yQBjawRp/" target="_blank">Facebook</a> |
                <a href="https://www.instagram.com/nikitrajaguru?igsh=NndmYmIxcWMxNW53" target="_blank">Instagram</a> |
                <a href="https://youtube.com/@nikitrajagurumaradi?si=QfK0HNb_Gp7wkpEZ" target="_blank">Youtube</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def careers_page():
    st.subheader("Job Registration Form")
    
    with st.form("job_form"):
        full_name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        pan_aadhar = st.text_input("PAN/Aadhar")
        
        current_year = datetime.now().year
        dob = st.date_input(
            "Date of Birth",
            min_value=date(1931, 1, 1),
            max_value=date(current_year, 12, 31),
            value=date(2000, 1, 1)
        )
        
        resume = st.file_uploader("Upload Resume", type=["pdf", "docx"])
        cover_letter = st.file_uploader("Upload Cover Letter", type=["pdf", "docx"])
        job_industry = st.selectbox("Job Industry", ["Select Job type", "IT (Technical And Non Technical)", "Mechanical (Diploma/Degree)", "Electrical (Diploma/Degree)", "Hospitality & Hotel Management", "Nursing", "Security & Guards", "BPO", "ITI(any trade)", "Electronics (Diploma/Degree)", "Caretaker/Guardian", "Welder/fitter/turner/helper", "Backoffice", "CNC/VMC Operator or Programmer", "Accountant & finance", "Sales & Marketing", "HR", "Other"])
        
        transaction_id = str(uuid.uuid4())[:8]
        transaction_note = f"Job Application Fee - {transaction_id}"
        amount = 150
        
        st.markdown(
            f"""
            <p style='text-align: center; color: black;'>
                Scan the QR code below to make the payment of <b>150 Rupees</b>.<br>
                Transaction Note (for reference): <strong>{transaction_note}</strong>
            </p>
            """,
            unsafe_allow_html=True
        )
        
        qr_buffer = generate_qr_code(transaction_id)
        st.image(qr_buffer, caption="Scan this QR code to pay 150 Rupees", width=200)
        
        screenshot = st.file_uploader("Upload Payment Screenshot", type=["png", "jpg", "jpeg"])
        
        submit_button = st.form_submit_button("Submit & Verify Payment")

        if submit_button:
            if not full_name or not email or not phone or not pan_aadhar or job_industry == "Select Job type" or not screenshot:
                st.error("All fields, including payment screenshot, are required!")
            else:
                st.info("Verifying payment screenshot...")
                payment_verified, verification_message = verify_payment_screenshot(screenshot, transaction_id)
                
                if payment_verified:
                    resume_path = save_resume(resume, job_industry, email)
                    username = email
                    raw_password = generate_random_password()
                    
                    conn = get_db_connection()
                    if conn is None:
                        return
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO candidates (full_name, email, phone, pan_aadhar, dob, job_industry, payment_status, username, password, transaction_id, resume_path) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                        (full_name, email, phone, pan_aadhar, dob, job_industry, True, username, raw_password, transaction_id, resume_path)
                    )
                    
                    cursor.execute(
                        "INSERT INTO users (username, password, role) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE password=%s",
                        (username, raw_password, "Candidate", raw_password)
                    )
                    
                    conn.commit()
                    conn.close()
                    
                    email_subject = "NA Manpower Services - Your Login Credentials"
                    email_body = f"""
                    Dear {full_name},

                    Thank you for registering with NA Manpower Services. Your job application has been successfully submitted.

                    Here are your login credentials:
                    Username: {username}
                    Password: {raw_password}

                    Please use these credentials to log in to your account at NA Manpower Services.

                    Best regards,
                    NA Manpower Services Team
                    """
                    if send_email(email, email_subject, email_body):
                        st.success("An email with your login credentials has been sent to your email address.")
                    else:
                        st.warning("Failed to send login credentials via email. Please contact support.")
                    
                    st.success("Job Application Submitted Successfully!")
                    st.markdown(
                        """
                        <p style='color: green; text-align: center; font-weight: bold;'>
                            Fees: 150 Rupees Only
                        </p>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.error(verification_message)

def admin_dashboard():
    st.subheader("Admin Dashboard")
    
    conn = get_db_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, email, phone, pan_aadhar, dob, job_industry, payment_status, transaction_id FROM candidates")
    candidates = cursor.fetchall()
    conn.close()
    
    branch_data = {}
    for candidate in candidates:
        branch = candidate[5]
        if branch not in branch_data:
            branch_data[branch] = []
        branch_data[branch].append({
            "Full Name": candidate[0],
            "Email": candidate[1],
            "Phone": candidate[2],
            "PAN/Aadhar": candidate[3],
            "Date of Birth": candidate[4],
            "Job Industry": candidate[5],
            "Payment Status": "Paid" if candidate[6] else "Not Paid",
            "Transaction ID": candidate[7]
        })
    
    st.markdown("### Candidate Data by Branch")
    for branch, data in branch_data.items():
        st.markdown(f"#### {branch}")
        df = pd.DataFrame(data)
        st.dataframe(df)
        
        csv = df.to_csv(index=False)
        st.download_button(
            label=f"Download {branch} Data as CSV",
            data=csv,
            file_name=f"{branch}_candidates.csv",
            mime="text/csv"
        )
        
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)
        st.download_button(
            label=f"Download {branch} Data as XLSX",
            data=buffer,
            file_name=f"{branch}_candidates.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    st.markdown("### All Job Postings")
    conn = get_db_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute("SELECT title, description, branch, posted_by, created_at FROM job_postings")
    job_postings = cursor.fetchall()
    conn.close()
    
    if job_postings:
        job_data = [{
            "Title": jp[0],
            "Description": jp[1],
            "Branch": jp[2],
            "Posted By": jp[3],
            "Created At": jp[4]
        } for jp in job_postings]
        st.dataframe(pd.DataFrame(job_data))
    else:
        st.write("No job postings available.")

def hr_hiring_dashboard(username):
    st.subheader("HR (Hiring) Dashboard")
    
    st.markdown("### Post a New Job")
    with st.form("job_posting_form"):
        title = st.text_input("Job Title")
        description = st.text_area("Job Description")
        branch = st.selectbox("Branch", ["IT (Technical And Non Technical)", "Mechanical (Diploma/Degree)", "Electrical (Diploma/Degree)", "Hospitality & Hotel Management", "Nursing", "Security & Guards", "BPO", "ITI(any trade)", "Electronics (Diploma/Degree)", "Caretaker/Guardian", "Welder/fitter/turner/helper", "Backoffice", "CNC/VMC Operator or Programmer", "Accountant & finance", "Sales & Marketing", "HR", "Other"])
        submit_job = st.form_submit_button("Post Job")
        
        if submit_job:
            if not title or not description:
                st.error("All fields are required!")
            else:
                conn = get_db_connection()
                if conn is None:
                    return
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO job_postings (title, description, branch, posted_by) VALUES (%s, %s, %s, %s)",
                    (title, description, branch, username)
                )
                conn.commit()
                conn.close()
                st.success("Job posted successfully!")
    
    st.markdown("### Your Job Postings")
    conn = get_db_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute("SELECT title, description, branch, created_at FROM job_postings WHERE posted_by=%s", (username,))
    job_postings = cursor.fetchall()
    conn.close()
    
    if job_postings:
        job_data = [{
            "Title": jp[0],
            "Description": jp[1],
            "Branch": jp[2],
            "Created At": jp[3]
        } for jp in job_postings]
        st.dataframe(pd.DataFrame(job_data))
    else:
        st.write("No job postings available.")

def login_page():
    st.subheader("User Login")
    role = st.selectbox("Select Role", ["Candidate", "HR (Manpower)", "HR (Hiring)", "Admin"], key="role_select")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    login_button = st.button("Login", key="login_button")

    if login_button:
        conn = get_db_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=%s AND role=%s", (username, role))
        result = cursor.fetchone()

        if result and result[0] == password:
            if role == "Candidate":
                cursor.execute(
                    "SELECT full_name, email, phone, pan_aadhar, dob, job_industry, payment_status, transaction_id FROM candidates WHERE username=%s", 
                    (username,)
                )
                candidate_result = cursor.fetchone()
                
                if candidate_result:
                    payment_status = candidate_result[6]
                    if payment_status:
                        st.session_state["logged_in"] = True
                        st.session_state["role"] = role
                        st.session_state["username"] = username
                        st.session_state["candidate_data"] = candidate_result
                        st.success(f"Welcome {role}")
                    else:
                        st.error("Payment not verified. Please complete the payment and submit the form.")
                else:
                    st.error("Form not submitted. Please submit the job application form first.")
            else:
                st.session_state["logged_in"] = True
                st.session_state["role"] = role
                st.session_state["username"] = username
                st.success(f"Welcome {role}")
        else:
            st.error("Invalid Credentials")
        
        conn.close()

    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        if st.session_state["role"] == "Candidate":
            st.subheader("Candidate Dashboard")
            candidate_data = st.session_state["candidate_data"]
            full_name, email, phone, pan_aadhar, dob, job_industry, payment_status, transaction_id = candidate_data
            
            st.markdown("### Your Submitted Form Details")
            st.write(f"**Full Name:** {full_name}")
            st.write(f"**Email:** {email}")
            st.write(f"**Phone Number:** {phone}")
            st.write(f"**PAN/Aadhar:** {pan_aadhar}")
            st.write(f"**Date of Birth:** {dob}")
            st.write(f"**Job Industry:** {job_industry}")
            
            st.markdown("### Download Payment Receipt")
            receipt_buffer = generate_receipt(full_name, email, transaction_id, 150)
            st.download_button(
                label="Download Receipt",
                data=receipt_buffer,
                file_name=f"payment_receipt_{transaction_id}.pdf",
                mime="application/pdf"
            )
        
        elif st.session_state["role"] == "Admin":
            admin_dashboard()
        
        elif st.session_state["role"] == "HR (Hiring)":
            hr_hiring_dashboard(st.session_state["username"])

def feedback_page():
    st.subheader("Feedback & Testimonials")

    # Custom CSS for styling
    st.markdown(
        """
        <style>
            .star-rating {
                display: flex;
                justify-content: center;
                gap: 10px;
                margin-bottom: 20px;
            }
            .star {
                font-size: 2rem;
                color: #ddd;
                cursor: pointer;
            }
            .star.filled {
                color: #FFD700;
            }
            .feedback-container {
                border: 1px solid #ddd;
                padding: 15px;
                border-radius: 10px;
                margin-top: 20px;
                background-color: #f9f9f9;
            }
            .feedback-item p {
                margin: 5px 0;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Feedback submission (only for logged-in Candidates)
    if "logged_in" in st.session_state and st.session_state["logged_in"] and st.session_state["role"] == "Candidate":
        username = st.session_state["username"]
        conn = get_db_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM candidates WHERE username=%s AND payment_status=TRUE", (username,))
        form_submitted = cursor.fetchone()[0] > 0
        conn.close()

        if not form_submitted:
            st.error("You must submit the job application form and complete payment before providing feedback.")
        else:
            st.markdown("### Submit Your Feedback")
            with st.form("feedback_form"):
                if "rating" not in st.session_state:
                    st.session_state["rating"] = 0

                rating_html = "<div class='star-rating'>"
                for i in range(1, 6):
                    filled = "filled" if i <= st.session_state["rating"] else ""
                    rating_html += f"<span class='star {filled}' onclick='st.session_state.rating={i}'>★</span>"
                rating_html += "</div>"
                st.markdown(rating_html, unsafe_allow_html=True)
                
                rating = st.slider("Rate us (1-5)", 1, 5, st.session_state["rating"])
                st.session_state["rating"] = rating

                comment = st.text_area("Your Feedback", max_chars=500)
                submit_button = st.form_submit_button("Submit Feedback")

                if submit_button:
                    if st.session_state["rating"] == 0:
                        st.error("Please provide a rating!")
                    else:
                        conn = get_db_connection()
                        if conn is None:
                            return
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO feedback (username, rating, comment) VALUES (%s, %s, %s)",
                            (username, st.session_state["rating"], comment)
                        )
                        conn.commit()
                        conn.close()
                        st.success("Feedback submitted successfully!")
                        st.session_state["rating"] = 0

    else:
        if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
            st.info("Please log in as a Candidate to submit feedback.")
        elif st.session_state["role"] != "Candidate":
            st.info("Only Candidates can submit feedback.")

    # Display Submitted Feedback (visible to all, with shortened name)
    st.markdown("### Submitted Feedback")
    conn = get_db_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT f.username, f.rating, f.comment, f.submitted_at, c.full_name 
        FROM feedback f
        LEFT JOIN candidates c ON f.username = c.username
        ORDER BY f.submitted_at DESC
        """
    )
    feedbacks = cursor.fetchall()
    conn.close()

    if feedbacks:
        for feedback in feedbacks:
            username, rating, comment, submitted_at, full_name = feedback
            # Shorten the full_name (e.g., "John Doe" -> "J. Doe")
            if full_name:
                name_parts = full_name.split()
                if len(name_parts) >= 2:
                    display_name = f"{name_parts[0][0]}. {name_parts[-1]}"
                else:
                    display_name = name_parts[0] if name_parts else "Anonymous"
            else:
                display_name = "Anonymous"
            
            stars = "★" * rating + "☆" * (5 - rating)
            st.markdown(
                f"""
                <div class="feedback-container">
                    <p><b>User:</b> {display_name}</p>
                    <p><b>Rating:</b> {stars} ({rating}/5)</p>
                    <p><b>Comment:</b> {comment}</p>
                    <p><b>Submitted:</b> {submitted_at}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.write("No feedback submitted yet.")
        
def servicesandcomapnies_page():
    st.subheader("Our Stats and Hiring")
    st.markdown(
        """
        <style>
            .card {
                border: 1px solid #ddd;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                width: 100%;
                height: 250px;
                background-color: #FFAC1C;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                margin-bottom: 70px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                transition: transform 0.3s ease-in-out;
            }
            .card:hover {
                transform: translateY(-10px) scale(1.05);
                box-shadow: 4px 4px 15px rgba(0,0,0,0.2);
            }
            .card h4, .card p {
                color: black;
                margin: 10px 0;
            }
            .card h4 {
                font-size: 1.2rem;
                font-weight: bold;
            }
            .card p {
                font-size: 0.9rem;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    companies_data = [
        {"name": "IT Hiring", "desc": "Leading IT firm with 100% job placement for software engineers.", "hiring_stat": "Hired 250 candidates in 2024"},
        {"name": "Mechanical & Industrial Hiring", "desc": "Top mechanical engineering company offering guaranteed placements.", "hiring_stat": "Hired 180 candidates in 2024"},
        {"name": "HealthCare Hiring", "desc": "Premier healthcare provider with 100% placement for nurses.", "hiring_stat": "Hired 300 candidates in 2024"},
        {"name": "Electrical Hiring", "desc": "Electrical engineering leader with excellent job opportunities.", "hiring_stat": "Hired 150 candidates in 2024"},
        {"name": "Hospitality Hiring", "desc": "Luxury hotel chain with 100% placement in hospitality roles.", "hiring_stat": "Hired 200 candidates in 2024"},
        {"name": "BPO Hiring", "desc": "Top BPO firm offering secure jobs with 100% placement.", "hiring_stat": "Hired 220 candidates in 2024"}
    ]

    cols = st.columns(3)
    for i in range(3):
        with cols[i]:
            company = companies_data[i]
            st.markdown(
                f"""
                <div class="card">
                    <h4>{company['name']}</h4>
                    <p>{company['desc']}</p>
                    <p><b>{company['hiring_stat']}</b></p>
                </div>
                """,
                unsafe_allow_html=True
            )

    cols = st.columns(3)
    for i in range(3, 6):
        with cols[i - 3]:
            company = companies_data[i]
            st.markdown(
                f"""
                <div class="card">
                    <h4>{company['name']}</h4>
                    <p>{company['desc']}</p>
                    <p><b>{company['hiring_stat']}</b></p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("### Hiring Statistics (2024)")
    hiring_data = {
        "Company": [company["name"] for company in companies_data],
        "Candidates Hired": [int(company["hiring_stat"].split()[1]) for company in companies_data]
    }
    df = pd.DataFrame(hiring_data)
    
    fig = px.pie(
        df,
        values="Candidates Hired",
        names="Company",
        title="Candidates Hired by Partner Companies in 2024",
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    fig.update_traces(textinfo="percent+label", pull=[0.1, 0, 0, 0, 0, 0])
    fig.update_layout(showlegend=True, margin=dict(t=50, b=50, l=50, r=50), height=500)
    st.plotly_chart(fig, use_container_width=True)

def about_page():
    st.subheader("About NA Manpower Services")
    st.markdown(
        """
        <style>
            .big-card {
                border: 2px solid #ddd;
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                width: 100%;
                max-width: 600px;
                margin: 20px auto;
                background-color: #FFAC1C;
                box-shadow: 4px 4px 10px rgba(0,0,0,0.2);
                animation: popUp 0.8s ease-out forwards;
            }
            .big-card h4 {
                color: black;
                font-size: 1.5rem;
                font-weight: bold;
                margin-bottom: 20px;
            }
            .big-card p {
                color: black;
                font-size: 1.1rem;
                margin: 10px 0;
            }
            .big-card p i {
                margin-right: 10px;
                color: #333;
            }
            @keyframes popUp {
                0% { transform: scale(0.9) translateY(20px); opacity: 0; }
                100% { transform: scale(1) translateY(0); opacity: 1; }
            }
            .carousel-container {
                width: 100%;
                overflow: hidden;
                margin-top: 30px;
                position: relative;
            }
            .carousel {
                display: flex;
                animation: scroll-left 20s linear infinite;
                white-space: nowrap;
            }
            .carousel img {
                width: 400px;
                height: 400px;
                margin-right: 20px;
                border-radius: 10px;
                object-fit: cover;
            }
            @keyframes scroll-left {
                0% { transform: translateX(0); }
                100% { transform: translateX(-100%); }
            }
            .carousel:hover {
                animation-play-state: paused;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="big-card">
            <h4>Contact Information</h4>
            <p><b>Address:</b> #6, 17th Cross, 2nd Main, Jayanagar, Opp. Shri Ram Mandira , Mysore,Karnataka, India</p>
            <p><i>✉</i> Email: namanpowerservices1@outlook.com </p>
            <p><i>📞</i> Contact: +91 9071062229</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Our Journey - Image Gallery")
    image_urls = [
        get_base64_image("images/carousel_image1.jpg"),
        get_base64_image("images/carousel_image2.jpg"),
        get_base64_image("images/carousel_image3.jpg"),
        get_base64_image("images/carousel_image4.jpg"),
        get_base64_image("images/carousel_image5.jpg"),
        get_base64_image("images/carousel_image6.jpg"),
        get_base64_image("images/carousel_image7.jpg"),
        get_base64_image("images/carousel_image8.jpg"),
    ]
    if image_urls:
        image_urls_extended = image_urls + image_urls
        carousel_html = '<div class="carousel-container"><div class="carousel">'
        for url in image_urls_extended:
            carousel_html += f'<img src="{url}" alt="Carousel Image">'
        carousel_html += '</div></div>'
        st.markdown(carousel_html, unsafe_allow_html=True)
    else:
        st.write("No images available for the gallery.")

if __name__ == "__main__":
    main()