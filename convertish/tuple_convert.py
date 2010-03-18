from datetime import date

from convertish.convert import BaseConverter, ConvertError


class DateToDateTupleConverter(BaseConverter):

    def from_type(self, schema, data, converter):
        if data is None:
            return None
        return data.year, data.month, data.day

    def to_type(self, schema, data, converter):
        if data is None:
            return None
        try:
            try:
                V = [int(v) for v in data]
            except ValueError:
                raise ConvertError('Invalid Number')
            data = date(*V)
        except (TypeError, ValueError), e:
            raise ConvertError('Invalid date: '+str(e))
        return data


