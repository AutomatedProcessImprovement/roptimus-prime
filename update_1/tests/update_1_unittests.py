import unittest

from update_1.update_1 import Resource


class ResourceTests(unittest.TestCase):
    _valid_resource_json = {
        "id": "valid_resource_json",
        "name": "valid_resource_json",
        "time_periods": [
            {
                'from': "MONDAY",
                'to': "MONDAY",
                'beginTime': "09:00:00",
                'endTime': "12:00:00"
            },
            {
                'from': "MONDAY",
                'to': "MONDAY",
                'beginTime': "13:00:00",
                'endTime': "16:00:00"
            },
            {
                'from': "TUESDAY",
                'to': "TUESDAY",
                'beginTime': "09:00:00",
                'endTime': "12:00:00"
            },
            {
                'from': "TUESDAY",
                'to': "TUESDAY",
                'beginTime': "14:00:00",
                'endTime': "17:00:00"
            },
            {
                'from': "WEDNESDAY",
                'to': "WEDNESDAY",
                'beginTime': "14:00:00",
                'endTime': "17:00:00"
            },
            {
                'from': "THURSDAY",
                'to': "THURSDAY",
                'beginTime': "09:00:00",
                'endTime': "13:00:00"
            },
            {
                'from': "THURSDAY",
                'to': "THURSDAY",
                'beginTime': "14:00:00",
                'endTime': "17:00:00"
            },
        ]
    }

    def test_enable_all(self):
        pass

    def test_disable_all(self):
        pass

    def test_enable_day(self):
        pass

    def test_disable_day(self):
        pass

    def test_enable_day_slot(self):
        pass

    def test_disable_day_slot(self):
        pass

    def test_equals_returns_false_on_different_id_and_name(self):
        pass

    def test_equals_returns_true_on_similar_id_or_name(self):
        pass


class RosterTests(unittest.TestCase):
    def test_verify_valid_roster(self):
        pass


if __name__ == '__main__':
    unittest.main()
