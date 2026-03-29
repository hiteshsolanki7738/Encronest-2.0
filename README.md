# Encronest 2.0

A secure authentication and data management application built with Streamlit.

## Features
- Secure Login & Registration System
- OTP Verification
- Cloud Database and Storage Integration (Appwrite & Supabase)
- Cryptographic security algorithms

## Local Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd "encronest 2.0"
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file in the root directory and add your necessary environment variables based on the services used (e.g. Appwrite, Supabase, Twilio). 

5. **Run the App**
   ```bash
   streamlit run streamlit_app.py
   ```

## Deployment
This app can be deployed easily to [Streamlit Community Cloud](https://streamlit.io/cloud). 
1. Push this code to a public or private GitHub repository.
2. Log into Streamlit Community Cloud and click "New App".
3. Select your repository, branch, and set the Main file path to `streamlit_app.py`.
4. **Before deploying**, click on "Advanced settings" and paste your environment variables (from your `.env` file) into the Secrets field to ensure your app connects to your services properly!
