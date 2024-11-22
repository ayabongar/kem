from marshmallow_dataclass import dataclass
from bbdcommon.spechelpers.misc import schema_field
from typing import List

from bbdcommunications.message_component.messages.message_name_wrapper import message_name


@message_name("Bbd.Ai.Common.Bot.BotReplyMessage")
@dataclass
class BotReplyMessage:
    messages: List[str] = schema_field(data_key="Messages", default_factory=list)
