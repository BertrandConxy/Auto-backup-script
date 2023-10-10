import pickle
import sys
import os
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload


class MyDrive:
    def __init__(self):
        SCOPES = ["https://www.googleapis.com/auth/drive"]

        creds = None
        script_dir = os.path.dirname(os.path.abspath(__file__))
        credentials_path = os.path.join(script_dir, "credentials.json")
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

        self.service = build("drive", "v3", credentials=creds)

    def find_backup_folder(self):
        get_folders = (
            self.service.files()
            .list(
                q="name = 'BackupFolder2023' and mimeType='application/vnd.google-apps.folder'",
                spaces="drive",
            )
            .execute()
        )

        if not get_folders["files"]:
            folder_metadata = {
                "name": "BackupFolder2023",
                "mimeType": "application/vnd.google-apps.folder",
            }
            parent_folder = (
                self.service.files().create(body=folder_metadata, fields="id").execute()
            )
            parent_folder_id = parent_folder.get("id")
            return parent_folder_id
        else:
            parent_folder_id = get_folders["files"][0]["id"]
            return parent_folder_id

    def upload_files(self, filename, path):
        backup_folder_id = self.find_backup_folder()

        if not path.endswith(os.path.sep):
            path += os.path.sep

        # For some reason the path to file may not be correct so, exit gracefully
        try:
            file_to_upload = MediaFileUpload(f"{path}{filename}")
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found at path '{path}'")
            return  # Exit gracefully

        find_file = (
            self.service.files()
            .list(
                q=f"name='{filename}' and parents='{backup_folder_id}'",
                spaces="drive",
                fields="nextPageToken, files(id, name)",
                pageToken=None,
            )
            .execute()
        )

        if len(find_file["files"]) == 0:
            file_metadata = {"name": filename, "parents": [backup_folder_id]}

            self.service.files().create(
                body=file_metadata, media_body=file_to_upload, fields="id"
            ).execute()
            print(f"{filename} was backed up successfully!")
        else:
            print(f"{filename} is already backed up.")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 backup.py <path_to_directory>")
        return

    path = sys.argv[1]
    expanded_path = os.path.expanduser(path)
    files = os.listdir(expanded_path)
    my_drive = MyDrive()

    for file in files:
        my_drive.upload_files(file, expanded_path)

    print("Backup is complete!")


if __name__ == "__main__":
    main()
