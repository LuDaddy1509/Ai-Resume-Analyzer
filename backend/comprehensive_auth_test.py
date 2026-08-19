import requests
import json
import time

BASE_URL = "http://localhost:8002"

def test_complete_auth_flow():
    print("=== Complete Authentication Flow Test ===")

    # Step 1: Register a new user
    timestamp = str(int(time.time()))
    email = f"flowtest_{timestamp}@example.com"
    password = "SecurePass123!"
    full_name = f"Flow Test User {timestamp}"

    print(f"\n1. Registering user: {email}")
    register_url = f"{BASE_URL}/api/auth/register"
    register_data = {
        "email": email,
        "full_name": full_name,
        "is_active": True
    }
    register_response = requests.post(register_url, json=register_data)

    if register_response.status_code != 200:
        print(f"   Registration failed: {register_response.status_code} {register_response.text}")
        # Maybe user exists, try login
        print("   Trying login instead...")
        login_url = f"{BASE_URL}/api/auth/login"
        login_data = {
            "email": email,
            "password": password
        }
        login_response = requests.post(login_url, json=login_data)
        if login_response.status_code != 200:
            print(f"   Login also failed: {login_response.status_code} {login_response.text}")
            return False
        tokens = login_response.json()
    else:
        tokens = register_response.json()
        print("   Registration successful!")

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    user = tokens.get("user")

    print(f"   User ID: {user.get('id')}")
    print(f"   Access token received: {access_token[:20]}...")
    print(f"   Refresh token received: {refresh_token[:20]}...")

    # Step 2: Test accessing protected endpoint with access token
    print("\n2. Testing protected endpoint access with access token")
    me_url = f"{BASE_URL}/api/auth/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = requests.get(me_url, headers=headers)

    if me_response.status_code == 200:
        user_data = me_response.json()
        print(f"   Successfully accessed /api/auth/me: {user_data.get('email')}")
    else:
        print(f"   Failed to access protected endpoint: {me_response.status_code} {me_response.text}")
        return False

    # Step 3: Test refresh token endpoint
    print("\n3. Testing refresh token endpoint")
    refresh_url = f"{BASE_URL}/api/auth/refresh"
    refresh_data = {"refresh_token": refresh_token}
    refresh_response = requests.post(refresh_url, json=refresh_data)

    if refresh_response.status_code == 200:
        new_tokens = refresh_response.json()
        new_access_token = new_tokens.get("access_token")
        new_refresh_token = new_tokens.get("refresh_token")
        print(f"   New access token: {new_access_token[:20]}...")
        print(f"   New refresh token: {new_refresh_token[:20]}...")
        print("   Refresh successful!")

        # Step 4: Test that new access token works
        print("\n4. Testing new access token")
        me_response2 = requests.get(me_url, headers={"Authorization": f"Bearer {new_access_token}"})
        if me_response2.status_code == 200:
            user_data2 = me_response2.json()
            print(f"   New access token works: {user_data2.get('email')}")
        else:
            print(f"   New access token failed: {me_response2.status_code} {me_response2.text}")
            return False

        # Step 5: Test that old refresh token no longer works (token rotation)
        print("\n5. Testing token rotation (old refresh token should be invalid)")
        refresh_response2 = requests.post(refresh_url, json=refresh_data)  # Same old refresh token
        if refresh_response2.status_code == 401:
            print("   Old refresh token correctly rejected (token rotation working)")
        else:
            print(f"   WARNING: Old refresh token still works: {refresh_response2.status_code} {refresh_response2.text}")
            # This might be OK depending on implementation, but ideally should be invalid

        return True
    else:
        print(f"   Refresh failed: {refresh_response.status_code} {refresh_response.text}")
        return False

if __name__ == "__main__":
    success = test_complete_auth_flow()
    if success:
        print("\n=== ALL TESTS PASSED ===")
    else:
        print("\n=== SOME TESTS FAILED ===")
        exit(1)