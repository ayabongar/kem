from enum import IntEnum
from bbdcommon.spechelpers.misc import schema_field
from marshmallow_dataclass import dataclass
from bbdcommunications.message_component.messages.message_name_wrapper import message_name
from typing import List
from datetime import datetime
import uuid


class TextTypeEnum(IntEnum):
    TypeingIndicator: int = 1
    BasicText: int = 2
    Button: int = 3
    ReadIndicator: int = 4
    Download: int = 5
    DidYouMean: int = 6
    MenuButton: int = 7
    SessionEnded: int = 8
    SessionTransferred: int = 9
    DeliveredIndicator: int = 10
    Attachments: int = 11
    LinkButton: int = 12
    ContactList: int = 13

@dataclass
class AuthenticationDetails:
    is_authenticated: bool = schema_field(data_key="IsAuthenticated", default=False, allow_none=True)
    id_number: str = schema_field(data_key="IdNumber", allow_none=True, default=None)
    passport_number: str = schema_field(data_key="PassportNumber", allow_none=True, default=None)
    tax_reference_number: str = schema_field(data_key="TaxReferenceNumber", allow_none=True, default=None)
    contact_number: str = schema_field(data_key="ContactNumber", allow_none=True, default=None)
    email_address: str = schema_field(data_key="EmailAddress", allow_none=True, default=None)


@dataclass
class TextObject:
    """
        Attachments: (WHATSAPP only at the moment)
            text: The message displayed to the taxpayer along with the attachment
            action: The filename/fileId used in the downlink 
            text_type: Attachments = 11
            description: Used as the fileDisplayName which the user will see

        DidYouMean:
            text: If 3 suggested answers are returned, text is used as summary 
                    for each answer or initial display text
            action: The Lwazi answer value behind the initial display text
            text_type: DidYouMean = 6
            description: Used by WHATSAPP channel to display text in the in the menu
    """
    text: str = schema_field(data_key="Text")
    text_type: int = schema_field(data_key="TextType")
    action: str = schema_field(data_key="Action", default=None, allow_none=True)
    description: str = schema_field(data_key="Description", default=None, allow_none=True)


# TODO Create a new LiveChatMessage to distinguish internal messages from external messages SM/Efiling, which will be using the SARSLiveChatInterface. Jira: SCC-95


@message_name("Bbd.Ai.Common.SARSLiveChat.SARSLiveChatInterface")
@dataclass
class SARSLiveChatInterface:
    session_id: str = schema_field(data_key="SessionID", default="")
    message_id: str = schema_field(data_key="MessageID", default="")
    participant_name: str = schema_field(data_key="ParticipantName", default=None, allow_none=True)
    participant_id: str = schema_field(data_key="ParticipantId", default=None, allow_none=True)
    authentication_details: AuthenticationDetails = schema_field(
        data_key="AuthenticationDetails", default=None, allow_none=True
    )
    text_objects: List[TextObject] = schema_field(data_key="TextObjects", default_factory=list)
    sent_time: datetime = schema_field(data_key="SentTime", default=None, allow_none=True)

    def copy_from_other(self, other) -> None:
        self.session_id = other.session_id
        self.message_id = str(uuid.uuid1())
        self.authentication_details = other.authentication_details
