import sys; sys.path.insert(0, '..')

from objects.storage_indicators import _StoresText, _DropKwargs
from typing import Union


class Action(_DropKwargs):
    """ class that represents some common action  """
    def __init__(self, **kwargs):
        super(Action, self).__init__(**kwargs)


class PrintAction(Action, _StoresText):
    def __init__(self, text: str) -> None:
        assert isinstance(text, str)
        kwargs = locals(); kwargs.pop('self')
        super(PrintAction, self).__init__(**kwargs)


class ShowImage(Action):
    """ Action: show image. Contains image_name - filename name, that is stored in data/temp """
    def __init__(self, image_name: str, caption: str = '') -> None:
        assert isinstance(image_name, str)
        assert isinstance(caption, str)
        self.caption = caption
        self.image_name = image_name
        super(ShowImage, self).__init__()


class ShowPoll(Action):
    """ Action: show poll. Contains the title of the poll and (the list of) its options """
    def __init__(self, title: str, options: Union[list, tuple, set]) -> None:
        assert isinstance(title, str)
        assert isinstance(options, (list, tuple, set))
        self.title = title
        self.options = options
        super(ShowPoll, self).__init__()
