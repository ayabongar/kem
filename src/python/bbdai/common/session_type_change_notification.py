from marshmallow_dataclass import dataclass
from bbdcommon.spechelpers.misc import schema_field

from bbdcommunications.message_component.messages.message_name_wrapper import message_name


@message_name("Bbd.Ai.Common.ControlPlane.SessionTypeChangeNotification")
@dataclass
class SessionTypeChangeNotification:
    new_message_type: str = schema_field(data_key="NewMessageType")
    intention: str = schema_field(data_key="Intention")
    channel_type: int = schema_field(data_key="ChannelType", default=None, allow_none=True)
