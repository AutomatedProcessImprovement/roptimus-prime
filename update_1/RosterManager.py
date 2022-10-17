class RosterManager:
    def __init__(self, roster):
        self.roster = roster

        """
        TODOS:
        
        RosterManager should be able to give the free bits for a certain resource on a certain day
        RosterManager should be able to give the remaining capacity for a certain resource
        """

    def remaining_cap_resource(self, res):
        roster = self.roster.roster
        resource = roster[roster['resource_id'].str.contains(res)]
        return resource.to_string()

