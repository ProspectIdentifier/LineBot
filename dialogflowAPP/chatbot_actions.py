class DefaultChatBotAction():
    def __init__(self, msg, intent):
        self.msg = msg
        self.intent = intent

    def get_response(self):
        return self.intent.get("fulfillmentText", "")


class ChangeRateChatBotAction():
    def __init__(self, msg, intent):
        self.msg = msg
        self.intent = intent

    def get_response(self):
        from exchange_rate_service import changeRate
        params = self.intent.get("parameters")
        if params is None:
            return u"匯率轉換失敗"
        _from = params.get("from")
        to = params.get("to")
        number = params.get("number")
        data = changeRate(number, _from, to)
        return data
