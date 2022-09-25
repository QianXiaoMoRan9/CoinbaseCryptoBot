from datetime import datetime

"""
Given a start datetime and end date time, return (year, month) pairs in sequence covering start and end
"""


def get_sorted_year_month(start_datetime: datetime, end_datetime: datetime):
    result = list()
    start_year = start_datetime.year
    end_year = end_datetime.year

    start_month = start_datetime.month
    end_month = end_datetime.month

    for year in range(start_year, end_year + 1):
        month_list = [x for x in range(1, 13)]
        if year == end_year:
            month_list = [x for x in range(1, end_month + 1)]
        elif year == start_year:
            month_list = [x for x in range(start_month, 13)]
        for month in month_list:
            result.append((year, month))
    return result
