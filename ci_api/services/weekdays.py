class WeekDay:
    WEEK_DAYS: tuple[str] = (
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
    )

    @classmethod
    def to_string(cls, data: list[str]) -> str:
        if 'all' in data:
            week_days_string = 'all'
        else:
            week_days_string = ''.join(
                (str(cls.WEEK_DAYS.index(day))
                 for day in data
                 if day in cls.WEEK_DAYS)
            )

        return week_days_string

    @classmethod
    def to_list(cls, data: str) -> list[str]:
        if data == 'all':
            return list(cls.WEEK_DAYS)
        return [cls.WEEK_DAYS[int(index)] for index in data]
