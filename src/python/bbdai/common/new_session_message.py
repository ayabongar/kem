from enum import IntEnum
from typing import List
import uuid
from marshmallow_dataclass import dataclass
from bbdcommon.spechelpers.misc import schema_field
from bbdai.common.sars_live_chat_interface import AuthenticationDetails, TextObject
from datetime import datetime

from bbdcommunications.message_component.messages.message_name_wrapper import message_name

@message_name("Bbd.Ai.Common.LiveChat.NewSessionMessage")
@dataclass
class NewSessionMessage:
    session_id: str = schema_field(data_key="session_id", default=None, allow_none=True)
    channel_type: int = schema_field(data_key="ChannelType", default=None, allow_none=True)

