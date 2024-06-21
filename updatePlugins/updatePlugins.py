import requests
import subprocess
import os

def download_and_run_latest_release(repo_owner, repo_name):
    # GitHub API URL to fetch the latest release
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"

    # Send a request to the GitHub API
    response = requests.get(url)
    response.raise_for_status()  # Raises an exception for HTTP errors

    # Parse the JSON response
    latest_release = response.json()
    asset = latest_release['assets'][0]  # Assuming the first asset is the one we want to download
    download_url = asset['browser_download_url']
    file_name = asset['name']

    # Download the latest release file
    print(f"Downloading {file_name} from {download_url}...")
    download_response = requests.get(download_url)
    with open(file_name, 'wb') as f:
        f.write(download_response.content)

    # Making the file executable (necessary for Unix-like systems)
    if os.name != 'nt':  # If not Windows
        os.chmod(file_name, 0o755)

    # Run the downloaded file
    print(f"Running {file_name}...")
    subprocess.run(f"./{file_name}" if os.name != 'nt' else file_name, shell=True)

# Example usage:
# Replace 'repo_owner' and 'repo_name' with the actual GitHub repository owner and repository name
download_and_run_latest_release('CharlieYang0040', 'NukeScriptsRepo')