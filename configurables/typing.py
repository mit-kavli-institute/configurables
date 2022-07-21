import os
import typing

PathLike = typing.Union[str, bytes, os.PathLike]
CastLike = typing.Callable[[typing.Any], typing.Any]
ConfigLike = typing.Dict[str, typing.Any]
