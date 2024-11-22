from marshmallow_dataclass import dataclass
from bbdcommon.spechelpers.misc import schema_field

from bbdcommunications.message_component.messages.message_name_wrapper import message_name


@message_name("Bbd.Ai.Common.Files.FileDownloadMessage")
@dataclass
class FileDownloadMessage:
    download_link: str = schema_field(data_key="DownloadLink")
