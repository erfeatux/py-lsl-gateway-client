class LinksetDataException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class LinksetDataMemoryException(LinksetDataException):
    def __init__(self, key: str):
        super().__init__(
            f"An error occurred while trying to write linkset data '{key}': not enough memory"
        )


class LinksetDataNoKeyException(LinksetDataException):
    def __init__(self):
        super().__init__(
            "An error occurred while trying to write linkset data: empty key"
        )


class LinksetDataProtectedException(LinksetDataException):
    def __init__(self, key: str):
        super().__init__(
            f"An error occurred while trying to write linkset data '{key}': protected from overwrite"
        )


class LinksetDataNotFoundException(LinksetDataException):
    def __init__(self, key: str):
        super().__init__(
            f"An error occurred while trying to delete linkset data '{key}': not found"
        )


class LinksetDataNotUpdatedException(LinksetDataException):
    def __init__(self, key: str):
        super().__init__(
            f"An error occurred while trying to write linkset data '{key}': not changed"
        )


def exceptionByNum(num: int, msg: str = "") -> LinksetDataException:
    match num:
        case 1:
            return LinksetDataMemoryException(msg)
        case 2:
            return LinksetDataNoKeyException()
        case 3:
            return LinksetDataProtectedException(msg)
        case 4:
            return LinksetDataNotFoundException(msg)
        case 5:
            return LinksetDataNotUpdatedException(msg)
        case _:
            return LinksetDataException(msg)
