import json

import requests

authkey = "***REMOVED***"

SEND_OTP_ENDPOINT = "https://api.msg91.com/api/v5/otp"
OTP_TEMPLATE_ID = "***REMOVED***"


def send_sms(message, user):

    country_code = "+91"
    OTP = "025632"  # replace this with 'message' object
    phone_number = user.profile.phone
    full_phone = f"{country_code.strip()}{phone_number.strip()}"
    extra_param = json.dumps({"OTP": OTP})

    data = {
        "authkey": authkey,
        "template_id": OTP_TEMPLATE_ID,
        "extra_param": extra_param,
        "mobile": full_phone,
    }

    response = requests.post(SEND_OTP_ENDPOINT, data=data)
    response = response.json()
    # response_type = response.get("type", "")
    # if "error" in response_type:
    #     log.info(response)
    #     print('False')
    # print('True')
