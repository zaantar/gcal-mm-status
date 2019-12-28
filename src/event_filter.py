import re

WORK_FILTER = r"^work.*"


def filter_events(events):
    return [event for event in events if re.search(WORK_FILTER, event['summary'], re.IGNORECASE)]
