from datetime import date, time


class DateToJSONConverter(Converter):

    def from_type(self, value, converter_options={}):
        if value is None:
            return None
        return {'__type__':'date','year':value.year, 'month':value.month, 'day':value.day}

    def to_type(self, value, converter_options={}):
        if value is None:
            return None
        try:
            try:
                year, month, day = int(value['year']) ,int(value['month']) ,int(value['day']) ,
            except ValueError:
                raise ConvertError('Invalid Number')
            value = date(year, month, day)
        except (TypeError, ValueError), e:
            raise ConvertError('Invalid date: '+str(e))
        return value


class TimeToJSONConverter(Converter):

    def from_type(self, value, converter_options={}):
        if value is None:
            return None
        return {'__type__':'time','hour':value.hour, 'minute':value.minute, 'second':value.second,'microsecond':value.microsecond}

    def to_type(self, value, converter_options={}):
        if value is None:
            return None
        try:
            try:
                h, m, s, ms = int(value['hour']), int(value['minute']), int(value['second']) ,int(value.get('microsecond',0))
            except ValueError:
                raise ConvertError('Invalid Number')
            value = time(h, m, s, ms)
        except (TypeError, ValueError), e:
            raise ConvertError('Invalid time: '+str(e))
        return value


