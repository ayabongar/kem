from enum import IntEnum
from typing import List
import uuid
from marshmallow_dataclass import dataclass
from bbdcommon.spechelpers.misc import schema_field
from bbdai.common.sars_live_chat_interface import AuthenticationDetails, TextObject
from datetime import datetime

from bbdcommunications.message_component.messages.message_name_wrapper import message_name

class ChannelType(IntEnum):
    EFILING: int = 0
    WHATSAPP: int = 1

@message_name("Bbd.Ai.Common.Bot.BotMessage")
@dataclass
class BotMessage:
    message_id: str = schema_field(data_key="MessageID", default=str(uuid.uuid1()), allow_none=False)
    participant_id: str = schema_field(data_key="ParticipantId", default=None, allow_none=True)

    participant_name: str = schema_field(data_key="ParticipantName", default=None, allow_none=True)

    channel_type: int = schema_field(data_key="ChannelType", default=None, allow_none=True)

    authentication_details: AuthenticationDetails = schema_field(
        data_key="AuthenticationDetails", default=None, allow_none=True
    )
    text_objects: List[TextObject] = schema_field(data_key="TextObjects", default_factory=list)

    sent_time: datetime = schema_field(data_key="SentTime", default=datetime.now(), allow_none=True)

    def copy_from_other(self, other) -> None:
        self.authentication_details = other.authentication_details
        self.channel_type = other.channel_type
