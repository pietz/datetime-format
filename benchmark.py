from datetime import datetime, timedelta
from random import randint
from time import time

import polars as pl

from datetime_format import guess_datetime_format

def rnd_dt_str(format="%m-%d-%Y %H:%M:%S"):
    start = datetime(1970, 1, 1)
    offset = timedelta(seconds=randint(0, int(1e9)))
    return (start + offset).strftime(format)

def get_dt_format(col: list, patterns: list, n: int = 100):
    for val in col[:n]:
        for pattern in patterns.keys():
            try:
                _ = datetime.strptime(val, pattern)
                patterns[pattern] += 1
            except:
                pass

    if sum(patterns.values()) == 0:
        return False

    return max(patterns, key=patterns.get)

def create_dt_patterns():
    dates = create_date_patterns()
    times = ["%H:%M:%S", "%H:%M", "%I:%M:%S%p", "%I:%M%p", "%I:%M:%S %p", "%I:%M %p"]
    seps = [" ", "T", ""]
    dts = [d + s + t for d in dates for s in seps for t in times]
    dts += dates + times
    return {x: 0 for x in dts}

def create_date_patterns():
    date_opts = [
        "%Y{0}%m{0}%d",
        "%m{0}%d{0}%Y",
        "%d{0}%m{0}%Y",
        "%y{0}%m{0}%d",
        "%m{0}%d{0}%y",
        "%d{0}%m{0}%y",
    ]
    return [x.format(sep) for sep in ["-", "/", "."] for x in date_opts]

def to_datetime(values, errors='raise'):

    last_success_pattern = patterns[0]
    dti = []

    for value in values:
        try:
            dt = datetime.strptime(value, last_success_pattern)
        except ValueError:
            for pattern in [last_success_pattern] + patterns:
                try:
                    dt = datetime.strptime(value, pattern)
                except ValueError:
                    if errors == 'raise':
                        raise ValueError(f'Unknown format for "{value}"')
                    elif errors == 'coerce':
                        dt = None  # invalid value is set to None
                    elif errors == 'ignore':
                        dt = value  # invalid value returns the input
                else:
                    last_success_pattern = pattern
                    break

        dti.append(dt)
    return dti

fmt = "%m-%d-%Y %H:%M:%S"
l = [rnd_dt_str(fmt) for _ in range(100000)]
s = pl.Series("ts", l, pl.Utf8)
df = pl.DataFrame(s)

patterns_dict = create_dt_patterns()
patterns = list(patterns_dict.keys())
print(len(patterns))

assert fmt in patterns

print("START")
t1 = time()

for pattern in patterns:
    try:
        df=df.with_columns(Date=pl.col('ts').str.strptime(pl.Datetime(), pattern))
    except:
        pass

print("Polars brute force")
t2 = time()
print(t2 - t1)

_ = guess_datetime_format(l)

print("RegEx")
t3 = time()
print(t3 - t2)

# _ = to_datetime(s, errors='raise')

_ = get_dt_format(l, patterns_dict)

print("Datetime brute force")
t4 = time()
print(t4 - t3)