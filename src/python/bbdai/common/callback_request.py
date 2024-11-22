from marshmallow_dataclass import dataclass
from bbdcommon.spechelpers.misc import schema_field

from bbdcommunications.message_component.messages.message_name_wrapper import message_name


@message_name("Bbd.Ai.TelephonyComponent.Models.CallbackRequest")
@dataclass
class CallbackRequest:
    name: str = schema_field(data_key="Name")
    surname: str = schema_field(data_key="Surname")
    id_number: str = schema_field(data_key="IDNumber")
    contact_number: str = schema_field(data_key="ContactNumber")
