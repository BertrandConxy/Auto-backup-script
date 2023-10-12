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

        # The file token.pickle stores the user's access and refresh tokens
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

    def create_folder(self, folder_name, parent_id):
        # Create a folder in Google Drive
        folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        }
        try:
            folder = (
                self.service.files().create(body=folder_metadata, fields="id").execute()
            )
            folder_id = folder.get("id")
            print(f"Folder: {folder_name} is created on GDrive.")
            return folder_id
        except Exception as e:
            print(f"Error creating the folder '{folder_name}': {e}")

    def upload_file(self, file_path, file_name, parent_id):
        try:
            # Check if the file exists in Google Drive
            find_file = (
                self.service.files()
                .list(
                    q=f"name='{file_name}' and parents='{parent_id}'",
                    spaces="drive",
                    fields="files(id)",
                    pageToken=None,
                )
                .execute()
            )

            if not find_file.get("files"):
                # Upload the file to the folder
                file_metadata = {
                    "name": file_name,
                    "parents": [parent_id],
                }
                file_to_upload = MediaFileUpload(file_path)
                self.service.files().create(
                    body=file_metadata, media_body=file_to_upload, fields="id"
                ).execute()

                print(f"------ File: {file_name} was backed up successfully!")
        except Exception as e:
            print(f"Error uploading the file '{file_name}': {e}")

    def find_or_create_backup_folder(self):
        # Define the folder name you're looking for
        folder_name = "BackupFolder2023"

        # Query Google Drive to find the folder
        query = (
            f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        )
        get_folders = self.service.files().list(q=query, spaces="drive").execute()

        if not get_folders.get("files"):
            # If the folder doesn't exist, create it
            folder_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
            }

            try:
                parent_folder = (
                    self.service.files()
                    .create(body=folder_metadata, fields="id")
                    .execute()
                )
                parent_folder_id = parent_folder.get("id")
                return parent_folder_id
            except Exception as e:
                print(f"Error creating the main backup folder: {e}")
                return None
        else:
            # If the folder exists, return its ID
            parent_folder_id = get_folders["files"][0].get("id")
            return parent_folder_id

    def upload_folders(self, path):
        backup_folder_id = self.find_or_create_backup_folder()
        new_backup_counter = 0

        for root, dirs, files in os.walk(path):
            for directory in dirs:
                folder_path = os.path.join(root, directory)
                folder_name = os.path.basename(directory)

                # Check if the folder exists in Google Drive
                query = f"name='{folder_name}' and parents='{backup_folder_id}'"
                find_folder = (
                    self.service.files()
                    .list(q=query, spaces="drive", fields="files(id)")
                    .execute()
                )

                if not find_folder.get("files"):
                    # If the folder is empty, skip creating it and print a message
                    folder_files = os.listdir(folder_path)
                    if not folder_files:
                        print(f"Folder {folder_name} is empty. Skipping...")
                    else:
                        # If there are files inside the folder, create it
                        folder_id = self.create_folder(folder_name, backup_folder_id)
                        # Now, upload any files inside the folder
                        for file in folder_files:
                            file_path = os.path.join(folder_path, file)
                            file_name = os.path.basename(file)
                            self.upload_file(file_path, file_name, folder_id)
                            new_backup_counter += 1
        return new_backup_counter


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 backup.py <path_to_directory>")
        return

    path = sys.argv[1]
    expanded_path = os.path.expanduser(path)

    if not expanded_path.endswith(os.path.sep):
        expanded_path += os.path.sep

    # Check if the specified directory exists
    if not os.path.exists(expanded_path):
        print(f"Error: Directory '{expanded_path}' does not exist.")
        return

    my_drive = MyDrive()
    print("___Backup cron is started___\n")

    try:
        backups_made = my_drive.upload_folders(expanded_path)

        if backups_made == 0:
            print("No new backups made today\n")
        else:
            print(f"\nTotal new backups made today: {backups_made}\n")

        print("___Backup is completed!___")

    except Exception as e:
        print(f"Error: {e}")
        print("___Backup terminated due to an error___")


if __name__ == "__main__":
    main()
