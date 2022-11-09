def time_format(_time: str) -> int:
    # Economictime  "31 May, 2018, 07.52 PM IST"
    _time = _time[_time.find(",") + 2:]
    _time = _time[:_time.find(",")]
    return _time
