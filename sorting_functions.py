from tasks import Task, Assessment, Homework
from fileio import Settings
'''
Type: Assignment, Exam, Homework, Task
Group: ###, ###, ###...
Importance: High, Medium, Low

Due date: <->
Desc. Size: <->
Asc. Size: <->
'''

def sort_by_type(raw_list=Task.task_list, unseparated = False):
    '''Sort the list of tasks by their type. Assignment, Exam, Homework, Task.'''
    assignments_ls, exam_ls, homework_ls, tasks_ls = [], [], [], []
    for t in raw_list:
        if type(t) is Assessment:
            if t.type == "Exam":
                exam_ls.append(t)
            elif t.type == "Assignment":
                assignments_ls.append(t)
        elif type(t) is Homework:
            homework_ls.append(t)
        elif type(t) is Task:
            tasks_ls.append(t)
    if unseparated:
        return  assignments_ls + exam_ls + homework_ls + tasks_ls
    else:
        return (["Assignments:", assignments_ls], ["Exam:", exam_ls], ["Homework:", homework_ls], ["Tasks:", tasks_ls])


def sort_by_group(raw_list=Task.task_list, unseparated=None):
    '''Sort the list of tasks by their groups.'''
    group_dict = {}
    # Add each task in the list to the dictionary under the group it's in with the highest significance.
    for t in raw_list:
        highest_group = t.groups[0]
        if (highest_group.name, highest_group.significance) in group_dict:
            group_dict[highest_group.name, highest_group.significance].append(t)
        else:
            group_dict[highest_group.name, highest_group.significance] = [t]
    
    # Sort the task groups by descending order of significance.
    sig_keyed_ls = list(group_dict.items())
    sig_keyed_ls.sort(key=lambda g: g[0][1], reverse=True)
    if unseparated:
        lsls = [t_ls for (g_info, t_ls) in sig_keyed_ls]
        return (sum(lsls, [])) # Remove internal layer of lists: [[a], [b]] into [a, b]
    else:
        # Create a copy of the list without the significance values and return it.
        return [[g_info[0], t_ls] for (g_info, t_ls) in sig_keyed_ls]


def sort_by_due_date(raw_list=Task.task_list, placeholder=None):
    '''Sort the list of tasks by their due date earliest to latest.'''
    return sorted(raw_list, key=lambda t: t.due_date)


def sort_by_size_descending(raw_list=Task.task_list, placeholder=None):
    '''Sort the list of tasks by their size, descending.'''
    return sorted(raw_list, key=lambda t: t.size, reverse=True)


def sort_by_size_ascending(raw_list=Task.task_list, placeholder=None):
    '''Sort the list of tasks by their size, descending.'''
    return sorted(raw_list, key=lambda t: t.size)


def sort_by_importance(raw_list=Task.task_list, unseparated=False):
    '''Sort the list of tasks by their importance highest to lowest.'''
    low_ls, medium_ls, high_ls = [], [], []
    for t in raw_list:
        match t.importance:
            case "Low":
                low_ls.append(t)
            case "Medium":
                medium_ls.append(t)
            case "High":
                high_ls.append(t)
    if unseparated:
        return high_ls + medium_ls + low_ls
    else:
        return (["High:", high_ls], ["Medium:", medium_ls], ["Low:", low_ls])


def config_sort_ls(ls_to_sort=Task.task_list, procedure_index=0):
    '''Recursively return a sorted copy of the list of tasks according to settings configuration.
    May be a single list if both sorting procedures yield one list, or in ([label, subls], ...) structure otherwise.'''
    # Determine whether the sort function for this function call will yield a one-dimentional list or otherwise.
    config = Settings.sort_procedure
    procedure = config[procedure_index].lower()
    onels = True
    if procedure_index == 0 and procedure in ("type", "group", "importance"):
        onels = False
    match procedure:
        case "type":
            ls_to_sort = sort_by_type(ls_to_sort, onels)
        case "group":
            ls_to_sort = sort_by_group(ls_to_sort, onels)
        case "due_date":
            ls_to_sort = sort_by_due_date(ls_to_sort, onels)
        case "size_descending":
            ls_to_sort = sort_by_size_descending(ls_to_sort, onels)
        case "size_ascending":
            ls_to_sort = sort_by_size_ascending(ls_to_sort, onels)
        case "importance":
            ls_to_sort = sort_by_importance(ls_to_sort, onels)
    if not onels:
        return [[label, config_sort_ls(subls, 1)] for [label, subls] in ls_to_sort]
    elif procedure_index == 0:
        # Standardise the output format by reformatting one-dimensional lists into ([sort_type_label, ls]) form.
        label = config[1]
        if label.lower() == "none":
            # Use the first sorter as the label if the second is 'none'. 
            label = config[0]
        label = "Sorted by " + label.replace("_", " ").title()
        return ([label, config_sort_ls(ls_to_sort, 1)],) # A comma allows for returning one item tuples. 
    else:
        # Part of second sort, the deepest level and thus without need to continue.
        return ls_to_sort