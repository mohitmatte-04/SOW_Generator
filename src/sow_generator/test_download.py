import os
from google.oauth2 import service_account
import google.auth.transport.requests
import requests

creds = service_account.Credentials.from_service_account_file(
    "D:\\AI_ML\\SOW-Generator\\repo\\prj-sandbox-presales-portal-b9a1ce61abb0.json",
    scopes=["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/presentations.readonly"]
)

request = google.auth.transport.requests.Request()
creds.refresh(request)
token = creds.token

url = f"https://docs.google.com/presentation/d/1bEsxBu-HcJo54_zt27ucQGhJdavxNNuCIvFUDhBCGqM/export/pdf"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)
print(response.status_code)
if response.status_code == 200:
    print(f"Downloaded {len(response.content)} bytes")
else:
    print(response.text)
