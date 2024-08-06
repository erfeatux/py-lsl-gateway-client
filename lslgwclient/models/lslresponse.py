from pydantic import BaseModel
from uuid import UUID
import re

from lslgwlib.models import HTTPData, Avatar, Region


# LinkSet API responses model
class LSLResponse(HTTPData):
    def __init__(self, *args, **kwargs) -> None:
        # constructor by http response and parsed data
        if (
            len(args) == 2
            and hasattr(args[0], "headers")
            and isinstance(args[1], BaseModel | list | int | float | str | UUID | None)
        ):
            headers: dict[str, str] = dict()
            for headName in args[0].headers:
                if not headName.startswith("X-SecondLife"):
                    headers[headName] = args[0].headers[headName]
            super().__init__(
                owner=Avatar(
                    args[0].headers["X-SecondLife-Owner-Key"],
                    args[0].headers["X-SecondLife-Owner-Name"],
                ),
                objectKey=UUID(args[0].headers["X-SecondLife-Object-Key"]),
                objectName=args[0].headers["X-SecondLife-Object-Name"],
                position=re.sub(
                    r"(\(|\))", "", args[0].headers["X-SecondLife-Local-Position"]
                ).split(","),
                rotation=re.sub(
                    r"(\(|\))", "", args[0].headers["X-SecondLife-Local-Rotation"]
                ).split(","),
                velocity=re.sub(
                    r"(\(|\))", "", args[0].headers["X-SecondLife-Local-Velocity"]
                ).split(","),
                region=Region(args[0].headers["X-SecondLife-Region"]),
                production=args[0].headers["X-SecondLife-Shard"] == "Production",
                data=args[1],
                headers=headers,
            )
        else:
            super().__init__(**kwargs)
