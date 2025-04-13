from model_utils import Choices


class LogBadgeChoices:
    RED = 'R'
    GREEN = 'G'
    INFO = 'I'

    choices = Choices(
        (RED, "Red"),
        (GREEN, "Green"),
        (INFO, "Info")
    )