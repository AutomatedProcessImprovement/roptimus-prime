class RosterManager:
    def __init__(self, roster):
        self.roster = roster

        """
        TODOS:
        
        RosterManager should be able to give the free bits for a certain resource on a certain day
        RosterManager should be able to give the remaining capacity for a certain resource
        """

    def get_remaining_cap_resource(self, res, day=None):
        roster = self.roster.resources
        for i in roster:
            if i.resource_id == res:
                if day is not None:
                    if type(day) == list:
                        return i.get_free_cap(day)
                    return i.get_free_cap(day)
                return i.get_free_cap()

    def get_total_remaining_cap_resource(self, res):
        roster = self.roster.resources
        for i in roster:
            if i.resource_id == res:
                return i.get_free_cap()['total']

    def get_accessible_bits(self, resource, day=None):
        roster = self.roster.resources
        for i in roster:
            if i.resource_id == resource:
                if day is not None:
                    return i.get_changeable_bits(day)
                return i.get_changeable_bits()

    def set_new_shifts_on_resource(self, resource, shifts, day=None):
        roster = self.roster.resources
        for i in roster:
            if i.resource_id == resource:
                return i.set_shifts(shifts, day)

    def to_json(self):
        return self.roster.to_json()
