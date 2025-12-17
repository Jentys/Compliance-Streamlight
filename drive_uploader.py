
# drive_uploader.py
import re
from typing import Optional, Tuple, List
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

def _client_config_from_secrets():
    return {
        "web": {
            "client_id": st.secrets["GOOGLE_CLIENT_ID"],
            "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [st.secrets["APP_BASE_URL"]],
            "javascript_origins": [st.secrets["APP_BASE_URL"]],
        }
    }

def start_oauth_flow():
    flow = Flow.from_client_config(_client_config_from_secrets(), scopes=SCOPES)
    flow.redirect_uri = st.secrets["APP_BASE_URL"]
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    st.session_state["oauth_state"] = state
    return auth_url

def fetch_token_from_code(code):
    flow = Flow.from_client_config(_client_config_from_secrets(), scopes=SCOPES)
    flow.redirect_uri = st.secrets["APP_BASE_URL"]
    flow.fetch_token(code=code)
    creds = flow.credentials
    st.session_state["google_creds"] = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }

def get_service():
    if "google_creds" not in st.session_state:
        auth_url = start_oauth_flow()
        st.info("Para habilitar Google Drive, haz clic en **Autorizar Drive**.")
        st.link_button("Autorizar Drive", auth_url)
        return None
    creds_dict = st.session_state["google_creds"]
    creds = Credentials(**creds_dict)
    return build("drive", "v3", credentials=creds)

def slugify(t):
    import re
    t = re.sub(r"\s+", "_", str(t).strip())
    return re.sub(r"[^\w\-_\.]", "", t)

def find_or_create_folder(service, name, parent=None):
    q = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
    if parent:
        q += f" and '{parent}' in parents"
    res = service.files().list(q=q, fields="files(id,name)").execute()
    items = res.get("files", [])
    if items:
        return items[0]["id"]
    body = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent:
        body["parents"] = [parent]
    f = service.files().create(body=body, fields="id").execute()
    return f["id"]

def ensure_path(service, root, segments):
    parent = root
    for seg in segments:
        parent = find_or_create_folder(service, seg, parent)
    return parent

def set_permission_anyone(service, file_id):
    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"}
    ).execute()

def upload_file(service, path, folder_id, name):
    media = MediaFileUpload(path, resumable=True)
    meta = {"name": name, "parents": [folder_id]}
    f = service.files().create(
        body=meta, media_body=media,
        fields="id, webViewLink, webContentLink"
    ).execute()
   
