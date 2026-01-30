import sys
import requests
import json
import time

def verify_challenge(project_id):
    url = f"http://localhost:8000/api/projects/{project_id}/dojo/verify"
    print(f"📡 CONNECTING_TO_DOJO... [PROJECT: {project_id}]")
    
    try:
        response = requests.post(url)
        data = response.json()
        
        if data.get("success"):
            print("\n" + "="*40)
            print("🚀 CRITICAL_FIX_VERIFIED!")
            print(f"⏱️  TIME: {data.get('duration')} seconds")
            print(f"📝 MESSAGE: {data.get('message')}")
            print("="*40 + "\n")
        else:
            print("\n" + "!"*40)
            print("❌ VERIFICATION_FAILED")
            print(f"⚠️  ERROR: {data.get('error')}")
            print("!"*40 + "\n")
            
    except Exception as e:
        print(f"🛑 SYSTEM_LINK_OFFLINE: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dojo_verify.py <project_id>")
    else:
        verify_challenge(sys.argv[1])
