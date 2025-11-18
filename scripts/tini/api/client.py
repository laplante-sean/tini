import requests
from typing import Any

from tini.api.headset import Headset
from tini.api.query import OculusQuery

from tini.api.responses import ReleaseChannelResponse


class OculusClient:
    OCULUS_GRAPHQL_URI = "https://graph.oculus.com/graphql"

    access_token: str
    headset: Headset

    def __init__(self, access_token: str, headset: Headset) -> None:
        self.access_token = access_token
        self.headset = headset

    def make_query(self, query: OculusQuery) -> dict[Any, Any]:
        return requests.post(
            url=query.make_uri(self.OCULUS_GRAPHQL_URI, self.access_token),
            data=None,
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

    def get_app_release_channels(self, app_id: str) -> ReleaseChannelResponse:
        return ReleaseChannelResponse(
            **self.make_query(
                OculusQuery(
                    doc_id="3828663700542720",
                    variables={
                        "applicationID": app_id,
                    },
                )
            )
            .get("data", {})
            .get("node", {})
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
