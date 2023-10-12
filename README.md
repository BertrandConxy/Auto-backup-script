![](https://img.shields.io/badge/AutoBackup-blue)
# AutoBackup Script

> Handy script which can help to automate the repetitive task of backing up files and folders to GDrive

## Built With

- Major languages (Python)
- Libraries (google-api-python-client, google-auth-httplib2,   google-auth-oauthlib)
- Technologies/tools used

  ```bash
  - Git(version control)
  - Google workspace apis(GDrive api)
  ```

## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites

- Python 3.10.7 or greater
- The pip package management tool
- A Google Cloud project.
- A Google account with Google Drive enabled.

### References
- [QuickStart](https://developers.google.com/drive/api/quickstart/python)

### Install

- Git
- Python 3.x
- python libraries using pip (google-api-python-client, google-auth-httplib2, google-auth-oauthlib)

#### Clone this repository

```bash
$ git clone <repo_link>
$ cd <repo_name>
```

#### Run project

- Ensure that you have `credentials.json` file in your working directory

```bash
$ python3 backup.py <path_to_your_directory_for_backup> # this will open in the browser for the first time in order to grant your app access to GDrive
```
<br>
## 📝 License

This project is [MIT](https://opensource.org/licenses/MIT) licensed.

