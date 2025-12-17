
# drive_uploader.py
import os, re, json
from typing import Optional, Tuple, List
import streamlit as st
from urllib.parse import urlencode

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]  # gestiona carpetas/archivos

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

def start_oauth_flow() -> str:
    """Devuelve la URL de autorización para que el usuario la abra."""
    flow = Flow.from_client_config(_client_config_from_secrets(), scopes=SCOPES)
    flow.redirect_uri = st.secrets["APP_BASE_URL"]
    auth_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )
    st.session_state["oauth_state"] = state
    return auth_url

def fetch_token_from_code(code: str):
    """Intercambia el 'code' por tokens y guarda creds en session."""
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
    """Obtiene el servicio de Drive desde session_state; si no hay, inicia OAuth."""
    if "google_creds" not in st.session_state:
        # mostrar botón y devolver None
        auth_url = start_oauth_flow()
        st.info("Para habilitar Google Drive, haz clic en **Autorizar** y regresa.")
        st.link_button("Autorizar Drive", auth_url)
        return None

    creds_dict = st.session_state["google_creds"]
    creds = Credentials(**creds_dict)
    # refresco automático si expira (google-auth lo maneja internamente al llamar APIs)
    return build("drive", "v3", credentials=creds)

def slugify(text: str) -> str:
    t = re.sub(r"\s+", "_", text.strip())
    return re.sub(r"[^\w\-_\.]", "", t)

def find_or_create_folder(service, name: str, parent_id: Optional[str]=None) -> str:
    q = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        q += f" and '{parent_id}' in parents"
    res = service.files().list(q=q, fields="files(id,name)").execute()
    items = res.get("files", [])
    if items:
        return items[0]["id"]
    metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        metadata["parents"] = [parent_id]
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]

def ensure_path(service, root_folder_id: str, segments: List[str]) -> str:
    parent = root_folder_id
    for seg in segments:
        parent = find_or_create_folder(service, seg, parent)
    return parent

def set_permission_anyone(service, file_id: str):
    permission = {"type": "anyone", "role": "reader"}
    service.permissions().create(fileId=file_id, body=permission).execute()

def upload_file(service, local_path: str, dest_folder_id: str, display_name: str) -> Tuple[str, str]:
    media = MediaFileUpload(local_path, resumable=True)
    metadata = {"name": display_name, "parents": [dest_folder_id]}
    file = service.files().create(body=metadata, media_body=media,
                                  fields="id, webViewLink, webContentLink").execute()
    # Enlace visible/descargable
    return file
