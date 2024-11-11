from typing import Any, Generator, Protocol, Self


class XmlElementLike(Protocol):
    """
    Protocol for all ``elem`` attributes used in PythonTmx. Any class that
    follows this protocol can be used as replacement for an lxml ``_Element``
    in the context of this library.
    """

    tag: str
    """
    The tag if the xml Element.
    """
    text: str | None
    """
    The text of the Element, if any.
    """
    tail: str | None
    """
    The tail (text `after` the closing tag) of the Element, if any.
    """

    def get(self, key: str, default: None) -> Any:
        """
        Should any of the element's attribute using a key, and providing a
        default if the key doesn't exists.
        """
        ...

    def __iter__(self) -> Generator[Self]:
        """
        Should yield all direct children and all children should be of the same
        type.
        """
        ...

    def __len__(self) -> int:
        """
        Should return the amount of sub elements when calling ``len(element)``
        """
