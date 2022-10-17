class RosterManager:
    def __init__(self, roster):
        self.roster = roster

        """
        TODOS:
        
        RosterManager should be able to give the free bits for a certain resource on a certain day
        RosterManager should be able to give the remaining capacity for a certain resource
        """

    def remaining_cap_resource(self, res, day=None):
        roster = self.roster.resources
        for i in roster:
            if i.resource_id == res:
                if day is not None:
                    return i.day_free_cap[day]
                return i.day_free_cap


