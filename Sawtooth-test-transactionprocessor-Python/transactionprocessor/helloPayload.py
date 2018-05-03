from sawtooth_sdk.processor.exceptions import InvalidTransaction

class HelloPayload(object):
    def __init__(self,payload):
        try:
            # the payload is csv utf-8 encoded string
            name, action, type = payload.decode().split(",")
        except ValueError:
            raise InvalidTransaction('Invalid payload serialization')

        if not name:
            raise InvalidTransaction('name is required')

        if '|' in name:
            raise InvalidTransaction('name cannot contain |')

        if not action:
            raise InvalidTransaction('Action required')

        if action not in ('create','delete'):
            raise InvalidTransaction('Invalid Action: {}'.format(action))

        if action == 'create':
            type = 0

        self._name = name
        self._action = action
        self._type = type

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
    def type(self):
        return self._type
