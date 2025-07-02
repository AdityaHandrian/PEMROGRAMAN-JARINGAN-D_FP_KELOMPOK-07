import requests
import time

backends = [
    'http://10.8.195.10:8889',
    'http://10.8.195.10:8890',
    'http://10.8.195.10:8891'
]

def check_server(url):
    try:
        r = requests.get(f"{url}/", timeout=2)
        if r.status_code == 200:
            return "✅ UP"
        else:
            return f"⚠️ Error {r.status_code}"
    except:
        return "❌ DOWN"

def run_health_check():
    print("=== Realtime Backend Health Monitor ===")
    while True:
        for backend in backends:
            status = check_server(backend)
            print(f"{backend} → {status}")
        print("-" * 45)
        time.sleep(3)

if __name__ == "__main__":
    run_health_check()
