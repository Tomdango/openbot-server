class BroadcastTypes(object):
    MEMBER_ENTERED_GDPR_CONSENT = "me_gdpr_consent"
    MEMBER_ENTERED_CONSENT_GIVEN = "me_consent_granted"
    MEMBER_ENTERED_CONSENT_DENIED = "me_consent_denied"

    NET2_DISCONNECTED = "net2_disconnected"
    NET2_CONNECTING = "net2_connecting"
    NET2_CONNECTED = "net2_connected"
    GDPR_REQUEST = "gdpr_request"


class ResponseTypes(object):
    MEMBER_EXIT = "member_exit"
    RESPONSE_SUBMITTED = "response_submitted"
    RESPONSE_TIMEOUT = "response_timeout"
    GDPR_RESPONSE = "gdpr_response"
