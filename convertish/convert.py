

class ConvertError(Exception):
    """
    Exception to indicate failure in converting values.
    """

    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message

    def __str__(self):
        return self.message
    __unicode__ = __str__

    # Hide Python 2.6 deprecation warnings.
    def _get_message(self): return self._message
    def _set_message(self, message): self._message = message
    message = property(_get_message, _set_message)


class BaseConverter(object):

    def __init__(self, **kw):
        self.converter_options = kw.pop('converter_options', {})

    def from_type(self, schema, data, converter):
        """
        convert from i.e. for NumberToString converter - from number to string
        """
        raise NotImplementedError()

    def to_type(self, schema, data, converter):
        """
        convert to i.e. for NumberToString converter - to number from string
        """
        raise NotImplementedError()


class NullConverter(BaseConverter):

    def from_type(self, schema, value, converter):
        return value

    def to_type(self, schema, value, converter):
        return value


