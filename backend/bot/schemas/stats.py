from typing import Union, Dict



def Stats(_id: int) -> Dict[str, Union[str, int]]:
    return {
        "id": f"{_id}",
        "used_commands": 1,
        "used_customs": 0
    }