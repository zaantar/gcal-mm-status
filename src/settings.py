import json

with open('settings.json') as jsonFile:
    rawSettings = json.load(jsonFile)

print('settings:' + json.dumps(rawSettings))

def get_default_value(setting_name):
    return ''


def get_setting(setting_name):
    if setting_name in rawSettings:
        return rawSettings[setting_name]
    return get_default_value(setting_name)
