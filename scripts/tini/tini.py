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
                print(f"\r{round(percent)}% - {completed}/{total_size}", end="")
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


def list_games(client: OculusClient, all: bool, details: bool):
    obj = client.get_active_entitlements()

    games = (
        obj.get("data", {})
        .get("viewer", {})
        .get("user", {})
        .get("active_entitlements", {})
        .get("nodes", [])
    )

    print("Games:")
    for game in games:
        name = game.get("item", {}).get("display_name", "")

        if game.get("grant_reason") != "NUX":
            print(f" - {name}")
        elif all:
            print(f" * {name}")
        else:
            continue

        if details:
            print(f"\tApp ID: {game.get('item', {}).get('id')}")
            print(
                f"\tCanonical Name: {game.get('item', {}).get('canonical_name', '?')}"
            )

            latest_supported_binary = game.get("item", {}).get(
                "latest_supported_binary", {}
            )

            if latest_supported_binary is not None:
                print(
                    f"\tLatest Version Code: {latest_supported_binary.get('version_code', '?')}"
                )
                print(f"\tLatest Version ID: {latest_supported_binary.get('id', '?')}")
                print(
                    f"\tPackage Name: {latest_supported_binary.get('package_name', '?')}"
                )


def download_game(client: OculusClient, game_name: str):
    obj = client.get_active_entitlements()

    games = (
        obj.get("data", {})
        .get("viewer", {})
        .get("user", {})
        .get("active_entitlements", {})
        .get("nodes", [])
    )

    game_id: str | None = None
    for game in games:
        name = game.get("item", {}).get("display_name", "")
        if name == game_name:
            game_id = game.get("item", {}).get("id")

    if not game_id:
        print(f"Game {game_name} not found in your games")
        return

    release_channels_response = client.get_app_release_channels(game_id)
    version_id = release_channels_response.release_channels.nodes[
        0
    ].latest_supported_binary.id

    download_url = f"https://securecdn.oculus.com/binaries/download/?id={version_id}&access_token={client.access_token}"
    download_progress(download_url, f"{game_name}.apk")


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
        "TINI",
        description="Search, list, and download games you own from the Oculus/Meta/Quest store!",
    )

    parser.add_argument(
        "-t",
        "--access-token",
        required=True,
        help="The value of the oc_www_at cookie when logged into developers.meta.com/horizon",
    )

    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    download_parser = subparsers.add_parser("download")
    search_parser = subparsers.add_parser("search")

    list_parser = subparsers.add_parser(
        "list", help="List the games/apps you own and can download."
    )

    list_parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        default=False,
        help="Include default games/apps.",
    )

    list_parser.add_argument(
        "-d",
        "--details",
        action="store_true",
        default=False,
        help="In addition to listing available applications, show information such as application ID and version number.",
    )

    # TODO: add support for downloading by specific version, version code, app id, etc
    # Additionally, it would be nice to have a way to "investigate" a specific app to list recent
    # versions, etc
    download_parser.add_argument(
        "-n", "--name", help="Name of the game to download", required=True
    )

    args = parser.parse_args()
    client = OculusClient(access_token=args.access_token, headset=Headset("Quest 2"))

    match args.subcommand:
        case "list":
            list_games(client, args.all, args.details)
        case "download":
            download_game(client, args.name)
        case "search":
            print("not yet implemented")
            pass
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
