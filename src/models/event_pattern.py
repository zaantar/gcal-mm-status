import re


class EventPattern:
    pattern = ''
    flags = []
    suffix = ''
    status = ''

    def __init__(self, pattern_settings):
        self.pattern = pattern_settings['pattern']
        self.flags = pattern_settings['flags']
        self.suffix = pattern_settings['suffix']
        self.status = pattern_settings['status']

    def get_re_flags(self):
        flag_values = [eval('re.%s' % flag_name) for flag_name in self.flags]
        result = 0
        for flag_value in flag_values:
            result |= flag_value
        return result

    def is_match(self, event_summary):
        regex_pattern = re.compile(self.pattern, self.get_re_flags())
        match = re.search(regex_pattern, event_summary)
        return match is not None
