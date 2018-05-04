from sawtooth_sdk.processor.exceptions import InvalidTransaction

class HelloPayload(object):
    def __init__(self,payload):
        try:
            # the payload is csv utf-8 encoded string
            name, action, batchnr,username = payload.decode().split(",")
        except ValueError:
            raise InvalidTransaction('Invalid payload serialization')

        if not name:
            raise InvalidTransaction('name is required')

        if '|' in name:
            raise InvalidTransaction('name cannot contain |')

        if not action:
            raise InvalidTransaction('Action required')

        if action not in ('create','delete','update','list'):
            raise InvalidTransaction('Invalid Action: {}'.format(action))

        self._name = name
        self._action = action
        self._batchnr = batchnr
        self._username = username
        # self._latitude = latitude
        # self._longitude = longitude
        # self._batchnr = batchnr

    @staticmethod
    def from_bytes(payload):
        return HelloPayload(payload=payload)

    @property
    def name(self):
        return self._name
    @property
    def action(self):
        return self._action

    @property
    def username(self):
        return self._username

    # @property
    # def longitude(self):
    #     return self._longitude
    #
    @property
    def batchnr(self):
        return self._batchnr
