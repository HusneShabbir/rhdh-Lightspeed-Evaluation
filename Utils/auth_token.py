import os
from pathlib import Path
import time
import pytest
from dotenv import load_dotenv, set_key

# Load environment variables once at the top level
load_dotenv()
from playwright.sync_api import Page, expect


def get_auth_token(page: Page) -> None:
    auth_token = None

    def handle_request(request):
        nonlocal auth_token
        headers = request.headers
        if 'authorization' in headers and headers['authorization'].startswith('Bearer '):
            auth_token = headers['authorization'][7:]

    def handle_response(response):
        nonlocal auth_token
        try:
            if auth_token is None and response.status == 200:
                headers = response.headers
                if 'authorization' in headers and headers['authorization'].startswith('Bearer '):
                    auth_token = headers['authorization'][7:]
        except Exception as e:
            print(f"Response handling error: {e}")

    page.on("request", handle_request)
    page.on("response", handle_response)

    try:
        page.goto("http://localhost:7007/lightspeed", wait_until="networkidle", timeout=30000)
        page.get_by_role("button", name="Enter").click()
        expect(page.get_by_text("How can I help you today?")).to_be_visible()
    except Exception as e:
        print(f"Navigation or interaction failed: {e}")

    # Wait to allow additional requests/responses to complete
    page.wait_for_timeout(3000)

    return auth_token

def replace_auth_token(page: Page) -> None:
    token = get_auth_token(page)
    assert token is not None, "❌ No authorization Bearer token found"
    print("✓ Successfully extracted authorization Bearer token")

    # Update .env file with the retrieved token
    env_path = Path('.env')
    set_key(str(env_path), 'BEARER_TOKEN', token)
    print("✓ Updated BEARER_TOKEN in .env file")

