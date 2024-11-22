from marshmallow_dataclass import dataclass
from bbdcommon.spechelpers.misc import schema_field

from bbdcommunications.message_component.messages.message_name_wrapper import message_name


@message_name("Bbd.Ai.Common.Files.FileUploadMessage")
@dataclass
class FileUploadMessage:
    file_type: str = schema_field(data_key="FileType")
    file_data: str = schema_field(data_key="FileData")
