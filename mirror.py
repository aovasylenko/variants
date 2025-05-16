import click
import requests
import re
import subprocess
import os
from urllib.parse import urljoin, urlparse


@click.command()
@click.option(
    "--index", required=True, help="URL of the PyPI index to query",
    default="https://variants-index.wheelnext.dev/"
)
@click.option(
    "--projects", help="List of projects to query (comma-separated)", default=["numpy","torch"],
    type=click.STRING, multiple=True
)
@click.option(
    "--download-dir", help="Directory to download wheels to", default="./wheels",
    type=click.Path()
)
@click.option(
    "--site", help="Site option for anaconda-client", default="latest",
    type=click.Path()
)
def list_wheels(index, projects, download_dir, site):
    """List all wheel files available in the specified PyPI index according to PEP-503."""
    if not index.endswith("/"):
        index += "/"

    click.echo(f"Index: {index}")
    click.echo(f"Projects: {",".join(projects)}")

    # Create download directory if it doesn't exist
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    response = requests.get(index)
    response.raise_for_status()

    project_pattern = re.compile(r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>')
    found_projects = project_pattern.findall(response.text)

    if not found_projects:
        click.echo("No projects found in the index.")
        return

    total_wheels = 0
    found_wheels = []

    for project_path, project_name in found_projects:
        if project_name not in projects:
            continue
        project_url = urljoin(index, project_path)
        try:
            # Get the project page
            project_response = requests.get(project_url)
            project_response.raise_for_status()

            # Find wheel files
            wheel_pattern = re.compile(r'<a\s+href="([^"]+\.whl)"[^>]*>')
            wheels = wheel_pattern.findall(project_response.text)

            if wheels:
                for wheel in wheels:
                    wheel_url = urljoin(project_url, wheel)
                    found_wheels.append(wheel_url)
                    total_wheels += 1
        except requests.exceptions.RequestException as e:
            click.echo(f"Error accessing project {project_name}: {e}", err=True)
            continue

    if found_wheels:
        click.echo(f"Found {total_wheels} wheel files across {len(found_projects)} projects:")
        for wheel_url in found_wheels:
            click.echo(f"Processing: {wheel_url}")
            try:
                wheel_filename = os.path.basename(urlparse(wheel_url).path)
                local_path = os.path.join(download_dir, wheel_filename)

                click.echo(f"Downloading to {local_path}...")
                wheel_response = requests.get(wheel_url, stream=True)
                wheel_response.raise_for_status()

                with open(local_path, 'wb') as f:
                    for chunk in wheel_response.iter_content(chunk_size=8192):
                        f.write(chunk)

                click.echo(f"Uploading {local_path}...")
                subprocess.run(["python", "acvar.py", "-s", site, "upload", local_path], check=True)
                click.echo(f"Successfully uploaded: {wheel_filename}")
            except requests.exceptions.RequestException as e:
                click.echo(f"Failed to download {wheel_url}: {e}", err=True)
            except subprocess.CalledProcessError as e:
                click.echo(f"Failed to upload {wheel_url}: {e}", err=True)
    else:
        click.echo("No wheel files found in any projects.")

if __name__ == "__main__":
    list_wheels()