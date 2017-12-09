import pytz
import random
import re
from datetime import date, datetime, time, timedelta
from enum import Enum
from nlog import log

import parsedatetime as pdt
from faker import Factory
from timestring import Range, TimestringInvalid

from nlu import tokenizer
from nlu.knowledge_base.entity_type_registry import register_entity_type
from nlu.knowledge_base.entity_type_base import EntityTypeBase, DEFAULT_VALUE_KEY
from nlu_applications.blank.entities.helpers_en.text_to_time import duration_text_to_minute, SHORT_TIME_UNITS, \
    LONG_TIME_UNITS, DAYS_OF_WEEK, MONTHS, TIME_LENGTH_MODIFIERS, MONTH_ORDINAL_DATES, MONTH_ORDINAL_DATES_TEXT
from nlu.payload_utils import get_payload_timezone


class DateParserTypes(Enum):
    date = 1
    time = 2
    datetime = 3
    no_result = 0


class DateTimeType(EntityTypeBase):
    id = 'datetime'
    fake_factory = Factory.create()
    accepted_parse_types = [DateParserTypes.date,
                            DateParserTypes.time,
                            DateParserTypes.datetime]

    def get_candidates(self, text, **kwargs):
        dialogue_state = kwargs.get('dialogue_state', {})
        tz = get_payload_timezone(dialogue_state)
        text = remove_prepositions(text)
        datetime_object = get_date_from_text(text, tz, self.accepted_parse_types)
        if not datetime_object:
            return []

        spoken = datetime_object.strftime(r'%B %d at %-I:%M %p')
        dt_entity = "%s" % datetime_object

        return [
            {DEFAULT_VALUE_KEY: spoken,
             'iso_time': dt_entity,
             'type': self.id
            }
        ]

    def generate(self):
        while True:
            yield str(self.fake_factory.date_time())

    def is_normalize_input(self):
        return False


class TimeType(EntityTypeBase):
    id = 'time'
    fake_factory = Factory.create()
    accepted_parse_types = [DateParserTypes.time, DateParserTypes.datetime]

    def get_candidates(self, text, **kwargs):
        dialogue_state = kwargs.get('dialogue_state', {})
        tz = get_payload_timezone(dialogue_state)
        text = self.extract_user_input_text(text, **kwargs)
        text = remove_prepositions(text)
        datetime_object = get_date_from_text(text, tz, self.accepted_parse_types)
        if not datetime_object:
            if not text.isdigit():
                return []
            num = int(text)
            if not num:
                return []
            now = datetime.now(pytz.timezone(tz))
            flag = False
            if 1 <= num < 12 and now.hour >= 12:
                num += 12
                flag = True
            if now.hour >= 12 and flag:
                time_obj = time(num-12)
            elif 0 <= num < 24:
                time_obj = time(num)
            else:
                return []
        else:
            time_obj = datetime_object.time()
        spoken = time_obj.strftime(r'%-I:%M %p')
        dt_entity = "%s" % time_obj
        return [
            {DEFAULT_VALUE_KEY: spoken,
             'iso_time': dt_entity,
             'type': self.id
             }
        ]

    def from_datetime(self, dt):
        t = dt.time()
        spoken = t.strftime(r'%-I:%M %p')
        return {
            'type': self.id,
            DEFAULT_VALUE_KEY: spoken,
            'spoken_time': spoken,
            'iso_time': t.isoformat()
        }

    def generate(self):
        while True:
            yield str(self.fake_factory.time())

    def is_normalize_input(self):
        return False

    def extract_user_input_text(self, text, **kwargs):
        try:
            model_name = kwargs['dialogue_state'].model_name
            text = self.extract_raw_text(text,
                                         kwargs['dialogue_state'].query,
                                         model_name)
        except (ValueError, KeyError, TypeError):
            log.warning('raw input not available so normalized input used.')

        return text


class DateType(EntityTypeBase):
    id = 'date'
    fake_factory = Factory.create()
    accepted_parse_types = [DateParserTypes.date, DateParserTypes.datetime]

    def get_candidates(self, text, **kwargs):
        dialogue_state = kwargs.get('dialogue_state', {})
        tz = get_payload_timezone(dialogue_state)
        text = remove_prepositions(text)
        datetime_object = get_date_from_text(text, tz, self.accepted_parse_types)

        if not datetime_object:
            return []

        spoken = datetime_object.strftime(r'%B %d')
        dt_entity = "%s" % datetime_object.date()

        return [
            {DEFAULT_VALUE_KEY: spoken,
             'iso_time': dt_entity,
             'type': self.id}
        ]

    def generate(self):
        while True:
            yield str(self.fake_factory.date())

    def from_datetime(self, dt):
        spoken = dt.strftime(r'%B %d')
        return {
            DEFAULT_VALUE_KEY: spoken,
            'spoken_time': spoken,
            'type': self.id,
            'iso_time': "%s" % dt.date()
        }

    def is_normalize_input(self):
        return False


class CommonTime(EntityTypeBase):
    id = 'common_time'

    def generate(self):
        while True:
            time_hour = str(random.randint(1, 12))
            am_or_pm = random.choice(['am', 'pm', 'a m', 'p m', 'a.m', 'p.m'])
            if random.random() <= .6:
                common_minutes = ['', ':15', ':30', ':45']
                final_time = time_hour + random.choice(common_minutes)
            else:
                time_minutes = str(random.randint(0, 60))
                final_time = time_hour + ":" + time_minutes

            if random.random() <= .4:
                yield final_time + ' ' + am_or_pm
            else:
                yield str(final_time)


def relative_date_handler(candidate_relative_date):
    if candidate_relative_date is 'this night':
        return 'tonight'
    elif candidate_relative_date is 'next_night':
        return 'tomorrow night'
    elif candidate_relative_date is 'last day':
        return 'yesterday'
    elif candidate_relative_date is 'this day':
        return 'today'
    elif candidate_relative_date is 'next day':
        return 'tomorrow'
    elif candidate_relative_date is 'last morning':
        return 'yesterday morning'
    elif candidate_relative_date is 'next morning':
        return 'tomorrow morning'
    else:
        return candidate_relative_date


class RelativeDate(EntityTypeBase):
    id = 'relative_date'

    # Generate function parameters set in action schema and read by framework
    # This yields correct relative dates and accepts past, present and future params for synthing
    def generate(self, past=True, present=True, future=True):
        modifiers = []
        if past:
            modifiers.append('last')
        if present:
            modifiers.append('this')
        if future:
            modifiers.append('next')
        while True:
            date = random.choice(['night', 'week', 'weekend', 'afternoon', 'morning', 'day'])
            final_value = random.choice(modifiers) + ' ' + date
            yield relative_date_handler(final_value)


class WeekDate(EntityTypeBase):
    id = 'week_date'

    def generate(self, past=True, present=True, future=True):
        modifiers = []
        if past:
            modifiers.append('last')
        if present:
            modifiers.append('this')
        if future:
            modifiers.append('next')
        while True:
            week_day = random.choice(DAYS_OF_WEEK)
            if random.random() <= .3:
                ordinal = random.choice(MONTH_ORDINAL_DATES)
                yield str(week_day + ' the ' + ordinal)
            elif random.random() <= .7:
                modifier = random.choice(modifiers)
                yield str(modifier + " " + week_day)


class CommonEventDate(EntityTypeBase):
    # container type for RelativeDate and WeekDate
    id = 'common_event_date'

    def generate(self):
        while True:
            yield None


class MonthDate(EntityTypeBase):
    id = 'month_date'

    def generate(self, present=True, past=True, future=True):
        while True:
            month = random.choice(MONTHS)
            ordinal = random.choice(MONTH_ORDINAL_DATES)
            yield str(month + ' ' + ordinal)


class CommonDate(EntityTypeBase):
    id = 'common_date'

    def generate(self, present=True, past=True, future=True):
        while True:
            month = random.choice(MONTHS)
            ordinal = random.choice(MONTH_ORDINAL_DATES_TEXT)
            if random.random() <= .5:
                output = str(month + ' ' + ordinal)
            else:
                output = str(ordinal + ' ' + month)
            yield output


class ShortDuration(EntityTypeBase):
    id = 'short_duration'
    fake_factory = Factory.create()

    def get_candidates(self, text, **kwargs):
        short_duration = self._create_short_duration(text)

        if short_duration is None:
            return []
        else:
            return [
                short_duration
            ]

    def _create_short_duration(self, text):
        tokenized_text = tokenizer.tokenize(text)

        mins = duration_text_to_minute(tokenized_text)

        if mins is None:
            return None

        return {
            'mins': mins,
            'type': self.id,
            DEFAULT_VALUE_KEY: mins
        }

    def generate(self):
        while True:
            unit = random.choice(SHORT_TIME_UNITS)
            singular_or_plural = random.choice(['singular', 'plural', 'plural', 'plural', 'plural'])
            pluralize = ''
            if singular_or_plural == 'plural':
                pluralize = 's'
            modifier = random.choice(TIME_LENGTH_MODIFIERS[unit][singular_or_plural])
            yield modifier + ' ' + unit + pluralize


class LongDuration(EntityTypeBase):
    id = 'long_duration'
    fake_factory = Factory.create()

    def generate(self):
        while True:
            unit = random.choice(LONG_TIME_UNITS)
            singular_or_plural = random.choice(['singular', 'plural', 'plural', 'plural', 'plural'])
            pluralize = ''
            if singular_or_plural is 'plural':
                pluralize = 's'
            modifier = random.choice(TIME_LENGTH_MODIFIERS[unit][singular_or_plural])
            yield modifier + ' ' + unit + pluralize


class TimeDuration(EntityTypeBase):
    id = 'duration'

    def generate(self):
        while True:
            yield None


class DateRangeType(EntityTypeBase):
    id = 'date_range'

    def get_candidates(self, text, **kwargs):
        dialogue_state = kwargs.get('dialogue_state', {})
        tz = get_payload_timezone(dialogue_state)
        text = remove_prepositions(text)
        range_obj = get_range_from_text(text, tz)

        if not range_obj:
            return []
        start = range_obj.start
        start_date = date(start.year, start.month, start.day)
        end = range_obj.end
        end_date = date(end.year, end.month, end.day)
        print(start_date, end_date)
        spoken = "from {0} to {1}".format(spoken_date(start_date), spoken_date(end_date))
        return [
            {DEFAULT_VALUE_KEY: spoken,
             'start': "%s" % start_date,
             'end': "%s" % end_date,
             'type': self.id
             }
        ]

    def is_normalize_input(self):
        return False


class TimeRangeType(EntityTypeBase):
    id = 'time_range'

    def get_candidates(self, text, **kwargs):
        dialogue_state = kwargs.get('dialogue_state', {})
        tz = get_payload_timezone(dialogue_state)
        text = remove_prepositions(text)
        range_obj = get_range_from_text(text, tz)

        if not range_obj:
            return []
        start = range_obj.start
        start_time = time(start.hour, start.minute, start.second)
        end = range_obj.end
        end_time = time(end.hour, end.minute, end.second)
        spoken = "from {0} to {1}".format(spoken_time(start_time), spoken_time(end_time))
        return [
            {DEFAULT_VALUE_KEY: spoken,
             'start': "%s" % start_time,
             'end': "%s" % end_time,
             'type': self.id
             }
        ]

    def is_normalize_input(self):
        return False


class DateTimeRangeType(EntityTypeBase):
    id = 'datetime_range'

    def get_candidates(self, text, **kwargs):
        dialogue_state = kwargs.get('dialogue_state', {})
        tz = get_payload_timezone(dialogue_state)
        text = remove_prepositions(text)
        range_obj = get_range_from_text(text, tz)
        if not range_obj:
            return []

        start = range_obj.start
        end = range_obj.end
        # Check is added as timestring always gives current time which is not required
        if start.day == end.day and start.month == end.month and start.year == end.year:
            start_date = datetime(start.year, start.month, start.day, start.hour, start.minute, start.second)
            end_date = datetime(end.year, end.month, end.day, end.hour, end.minute, end.second)
        else:
            start_date = datetime(start.year, start.month, start.day, hour=0, minute=0, second=0)
            end_date = datetime(end.year, end.month, end.day, hour=0, minute=0, second=0)
        return [
            {DEFAULT_VALUE_KEY: text,
             'start': "%s" % start_date,
             'end': "%s" % end_date,
             'type': self.id
             }
        ]

    def is_normalize_input(self):
        return False


def get_date_from_text(text, time_zone='US/Pacific', accepted_types=[DateParserTypes.datetime]):
    tz = pytz.timezone(time_zone)

    # fix to support 'day after tomorrow' as parsedatetime fails.
    if DateParserTypes.date in accepted_types or DateParserTypes.datetime in accepted_types:
        date_obj = handle_extra_cases(text, tz)
        if date_obj:
            return date_obj

    source_time = datetime.now(tz)
    date_obj, answer_type = pdt.Calendar().parseDT(text, sourceTime=source_time)
    accepted_types_values = [accepted_type.value for accepted_type in accepted_types]
    if answer_type in accepted_types_values:
        return date_obj

def remove_prepositions(text):
    pat = r'\b(of|on|in|by|at)\b'
    text = re.sub(pat, '', text)
    # parsedatetime fails if there are extra spaces between words
    # removing extra spaces between words
    return re.sub(' +', ' ', text).strip()


def get_range_from_text(text, time_zone):
    try:
        return Range(text, tz=time_zone)
    except TimestringInvalid:
        return None


def spoken_date(date_obj):
    return date_obj.strftime(r'%B %d')


def spoken_time(time_obj):
    return time_obj.strftime(r'%-I:%M %p')


def handle_extra_cases(text, tz):
    if text == 'day after tomorrow':
        return datetime.now(tz) + timedelta(days=2)
    elif text == 'day before yesterday':
        return datetime.now(tz) - timedelta(days=2)


register_entity_type(TimeType())
register_entity_type(DateType())
register_entity_type(DateTimeType())
register_entity_type(TimeDuration())
register_entity_type(DateRangeType())
register_entity_type(TimeRangeType())
register_entity_type(DateTimeRangeType())
register_entity_type(WeekDate())
register_entity_type(MonthDate())
register_entity_type(CommonDate())
register_entity_type(ShortDuration())
register_entity_type(LongDuration())
register_entity_type(CommonTime())
register_entity_type(RelativeDate())
register_entity_type(CommonEventDate())
