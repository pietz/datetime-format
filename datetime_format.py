import re

DATE_RE = r"(?P<date>\d{2,4}[-/.]\d{2}[-/.]\d{2,4})?"
SEP_RE = r"(?P<sep>\s|T)?"
TIME_RE = r"(?P<time>\d{2}:\d{2}(:\d{2})?\s*([AP]M)?)?"
FULL_RE = DATE_RE + SEP_RE + TIME_RE
YMD_RE = r"^(?P<ay>(?:[12][0-9])?[0-9]{2})(?P<bs>[-/.])(?P<cm>0[1-9]|1[0-2])(?P<ds>[-/.])(?P<ed>0[1-9]|[12][0-9]|3[01])$"
DMY_RE = r"^(?P<ad>0[1-9]|[12][0-9]|3[01])(?P<bs>[-/.])(?P<cm>0[1-9]|1[0-2])(?P<ds>[-/.])(?P<ey>(?:[12][0-9])?[0-9]{2})$"
MDY_RE = r"^(?P<am>0[1-9]|1[0-2])(?P<bs>[-/.])(?P<cd>0[1-9]|[12][0-9]|3[01])(?P<ds>[-/.])(?P<ey>(?:[12][0-9])?[0-9]{2})$"
HMS_RE = r"^(?P<aH>\d{1,2})(?P<bs>:?)(?P<cM>\d{2})(?:(?P<ds>:?)(?P<eS>\d{2}))?(?:(?P<fs>\s)?(?P<ga>[AP]M))?$"


def guess_datetime_format(values: list[str], n=100, return_dict=False):
    di = {}
    for val in values:
        if val is None:
            continue
        fmts = datetime_formats(val)
        for fmt in fmts:
            if fmt not in di:
                di[fmt] = 1
            di[fmt] += 1

    if len(di) == 0:
        return None

    if return_dict:
        return di

    return max(di, key=di.get)


def datetime_formats(value: str) -> list:
    assert "," not in value  # TODO: handle these cases
    m = re.match(FULL_RE, value)
    dates = "" if m["date"] is None else date_formats(m["date"])
    sep = "" if m["sep"] is None else m["sep"]
    time = "" if m["time"] is None else time_format(m["time"])
    return [date + sep + time for date in dates]


def date_formats(date_value: str) -> list:
    matches = []
    for p in [YMD_RE, MDY_RE, DMY_RE]:
        m = re.match(p, date_value)
        if m is None:
            continue
        fmt = ""
        for c in sorted(m.groupdict().keys()):
            if c[1] == "s":  # separator character
                fmt += "" if m[c] is None else m[c]
            else:  # year, month, day
                fmt += "%" + c[1] if len(m[c]) == 2 else "%Y"
        matches.append(fmt)
    return matches


def time_format(time_value: str) -> str:
    m = re.match(HMS_RE, time_value)
    fmt = ""
    for c in sorted(m.groupdict().keys()):
        if c[1] == "s":  # separator character
            fmt += "" if m[c] is None else m[c]
        else:
            fmt += "" if m[c] is None else "%" + c[1]
    if "M" in time_value:  # AM or PM
        fmt = fmt.replace("%H", "%I")
    return fmt
