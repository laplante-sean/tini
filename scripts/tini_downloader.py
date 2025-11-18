"""Quest app APK downloader."""

import json
import argparse
from enum import Enum
from typing import Any
from dataclasses import dataclass

import requests


# TODO: type-hinting for Entitlements API
class Entitlement:
    pass


class Headset(Enum):
    RIFT = "Rift"
    LAGUNA = "Rift S"
    MONTEREY = "Quest 1"
    HOLLYWOOD = "Quest 2"
    EUREKA = "Quest 3"
    SEACLIFF = "Quest Pro"
    GEARVR = "GearVR"
    PACIFIC = "Go"

    def to_section_id(self) -> str | None:
        """When retrieving applications from the app store, a "sectionId" must be provided."""
        match self:
            case Headset.RIFT | Headset.LAGUNA:  # Rift line
                return "1736210353282450"
            case (
                Headset.MONTEREY | Headset.HOLLYWOOD | Headset.EUREKA | Headset.SEACLIFF
            ):  # Quest line
                return "1888816384764129"
            case Headset.GEARVR | Headset.PACIFIC:
                return "174868819587665"


@dataclass
class OculusQuery:
    """
    Dataclass holding representation of GraphQL query
    """

    # GraphQL document to query
    # these often-times tend to be magic numbers that we just have to trust
    doc_id: str | None = None

    # GraphQL query itself
    doc: str | None = None

    # parameters injected into GraphQL query
    variables: dict[Any, Any] | None = None

    def encode(self, access_token: str) -> str:
        return f"access_token={access_token}&variables={json.dumps(self.variables or {})}&doc_id={self.doc_id or ''}&doc={self.doc or ''}"

    def make_uri(self, base_uri: str, access_token: str) -> str:
        return f"{base_uri}?{self.encode(access_token)}"


class OculusClient:
    OCULUS_URI = "https://graph.oculus.com/graphql"
    access_token: str
    headset: Headset

    def __init__(self, access_token: str, headset: Headset) -> None:
        self.access_token = access_token
        self.headset = headset

    def make_query(self, query: OculusQuery) -> dict[Any, Any]:
        return requests.post(
            url=query.make_uri(self.OCULUS_URI, self.access_token), data=None
        ).json()

    def get_app_details(self, app_id: str):
        return self.make_query(
            OculusQuery(
                doc_id="4282918028433524",
                variables={
                    "itemId": app_id,
                    "first": 20,
                    "last": None,
                    "after": None,
                    "before": None,
                    "forward": True,
                    "ordering": None,
                    "ratingScores": None,
                    "hmdType": self.headset.name,
                },
            )
        )

    def get_app_all_versions(self, app_id: str):
        return self.make_query(
            OculusQuery(
                doc_id="2885322071572384",
                variables={
                    "applicationID": app_id,
                },
            )
        )

    def get_app_latest_version(self, app_id: str):
        return self.make_query(
            OculusQuery(
                doc_id="1586217024733717",
                variables={
                    "id": app_id,
                },
            )
        )

    def get_app_dlcs(self, app_id: str):
        return self.make_query(
            OculusQuery(
                doc_id="3853229151363174",
                variables={
                    "id": app_id,
                    "first": 200,
                    "last": None,
                    "after": None,
                    "before": None,
                    "forward": True,
                    "ordering": None,
                    "ratingScores": None,
                    "hmdType": self.headset.name,
                },
            )
        )

    def get_binary_details(self, binary_id: str):
        return self.make_query(
            OculusQuery(
                doc_id="4734929166632773",
                variables={
                    "binaryID": binary_id,
                },
            )
        )

    def get_additional_binary_details(self, binary_id: str):
        return self.make_query(
            OculusQuery(
                doc_id="24072064135771905",
                variables={
                    "binaryID": binary_id,
                },
            )
        )

    def get_asset_files(self, app_id: str, version_code: int):
        return self.make_query(
            OculusQuery(
                doc="query ($params: AppBinaryInfoArgs!) { app_binary_info(args: $params) { info { binary { ... on AndroidBinary { id package_name version_code asset_files { edges { node { ... on AssetFile {  file_name uri size  } } } } } } } }}",
                variables={
                    "params": {
                        "app_params": [{"app_id": app_id, "version_code": version_code}]
                    },
                },
            )
        )

    def query_store(self, query: str):
        return self.make_query(
            OculusQuery(
                doc_id="3928907833885295",
                variables={
                    "query": query,
                    "hmdType": self.headset.name,
                    "firstSearchResultItems": 100,
                },
            )
        )

    def get_active_entitlements(self):
        """
        Entitlements include all digital assets owned by an Oculus account
        """
        # doc_id is the "magic" ID used to get active entitlements
        return self.make_query(OculusQuery(doc_id="4850747515044496"))


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

    download_url = f"https://securecdn.oculus.com/binaries/download/?id={game_id}&access_token={args.access_token}"
    download_progress(download_url, f"{game_name}.apk")


if __name__ == "__main__":
    main()
