import streamlit as st
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
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

# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="manpower_user",
        password="root",
        database="manpower_db"
    )

def get_base64_image(image_path):
    try:
        # Determine the MIME type based on the file extension
        ext = os.path.splitext(image_path)[1].lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".avif": "image/avif",
        }
        mime_type = mime_types.get(ext, "image/jpeg")  # Default to JPEG if unknown
        
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        return f"data:{mime_type};base64,{encoded}"
    except FileNotFoundError:
        st.warning(f"Image not found: {image_path}. Using a placeholder instead.")
        placeholder_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        return f"data:image/jpeg;base64,{placeholder_base64}"

# Email Sender Function
def send_email(receiver_email, subject, body):
    sender_email = "your_email@gmail.com"  # Replace with your email
    sender_password = "your_email_password"  # Replace with your email password (App Password for Gmail)
    
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

# Generate a Random Password
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
    
    # Define the base directory for resumes
    base_dir = "resumes"
    branch_dir = os.path.join(base_dir, branch.replace(" ", "_"))  # Replace spaces with underscores
    
    # Create the branch directory if it doesn't exist
    if not os.path.exists(branch_dir):
        os.makedirs(branch_dir)
    
    # Define the file path (use email to make the filename unique)
    filename = f"{email.replace('@', '_')}_{resume.name}"
    file_path = os.path.join(branch_dir, filename)
    
    # Save the resume file
    with open(file_path, "wb") as f:
        f.write(resume.read())
    
    return file_path

# Streamlit UI
def main():
    st.set_page_config(page_title="Manpower Management", layout="wide")
    st.markdown(
        """
        <style>
            /* Hide the Streamlit top bar */
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .stApp {
                margin-top: -18px; /* Adjust to remove the empty space left by the hidden header */
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    # Sidebar with Logo and Vertical Menu
    with st.sidebar:
        st.image("images/NA_Logo.png", width=150)
        st.markdown("---")
        menu = ["Home", "Job Application Form", "Services & Companies", "About Us", "Login"]
        for item in menu:
            if st.button(item, key=f"menu_{item}"):
                st.session_state["page"] = item

    # Default Page Handling
    if "page" not in st.session_state:
        st.session_state["page"] = "Home"

    # Page Routing
    if st.session_state["page"] == "Home":
        home_page()
    elif st.session_state["page"] == "Job Application Form":
        careers_page()
    elif st.session_state["page"] == "Services & Companies":
        servicesandcomapnies_page()
    elif st.session_state["page"] == "About Us":
        about_page()
    elif st.session_state["page"] == "Login":
        login_page()

def home_page():
    # Encode the background image
    background_image_base64 = get_base64_image("images/bg_home_page.avif")

    # Updated CSS with the local background image
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
                transition: transform 0.3s ease-in-out; /* Smooth transition for hover effect */
            }}
            .card:hover {{
                transform: translateY(-10px) scale(1.05); /* Pop-up effect: move up 10px and scale up slightly */
                box-shadow: 4px 4px 15px rgba(0,0,0,0.2); /* Enhance shadow on hover for depth */
            }}
            .card img {{
                width: 170px;
                height: 120px;
                margin: 0 auto; /* Center the image */
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
                margin-top: 0 !important; /* Ensure no top margin */
                padding-top: 0 !important; /* Ensure no top padding */
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
                    height: 230px; /* Slightly smaller on mobile */
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # Header with background image starting from top
    st.markdown(
        """
        <div class="header-container">
            <h1 class="header-text"><b> NA Manpower Services </b></h1>
        </div>
        <p class="description-text"><b>Connecting the right talent with the right opportunities!</b></p>
        """,
        unsafe_allow_html=True
    )

    # Card data (unchanged)
    card_data = [
        {"title": "Job Opportunities", "desc": "Find the best job opportunities across industries.", "image": get_base64_image("images/job_opportunities_homepage_card1.png")},
        {"title": "Resume Services", "desc": "Get professional resume building services.", "image": get_base64_image("images/resume_services_homepage_card2.jpg")},
        {"title": "Career Counseling", "desc": "Expert advice to shape your career path.", "image": get_base64_image("images/career_counseling_homepage_card3.png")},
        {"title": "Employee Hiring", "desc": "We help companies hire the right talent.","image": get_base64_image("images/Employee_hiring_homepage_card4.avif")},
        {"title": "Training & Development", "desc": "Skill enhancement programs for job seekers.", "image": get_base64_image("images/training_and_development_homepage_card5.jpg")},
        {"title": "Industry Connect", "desc": "Network with industry experts and recruiters.", "image": get_base64_image("images/industry_connect_homepage_card6.avif")}
    ]

    # First row: 3 cards
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

    # Second row: 3 cards
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
        dob = st.date_input("Date of Birth")
        resume = st.file_uploader("Upload Resume", type=["pdf", "docx"])
        cover_letter = st.file_uploader("Upload Cover Letter", type=["pdf", "docx"])
        job_industry = st.selectbox("Job Industry", ["Select Job type", "IT (Technical And Non Technical)", "Mechanical (Diploma/Degree)", "Electrical (Diploma/Degree)", "Hospitality & Hotel Management", "Nursing", "Security & Guards", "BPO", "ITI(any trade)", "Electronics (Diploma/Degree)", "Caretaker/Guardian", "Welder/fitter/turner/helper", "Backoffice", "CNC/VMC Operator or Programmer", "Accountant & finance", "Sales & Marketing", "HR", "Other"])
        
        upi_id = "9731728337@okbizaxis"
        transaction_id = str(uuid.uuid4())[:8]
        transaction_note = f"Job Application Fee - {transaction_id}"
        amount = 150
        upi_link = f"upi://pay?pa={upi_id}&pn=NA%20Manpower%20Services&am={amount}&cu=INR&tn={transaction_note}"
        
        st.markdown(
            f"""
            <p style='text-align: center; color: black;'>
                Clicking "Submit & Pay" will open your UPI app to complete the payment.<br>
                Transaction Note (for reference): <strong>{transaction_note}</strong> .<br>
                <b>Application Fees: 150 Rupees Only</b>
            </p>
            """,
            unsafe_allow_html=True
        )
        
        submit_button = st.form_submit_button("Submit & Pay")

        if submit_button:
            if not full_name or not email or not phone or not pan_aadhar or job_industry == "Select Job type":
                st.error("All fields are required!")
            else:
                # Save the resume to a branch-wise folder
                resume_path = save_resume(resume, job_industry, email)
                
                st.info("Opening your UPI app to complete the payment...")
                st.markdown(
                    f"""
                    <script>
                        window.open("{upi_link}", "_blank");
                    </script>
                    """,
                    unsafe_allow_html=True
                )
                
                st.info("Please complete the payment in your UPI app. Verifying payment status...")
                time.sleep(10)
                
                payment_verified = True
                
                if payment_verified:
                    username = email
                    raw_password = generate_random_password()
                    hashed_password = generate_password_hash(raw_password)
                    
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO candidates (full_name, email, phone, pan_aadhar, dob, job_industry, payment_status, username, password, transaction_id, resume_path) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                        (full_name, email, phone, pan_aadhar, dob, job_industry, True, username, hashed_password, transaction_id, resume_path)
                    )
                    
                    cursor.execute(
                        "INSERT INTO users (username, password, role) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE password=%s",
                        (username, hashed_password, "Candidate", hashed_password)
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
                    st.error("Payment verification failed. Please try again or contact support.")

def admin_dashboard():
    st.subheader("Admin Dashboard")
    
    # Fetch all candidates
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, email, phone, pan_aadhar, dob, job_industry, payment_status, transaction_id FROM candidates")
    candidates = cursor.fetchall()
    conn.close()
    
    # Group candidates by branch (job_industry)
    branch_data = {}
    for candidate in candidates:
        branch = candidate[5]  # job_industry
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
    
    # Display candidates branch-wise with download options
    st.markdown("### Candidate Data by Branch")
    for branch, data in branch_data.items():
        st.markdown(f"#### {branch}")
        df = pd.DataFrame(data)
        
        # Display the data
        st.dataframe(df)
        
        # CSV Download
        csv = df.to_csv(index=False)
        st.download_button(
            label=f"Download {branch} Data as CSV",
            data=csv,
            file_name=f"{branch}_candidates.csv",
            mime="text/csv"
        )
        
        # XLSX Download
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)
        st.download_button(
            label=f"Download {branch} Data as XLSX",
            data=buffer,
            file_name=f"{branch}_candidates.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # Display Job Postings (Admin has access to view all)
    st.markdown("### All Job Postings")
    conn = get_db_connection()
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
    
    # Job Posting Form
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
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO job_postings (title, description, branch, posted_by) VALUES (%s, %s, %s, %s)",
                    (title, description, branch, username)
                )
                conn.commit()
                conn.close()
                st.success("Job posted successfully!")
    
    # Display Job Postings by this HR
    st.markdown("### Your Job Postings")
    conn = get_db_connection()
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
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=%s AND role=%s", (username, role))
        result = cursor.fetchone()

        if result and check_password_hash(result[0], password):
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

    # Display dashboards based on role
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

def servicesandcomapnies_page():
    st.subheader("Our Stats and Hiring")

    # CSS for card styling (removed image-related styles)
    st.markdown(
        """
        <style>
            .card {
                border: 1px solid #ddd;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                width: 100%;
                height: 250px; /* Reduced height since there's no image */
                background-color: #FFAC1C;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                margin-bottom: 70px;
                display: flex;
                flex-direction: column;
                justify-content: center; /* Center content vertically */
                transition: transform 0.3s ease-in-out; /* Smooth transition for hover effect */
            }
            .card:hover {
                transform: translateY(-10px) scale(1.05); /* Pop-up effect: move up 10px and scale up slightly */
                box-shadow: 4px 4px 15px rgba(0,0,0,0.2); /* Enhance shadow on hover for depth */
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

    # Data for 6 hiring stats (removed image field)
    companies_data = [
        {
            "name": "IT Hiring",
            "desc": "Leading IT firm with 100% job placement for software engineers.",
            "hiring_stat": "Hired 250 candidates in 2024"
        },
        {
            "name": "Mechanical & Industrial Hiring",
            "desc": "Top mechanical engineering company offering guaranteed placements.",
            "hiring_stat": "Hired 180 candidates in 2024"
        },
        {
            "name": "HealthCare Hiring",
            "desc": "Premier healthcare provider with 100% placement for nurses.",
            "hiring_stat": "Hired 300 candidates in 2024"
        },
        {
            "name": "Electrical Hiring",
            "desc": "Electrical engineering leader with excellent job opportunities.",
            "hiring_stat": "Hired 150 candidates in 2024"
        },
        {
            "name": "Hospitality Hiring",
            "desc": "Luxury hotel chain with 100% placement in hospitality roles.",
            "hiring_stat": "Hired 200 candidates in 2024"
        },
        {
            "name": "BPO Hiring",
            "desc": "Top BPO firm offering secure jobs with 100% placement.",
            "hiring_stat": "Hired 220 candidates in 2024"
        }
    ]

    # First row: 3 cards
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

    # Second row: 3 cards
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

    # Pie chart for hiring statistics
    st.markdown("### Hiring Statistics (2024)")
    hiring_data = {
        "Company": [company["name"] for company in companies_data],
        "Candidates Hired": [int(company["hiring_stat"].split()[1]) for company in companies_data]  # Extract number from "Hired X candidates"
    }
    df = pd.DataFrame(hiring_data)
    
    # Create a pie chart using Plotly
    fig = px.pie(
        df,
        values="Candidates Hired",
        names="Company",
        title="Candidates Hired by Partner Companies in 2024",
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    fig.update_traces(textinfo="percent+label", pull=[0.1, 0, 0, 0, 0, 0])  # Slightly pull out the first slice for emphasis
    fig.update_layout(
        showlegend=True,
        margin=dict(t=50, b=50, l=50, r=50),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

def about_page():
    st.subheader("About NA Manpower Services")

    # CSS for the big card and horizontal image carousel with pop-up animation
    st.markdown(
        """
        <style>
            /* Big Card Styling */
            .big-card {
                border: 2px solid #ddd;
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                width: 100%;
                max-width: 600px; /* Limit the width for better readability */
                margin: 20px auto; /* Center the card */
                background-color: #FFAC1C; /* Match the theme color */
                box-shadow: 4px 4px 10px rgba(0,0,0,0.2);
                animation: popUp 0.8s ease-out forwards; /* Apply the pop-up animation */
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

            /* Pop-up Animation */
            @keyframes popUp {
                0% {
                    transform: scale(0.9) translateY(20px); /* Start smaller and lower */
                    opacity: 0; /* Start invisible */
                }
                100% {
                    transform: scale(1) translateY(0); /* End at normal size and position */
                    opacity: 1; /* Fully visible */
                }
            }

            /* Carousel Styling */
            .carousel-container {
                width: 100%;
                overflow: hidden;
                margin-top: 30px;
                position: relative;
            }
            .carousel {
                display: flex;
                animation: scroll-left 20s linear infinite; /* Adjust speed with duration */
                white-space: nowrap;
            }
            .carousel img {
                width: 400px;
                height: 400px;
                margin-right: 20px; /* Space between images */
                border-radius: 10px;
                object-fit: cover; /* Ensure images fit nicely */
            }
            @keyframes scroll-left {
                0% {
                    transform: translateX(0);
                }
                100% {
                    transform: translateX(-100%); /* Move left by the full width of the carousel */
                }
            }
            /* Ensure the carousel loops seamlessly */
            .carousel:hover {
                animation-play-state: paused; /* Pause on hover */
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Big card with address, email, and contact number
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

    # Horizontal image carousel
    st.markdown("### Our Journey - Image Gallery")
    # List of local image paths (encoded as base64)
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
    # Duplicate the images to create a seamless loop
    if image_urls:
        image_urls_extended = image_urls + image_urls  # Duplicate for continuous scrolling
        carousel_html = '<div class="carousel-container"><div class="carousel">'
        for url in image_urls_extended:
            carousel_html += f'<img src="{url}" alt="Carousel Image">'
        carousel_html += '</div></div>'
        st.markdown(carousel_html, unsafe_allow_html=True)
    else:
        st.write("No images available for the gallery.")

if __name__ == "__main__":
    main()
