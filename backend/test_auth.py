import requests
import json
import time

# First, register a user (we can use a unique email each time to avoid "already registered")
# However, we already have a user from the previous registration? We got "Email already registered" for newtest@example.com.
# Let's use a timestamp-based email.

timestamp = str(int(time.time()))
email = f"test_{timestamp}@example.com"
password = "temporary"
full_name = f"Test User {timestamp}"

# Register
register_url = "http://localhost:8002/api/auth/register"
register_data = {
    "email": email,
    "full_name": full_name,
    "is_active": True
}
register_response = requests.post(register_url, json=register_data)
if register_response.status_code != 200:
    # Maybe the user already exists? Try to login instead.
    print(f"Registration failed: {register_response.status_code} {register_response.text}")
    # Fall back to login
    login_url = "http://localhost:8002/api/auth/login"
    login_data = {
        "email": email,
        "password": password
    }
    login_response = requests.post(login_url, json=login_data)
    if login_response.status_code != 200:
        print(f"Login also failed: {login_response.status_code} {login_response.text}")
        exit(1)
    else:
        tokens = login_response.json()
else:
    tokens = register_response.json()

access_token = tokens.get("access_token")
refresh_token = tokens.get("refresh_token")
print(f"Got access token: {access_token[:20]}...")
print(f"Got refresh token: {refresh_token[:20]}...")

# Now test the refresh endpoint
refresh_url = "http://localhost:8002/api/auth/refresh"
refresh_data = {
    "refresh_token": refresh_token
}
refresh_response = requests.post(refresh_url, json=refresh_data)
if refresh_response.status_code == 200:
    new_tokens = refresh_response.json()
    new_access_token = new_tokens.get("access_token")
    new_refresh_token = new_tokens.get("refresh_token")
    print(f"New access token: {new_access_token[:20]}...")
    print(f"New refresh token: {new_refresh_token[:20]}...")
    print("Refresh token endpoint works!")
else:
    print(f"Refresh failed: {refresh_response.status_code} {refresh_response.text}")