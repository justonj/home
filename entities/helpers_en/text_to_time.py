
SHORT_TIME_UNITS = ['minute', 'hour', 'day']

LONG_TIME_UNITS = ['week', 'month', 'year']

FRACTION_UNITS = {
    'quarter': 25,
    'half': 50,
    'three quarters': 75
}

DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday',
                'Thursday', 'Friday', 'Saturday', 'Sunday']

MONTHS = ['January', 'February', 'March', 'April', 'May',
          'June', 'July', 'August', 'September', 'October',
          'November', 'December']

# Dictionary which contains time length modifiers for synthesis
TIME_LENGTH_MODIFIERS = {'minute': {'singular': ['a', 'one'],
                                    'plural': ['ten', 'fifteen', 'thirty', 'fourty-five',
                                               '10', '15', '30', '45', 'a few', 'a couple']},
                         'hour': {'singular': ['an', 'half an', 'a quarter of an', 'less than an',
                                               'one', 'a little over an'],
                                  'plural': ['a couple of', 'a few', 'two', 'three', 'four', '2', '3', '4']},
                         'day': {'singular': ['a', 'half of a', 'part of a',
                                              'more than half of a', 'less than half a'],
                                 'plural': ['a few', 'a couple of', 'several',
                                            ' two', 'three', 'two or three', 'four']},
                         'week': {'singular': [], 'plural': []},
                         'month': {'singular': [], 'plural': []},
                         'year': {'singular': [], 'plural': []},
                         }

MONTH_ORDINAL_DATES = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th',
                       '11th', '12th', '13th', '14th', '15th', '16th', '17th', '18th', '19th',
                       '20th', '21st', '22nd', '23rd', '24th', '25th', '26th', '27th', '28th',
                       '29th', '30th', '31st']

MONTH_ORDINAL_DATES_TEXT = ['first', 'second', 'third', 'fourth', 'fifth', 'fifteenth', 'twentieth', 'twenty sixth', 'twenty first']

NUMBER = {
    'zero': 0,
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
    'eleven': 11,
    'twelve': 12,
    'thirteen': 13,
    'fourteen': 14,
    'fifteen': 15,
    'sixteen': 16,
    'seventeen': 17,
    'eighteen': 18,
    'nineteen': 19,
    'twenty': 20,
    'thirty': 30,
    'forty': 40,
    'fifty': 50,
    'sixty': 60,
    'seventy': 70,
    'eighty': 80,
    'ninety': 90
}

MAGNITUDE = {
    'thousand': 10**3,
    'million': 10**6,
    'billion': 10**9,
    'trillion': 10**12,
    'quadrillion': 10**15,
    'quintillion': 10**18,
    'sextillion': 10**21,
    'septillion': 10**24,
    'octillion': 10**27,
    'nonillion': 10**30,
    'decillion': 10**33,
}


def duration_text_to_minute(tokenized_text):
    minutes = 0
    for tokenized_amount, unit in _unit_split_generator(tokenized_text):
        add_minutes = _duration_to_mins(tokenized_amount, unit)
        if add_minutes is None:
            return None
        minutes += add_minutes
    return minutes


def _unit_split_generator(tokenized_text):
    '''will yield one value and unit chunk at a time'''

    unit_positions = []
    for i, word in enumerate(tokenized_text):
        # depluralization
        if word[-1] == 's':
            word = word[0:-1]
        if word in SHORT_TIME_UNITS or word == LONG_TIME_UNITS[0] or word == LONG_TIME_UNITS[1]:
            if unit_positions:
                first_word_pos = unit_positions[-1] + 1
            else:
                first_word_pos = 0
            starting_position = first_word_pos + 1 if 'and' == tokenized_text[first_word_pos] else first_word_pos
            unit_positions.append(i)

            yield tokenized_text[starting_position: i], word


def _text_to_integer(tokenized_text):
    # digit check here
    if len(tokenized_text) == 1 and tokenized_text[0].isdigit():
        return int(tokenized_text[0])

    n = 0
    total = 0
    for word in tokenized_text:
        x = NUMBER.get(word, None)
        if x is not None:
            total += x
        elif word == "hundred" and total != 0:
            total *= 100
        else:
            x = MAGNITUDE.get(word, None)
            if x is not None:
                n += total * x
                total = 0
            else:
                return None
    return n + total


def _get_amount_with_fraction(tokenized_amount):
    fraction_percent = 0
    simplified_amount = []
    word_count = len(tokenized_amount)
    skip_countdown = 0
    for i, word in enumerate(tokenized_amount):
        if skip_countdown > 0:
            skip_countdown -= 1
            continue

        if word == 'and':
            # fraction unit checking here
            unit_check_index = i + 1
            if i + 1 < word_count and tokenized_amount[i + 1] == 'a':
                unit_check_index += 1

            # one quarter and one half case
            if unit_check_index < word_count and tokenized_amount[unit_check_index] in FRACTION_UNITS:
                split_unit = tokenized_amount[unit_check_index]

                if split_unit in FRACTION_UNITS:
                    fraction_percent = FRACTION_UNITS[split_unit]

                skip_countdown = unit_check_index - i
                continue

            # three quarters case
            if i + 2 < word_count and ' '.join(
                    [tokenized_amount[i + 1], tokenized_amount[i + 2]]) in FRACTION_UNITS:
                fraction_percent = FRACTION_UNITS[' '.join([tokenized_amount[i + 1], tokenized_amount[i + 2]])]
                skip_countdown = unit_check_index + 2 - i
                continue

        else:
            simplified_amount.append(word)

    amt_int = _text_to_integer(simplified_amount)

    return amt_int, fraction_percent


_minute_mod = 1
_hour_mod = 60
_day_mod = _hour_mod * 24
_week_mod = _day_mod * 7
_month_mod = _day_mod * 30


def _duration_to_mins(amount, unit):
    amt, fraction_percent = _get_amount_with_fraction(amount)
    if amt is None:
        return None

    fraction_amount = 0
    if unit == SHORT_TIME_UNITS[0]:
        mod = _minute_mod
    elif unit == SHORT_TIME_UNITS[1]:
        mod = _hour_mod
    elif unit == SHORT_TIME_UNITS[2]:
        mod = _day_mod
    elif unit == LONG_TIME_UNITS[0]:
        mod = _week_mod
    elif unit == LONG_TIME_UNITS[1]:
        mod = _month_mod
    else:
        return None

    if fraction_percent != 0:
        fraction_amount = int(mod / (100/fraction_percent))
    amount_mins = amt * mod + fraction_amount

    return amount_mins
