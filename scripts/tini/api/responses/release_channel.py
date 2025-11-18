from typing import Literal, Any, List
from pydantic import BaseModel, Field
from tini.api.responses.base import BaseResponse


class AndroidBinaryResponse(BaseResponse):
    typename: Literal["AndroidBinary"] = Field(alias="__typename")

    created_date: int
    id: str
    version: str
    version_code: int


class Organization(BaseModel):
    viewer_role: str | None
    id: str
    is_authorized_for_quest: bool


class UserLists(BaseModel):
    nodes: List[Any]


class ReleaseChannel(BaseModel):
    id: str
    channel_name: str
    group: str
    latest_supported_binary: AndroidBinaryResponse
    subscribedCustomers: None
    userlists: UserLists


class ReleaseChannels(BaseModel):
    count: int
    nodes: List[ReleaseChannel]


class ReleaseChannelResponse(BaseResponse):
    typename: Literal["Application"] = Field(alias="__typename")

    id: str
    organization: Organization
    is_approved: bool
    is_concept: bool
    is_enterprise_enabled: bool
    release_channels: ReleaseChannels
    platform: Literal["ANDROID_6DOF"] | str
