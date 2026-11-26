import os, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
c = Credentials(None, refresh_token=os.environ["RT"],
  token_uri="https://oauth2.googleapis.com/token",
  client_id=os.environ["CID"], client_secret=os.environ["CSEC"],
  scopes=["https://www.googleapis.com/auth/youtube.upload"])
yt = build("youtube", "v3", credentials=c)
body = {"snippet": {"title": "TEST upload", "description": "test",
        "categoryId": "27"},
        "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": True}}
r = yt.videos().insert(part="snippet,status", body=body,
      media_body=MediaFileUpload(sys.argv[1], resumable=True)).execute()
print("UPLOADED, video id:", r["id"])
