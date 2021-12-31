from groups import Group
from tasks import Task, Assessment, Homework

class Settings():
    sort_procedure = ["importance", "none"]
    auto_remove_overdue = False
    original = None
    always_dark_theme = False
    natural_dark_theme_change = True
    working_hours = [9, 22]

    load_failures = 0


    def log_failures(boolean):
        '''If the given output of a function is False, indicating failure, log it in load_failures.'''
        if boolean == False:
            Settings.load_failures += 1
    

    def set_sort_procedure(procedure_ls, autolog_failures=False):
        '''Checks whether the given procedure list is valid and adds it if so.'''
        formatted_procedure = set([e.lower() for e in procedure_ls])
        sorts_valid = set(formatted_procedure).issubset({"none", "type", "group", "due_date", "size_descending", "size_ascending", "importance"})
        if len(procedure_ls) == 2 and sorts_valid:
            Settings.sort_procedure = procedure_ls
            return True
        # If failed:
        if autolog_failures:
            Settings.load_failures += 1
        return False
    
    def set_working_hours(working_h, autolog_failures=False):
        '''Checks whether the given list contains two elements of 24h time where the first is earlier.'''
        if type(working_h) == list and len(working_h) == 2:
            if all([type(e) == str for e in working_h] + [len(e) in (1, 2) for e in working_h]):
                if all([e.isdecimal() for e in working_h]):
                    start, end = [int(e) for e in working_h]
                    if start < end and start in range(24) and end in range(24):
                        Settings.working_hours = [start, end]
                        return True
        # If failed:
        if autolog_failures:
            Settings.load_failures += 1
        return False
    
    def validate_str_bool(boolean, autolog_failures=False):
        '''Check that the input is either '0' or '1'.'''
        if boolean in ("0", "1"):
            return True
        # If failed:
        if autolog_failures:
            Settings.load_failures += 1
        return False


def fileread():
    '''Reads the group and task save files and reinitiates them into class instances.
    Also reads the settings file and records information in the settings class.'''
    # Groups.
    with open("savefiles\groupsaves.txt") as groupfile:
        # Splits string data into list of sublists containing each group's name and colour.
        group_ls = [g.split(":::") for g in groupfile.read().split("\n")]
    # Initiatise groups.
    for (name, significance, colour) in group_ls:
        Group(name, significance, colour)

    # Tasks.
    with open("savefiles\\tasksaves.txt") as taskfile:
        task_str = taskfile.read()
    # Splits string data into numerous variables and initialises them into task instances.
    for t in task_str.split("\n:::")[1:]:
        (t_type, t_name, t_groups_str, t_due, t_size, t_completion, t_importance, t_notes_str) = t.split("___ ")
        t_groups = t_groups_str.split("///")
        t_notes = t_notes_str.split("|||")
        match t_type:
            case "Task":
                Task(t_name, t_groups, t_due, t_size, t_importance, t_notes).completion = t_completion
            case "Homework":
                Homework(t_name, t_groups, t_due, t_size, t_importance, t_notes).completion = t_completion
            case "Exam" | "Assignment":
                Assessment(t_name, t_type, t_groups, t_due, t_size, t_importance, t_notes).completion = t_completion

    # Settings.
    with open("savefiles\\settingsaves.txt") as settingsfile:
        text = [line.rstrip("\n") for line in settingsfile.readlines()]
    i = 0
    while i < len(text):
        text[i] = text[i].split(" ###", 1) # Make only one split for each line of the text, creates 2D list.
        i += 1
    Settings.original = text
    for line in text:
        setting_info = line[0].split(":::", 1) # Keep as 'info' because comment only lines return one value after split.
        match setting_info[0]:
            case "SORT PROCEDURE":
                Settings.set_sort_procedure(setting_info[1].split(", ", 1), autolog_failures=True) # Make only one split.
            case "AUTO REMOVE OVERDUE":
                if Settings.validate_str_bool(setting_info[1]) == True:
                    Settings.auto_remove_overdue = bool(int(setting_info[1]))
            case "ALWAYS DARK THEME":
                if Settings.validate_str_bool(setting_info[1]) == True:
                    Settings.always_dark_theme = bool(int(setting_info[1]))
            case "NATURAL DARK THEME CHANGE":
                if Settings.validate_str_bool(setting_info[1]) == True:
                    Settings.natural_dark_theme_change = bool(int(setting_info[1]))
            case "WORKING HOURS":
                Settings.set_working_hours(setting_info[1].split(", ", 1), autolog_failures=True)


def filewrite():
    '''Saves all data into text files to retrieve next time.'''
    # Groups.
    groups_str = ""
    for g in Group.group_list:
        groups_str += "".join((g.name, ":::", str(g.significance), ":::", g.colour, "\n"))
    with open("savefiles\\groupsaves.txt", "w") as groupfile:
        groupfile.write(groups_str[:-1])

    # Tasks.
    tasks_str = ""
    for t in Task.task_list:
        tasks_str += "\n:::"
        if type(t) in (Task, Homework):
            tasks_str += "___ ".join((t.__class__.__name__, t.name, "///".join(t.str_groups), t.due_date, t.size, t.completion, t.importance, "|||".join(t.notes)))
        elif type(t) == Assessment:
            tasks_str += "___ ".join((t.type, t.name, "///".join(t.str_groups), t.due_date, t.size, t.completion, t.importance, "|||".join(t.notes)))
    with open("savefiles\\tasksaves.txt", "w") as taskfile:
        taskfile.write(tasks_str)
    
    # Settings.
    write_out = Settings.original # 2D list of lines with inner list of useful information, then comments. [[setting_info, comment], ...]
    i = 0
    while i < len(write_out):
        # Refresh all settings values.
        setting_info = write_out[i][0].split(":::", 1)
        if setting_info == "":
            pass
        else:
            match setting_info[0]:
                case "SORT PROCEDURE":
                    setting_info[1] = ", ".join(Settings.sort_procedure)
                case "AUTO REMOVE OVERDUE":
                    setting_info[1] = str(int(Settings.auto_remove_overdue))
                case "ALWAYS DARK THEME":
                    setting_info[1] = str(int(Settings.always_dark_theme))
                case "NATURAL DARK THEME CHANGE":
                    setting_info[1] = str(int(Settings.natural_dark_theme_change))
                case "WORKING HOURS":
                    setting_info[1] = ", ".join([str(e) for e in Settings.working_hours])
            write_out[i][0] = ":::".join(setting_info)
        i += 1
    # Join list form object into a string and then write it up.
    i = 0
    while i < len(write_out):
        write_out[i] = " ###".join(write_out[i])
        i += 1
    write_out = "\n".join(write_out)
    with open("savefiles\\settingsaves.txt", "w") as settingsfile:
        settingsfile.write(write_out)


# fileread()
# print(Settings.auto_remove_overdue, Settings.sort_procedure)
# filewrite()