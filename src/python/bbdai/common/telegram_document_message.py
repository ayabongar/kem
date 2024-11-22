from marshmallow_dataclass import dataclass
from bbdcommon.spechelpers.misc import schema_field


from bbdcommunications.message_component.messages.message_name_wrapper import message_name


@message_name("Bbd.Ai.Common.Telegram.TelegramDocumentMessage")
@dataclass
class TelegramDocumentMessage:
    caption: str = schema_field(data_key="caption")
    file_name: str = schema_field(data_key="fileName")
    base_64_encoded_string: str = schema_field(data_key="base64EncodedString")
