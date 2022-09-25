import pprint


def pretty_print(obj: dict) -> str:
    return pprint.pformat(obj, indent=2, sort_dicts=False)
