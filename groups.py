class Group():
    group_list = []

    def __init__(self, name, significance, colour="white") -> None:
        self.name = name
        self.significance = float(significance)
        self.colour = colour
        self.tasks = []
        Group.group_list.append(self)
    
    def __str__(self) -> str:
        return ", ".join((self.name, self.colour))

    def delete_group(self):
        '''Deletes all references to the group.'''
        # Remove references in task lists.
        for t in self.tasks:
            t.groups.remove(self)
            # Remove references in string task name lists.
            for s in t.str_groups:
                if s.lower() == self.name.lower():
                    t.remove(s)
        # Remove group from class list of groups.
        Group.group_list.remove(self)