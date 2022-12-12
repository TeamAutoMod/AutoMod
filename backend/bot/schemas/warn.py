# type: ignore

from typing import Union, Dict



def Warn(warn_id: str,  warns: int) -> Dict[str, Union[str, int]]:
    return {
        "id": warn_id,
        "warns": warns
    }