from groups import Group

class Task():
    task_list = []

    def __init__(self, name, str_groups=[], due_date="'Unspecified'", size="'Unspecified'", importance="Low", notes=[]) -> None:
        self.name = name
        self.str_groups = str_groups
        self.groups = []
        # Tag tasks under matching groups, or create one if new.
        i = 0
        while i < len(str_groups):
            found = False
            for g in Group.group_list:
                if str_groups[i] == g.name:
                    g.tasks.append(self)
                    self.groups.append(g) 
                    found = True
            if not found:
                g = Group(str_groups[i], 0).tasks.append(self)
                self.groups.append(g)
            i += 1
        self.due_date = due_date
        self.size = size
        self.importance = importance
        self.notes = notes
        self.completion = 0
        Task.task_list.append(self)
    
    def __str__(self) -> str:
        formatted_notes_ls = []
        for line in self.notes:
            if line[:3] == "///":
                formatted_line = line[3:].upper()
            else:
                formatted_line = line
            formatted_notes_ls.append(formatted_line)
        # formatted_notes_ls = "\n".join([line[3:].upper() if line[:3] == "///" else line for line in self.notes])
        return "'{}' from {}. Due at {}, approximately {} hours of work total and {}% complete. {} importance.".format(
            self.name, ", ".join([e for e in self.str_groups]), self.due_date, self.size, self.completion, self.importance
        )

    def add_group(self, str_group_name):
        '''Tags the task with a new group, in the correct location based off significance.'''
        # Finds and adds group to group object list.
        for g in Group.group_list:
            if g.name.lower() == str_group_name.lower():
                self.groups.append(g)
                break
        # Sorts the group object list by most significant to least.
        self.groups.sort(key=lambda x: x.significance, reverse=True)
        # Inserts the name of the added group in the correct position of the group string name list using the object list.
        self.str_groups.insert(self.groups.index(g), g.name)

    def delete_task(self):
        '''Deletes all references of the task.'''
        # Remove task from its groups.
        for g in self.groups:
            g.tasks.remove(self)
        # Remove task from the class list of tasks.
        Task.task_list.remove(self)


class Assessment(Task):
    def __init__(self, name, type, str_groups=[], due_date="'Unspecified'", size="'Unspecified'", importance="Low", notes=[]) -> None:
        super().__init__(name, str_groups, due_date, size, importance, notes)
        self.type = type

    def __str__(self) -> str:
        return "{}: ".format(self.type) + super().__str__()


class Homework(Task):
    def __init__(self, name, str_groups=[], due_date="'Unspecified'", size="'Unspecified'", importance="Low", notes=[]) -> None:
        super().__init__(name, str_groups, due_date, size, importance, notes)
    
    def __str__(self) -> str:
        return "Homework: " + super().__str__()