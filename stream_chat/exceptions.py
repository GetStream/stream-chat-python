class StreamChannelException(Exception):
    pass


class StreamAPIException(Exception):
    def __init__(self, response):
        self.response = response
        self.json_response = False

        try:
            parsed_response = response.json()
            self.error_code = parsed_response.get("code", "unknown")
            self.error_message = parsed_response.get(
                "message", "unknown"
            )
            self.json_response = True
        except ValueError:
            pass

    def __str__(self):
        if self.json_response:
            return "StreamChat error code {}: {}".format(self.error_code, self.error_message)
        else:
            return "StreamChat error HTTP code: {}".format(self.response.status_code)
