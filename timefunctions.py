from datetime import datetime, date, timedelta
from tasks import Task

def convert_datetime_format(time, arrangement, obj_type):
    '''Converts a string in DD/MM/YY HH format to a datetime object or vice versa and returns it.'''
    match arrangement.lower():
        case "datetime":
            arrangement = "%d/%m/%y %H"
        case "24htime":
            arrangement = "%H%M"
    match obj_type.lower():
        case "string":
            return datetime.strftime(time, arrangement)
        case "object":
            return datetime.strptime(time, arrangement)

# def current_time():
#     '''Finds current datetime and returns it.'''
#     return datetime.now()


# def earlier_time(*times):
#     '''Determines which time object of multiple was the earliest.'''
#     return min(times)


def find_week_num():
    '''Reads the save file to determine what week number it is and returns it, as well as updates the file.'''
    with open("savefiles\weeksave.txt") as weekfile:
        weekinfo = weekfile.readline()
    old_str_date, old_week = weekinfo.split(":::")
    # Convert saved information into list of integers in [YYYY, MM, DD] format and then a date object.
    int_date = [int(t) for t in old_str_date.split("-")]
    old_date = date(*int_date)
    # Determines the integer number of days to substract from date to reach the Monday and convert into time object to subtract.
    old_monday = old_date - timedelta(days=old_date.weekday())
    current_date = date.today()
    this_monday = current_date - timedelta(days = current_date.weekday())
    # Find number of days and thus weeks that have past, and then the current week number.
    week_diff = (this_monday - old_monday).days // 7
    week_num = week_diff + int(old_week)
    # Rewrite save file.
    with open("savefiles\weeksave.txt", "w") as weekfile:
        weekfile.write(":::".join((str(current_date), str(week_num))))
    return week_num


def find_overdue_tasks(task_ls=Task.task_list):
    '''Identify all tasks with a due date around past from a given list.'''
    overdue_tasks = []
    for t in task_ls:
        if convert_datetime_format(t.due_date, "datetime", "object") < datetime.now():
            overdue_tasks.append(t)
    return overdue_tasks


def get_int_24h_time(h_min_decimal=False):
    '''Returns the current time in HHMM or (HH, MM) integer form.'''
    now = int(convert_datetime_format(datetime.now(), "24htime", "string"))
    if not h_min_decimal:
        return now
    # Else return a tuple of hours and minutes.
    return now//100 + round(now%100/60, 2)


# now = current_time()
# print(now)
# print(convert_to_strtime(now))
# print(convert_to_timeobject(convert_to_strtime(now)))
# print(find_week_num())