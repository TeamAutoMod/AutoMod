from typing import Union, Dict



def Stats(_id: int, cmds: int, customs: int) -> Dict[str, Union[str, int]]:
    return {
        "id": f"{_id}",
        "used_commands": cmds,
        "used_customs": customs
    }