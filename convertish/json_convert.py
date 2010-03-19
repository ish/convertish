from datetime import date, time

from convertish.convert import BaseConverter, ConvertError


class DateToJSONConverter(BaseConverter):

    def from_type(self, schema, data, converter, k):
        if data is None:
            return None
        return {'__type__':'date','year':data.year, 'month':data.month, 'day':data.day}

    def to_type(self, schema, data, converter, k):
        if data is None:
            return None
        try:
            try:
                year, month, day = int(data['year']) ,int(data['month']) ,int(data['day']) ,
            except ValueError:
                raise ConvertError('Invalid Number')
            data = date(year, month, day)
        except (TypeError, ValueError), e:
            raise ConvertError('Invalid date: '+str(e))
        return data


class TimeToJSONConverter(BaseConverter):

    def from_type(self, schema, data, converter, k):
        if data is None:
            return None
        return {'__type__':'time','hour':data.hour, 'minute':data.minute, 'second':data.second,'microsecond':data.microsecond}

    def to_type(self, schema, data, converter, k):
        if data is None:
            return None
        try:
            try:
                h, m, s, ms = int(data['hour']), int(data['minute']), int(data['second']) ,int(data.get('microsecond',0))
            except ValueError:
                raise ConvertError('Invalid Number')
            data = time(h, m, s, ms)
        except (TypeError, ValueError), e:
            raise ConvertError('Invalid time: '+str(e))
        return data


