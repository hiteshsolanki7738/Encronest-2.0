from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ==============================
# SIGN UP
# ==============================
def signup_user(email, password):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        if response.user:
            print("SIGNUP SUCCESS:", response.user.email)
            return True, "Account created successfully"
        else:
            return False, "Signup failed"

    except Exception as e:
        print("SIGNUP ERROR:", e)
        return False, str(e)
    


# ==============================
# LOGIN
# ==============================
def login_user(email, password):
    try:
        print("Trying login:", email)

        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        print("Login success:", res)
        return True, res.user

    except Exception as e:
        print("LOGIN ERROR:", e)
        return False, str(e)
# ==============================
# LOGOUT
# ==============================
def logout_user():
    try:
        supabase.auth.sign_out()
        print("LOGOUT SUCCESS")
    except Exception as e:
        print("LOGOUT ERROR:", e)