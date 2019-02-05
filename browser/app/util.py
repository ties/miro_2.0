from calendar import timegm
import datetime
from werkzeug.routing import BaseConverter


def get_start_and_end_of_day(date):
    start_of_day = timegm(date.timetuple())
    end_of_day = start_of_day + 60 * 60 * 24
    return start_of_day, end_of_day


class DateConverter(BaseConverter):
    def to_python(self, value):
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()

    def to_url(self, value):
        return value.strftime('%Y-%m-%d')
