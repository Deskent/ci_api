class WeekDay:
    WEEK_DAYS: tuple[str] = (
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
    )

    def __init__(self, data: list | str):
        self.as_string: str = ''
        self.as_list: list[str] = []
        if isinstance(data, list):
            self.as_string = self._to_string(data)
            self.as_list = self._to_list(self.as_string)
        elif isinstance(data, str):
            self.as_list = self._to_list(data)
            self.as_string = self._to_string(self.as_list)

    def _to_string(self, data: list[str]) -> str:
        """Convert list ['monday', 'saturday', 'thursday'] to string like '053'"""

        if 'all' in data:
            week_days_string = 'all'
        else:
            week_days_string = ''.join(
                (str(self.WEEK_DAYS.index(day))
                 for day in data
                 if day in self.WEEK_DAYS)
            )

        return week_days_string

    def _to_list(self, data: str) -> list[str]:
        """Convert string like '053' to list ['monday', 'saturday', 'thursday']"""

        if data == 'all':
            return list(self.WEEK_DAYS)

        return [self.WEEK_DAYS[int(index)] for index in data]
