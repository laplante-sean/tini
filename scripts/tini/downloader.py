"""Quest app APK downloader."""

import requests
import argparse

from tini.api.client import OculusClient
from tini.api.headset import Headset


def download_progress(url: str, dest: str):
    """Download a file."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        completed = 0
        percent = 0
        with open(dest, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                print(f"\r{percent}% - {completed}/{total_size}", end="")
                if not chunk:
                    continue
                f.write(chunk)
                completed += len(chunk)
                percent = (completed / total_size) * 100.0
        print(f"\nFile downloaded successfully to: {dest}")
    except requests.exceptions.RequestException as exc:
        print(f"\nError downloading the file: {exc}")
    except Exception as exc:
        print(f"\nAn unexpected error occurred: {exc}")


def main():
    """Entry Point.

    How to?

    1. Sign in or make an account here: https://developers.meta.com/horizon/
    2. Open the F12 developer options in your browser (in Chrome select the Application tab)
    3. View Cookies for "developers.meta.com" and copy the value of the oc_www_at cookie. Provide this to the -t/--access_token argument

    NOTE: Don't share this cookie value with anyone!!! Never share cookies with anyone!
    NOTE: Never trust scripts with cookies...not even this one. Look at the code and make sure we're not shipping your cookie off to China
    """
    parser = argparse.ArgumentParser(
        "TINI Downloader", description="Download games you own from Oculus/Meta/Quest"
    )
    parser.add_argument(
        "-t",
        "--access-token",
        required=True,
        help="The value of the oc_www_at cookie when logged into developers.meta.com/horizon",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-n", "--name", help="Name of the game to download")
    group.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List the games/apps you own and can download.",
    )
    args = parser.parse_args()

    client = OculusClient(access_token=args.access_token, headset=Headset("Quest 2"))
    obj = client.get_active_entitlements()
    games = (
        obj.get("data", {})
        .get("viewer", {})
        .get("user", {})
        .get("active_entitlements", {})
        .get("nodes", [])
    )
    games_by_name = {}
    if args.list:
        print("Games:")
    for game in games:
        name = game.get("item", {}).get("display_name", "")
        if name:
            games_by_name[name.strip().lower()] = game
            if args.list:
                print(f"\t{name}")

    if args.list:
        return

    game = games_by_name.get(args.name.strip().lower())
    if not game:
        print(f"Game {args.name} not found in your games")
        return

    game_id = game.get("item", {}).get("id")
    game_name = game.get("item", {}).get("display_name")
    if not game_id:
        print("Game has no ID. Something went wrong.")
        return

    release_channels_response = client.get_app_release_channels(game_id)

    version_id = release_channels_response.release_channels.nodes[
        0
    ].latest_supported_binary.id

    download_url = f"https://securecdn.oculus.com/binaries/download/?id={version_id}&access_token={args.access_token}"
    download_progress(download_url, f"{game_name}.apk")


if __name__ == "__main__":
    main()
