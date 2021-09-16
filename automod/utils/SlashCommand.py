import inspect



def get_callback_params(wrapper):
    signature = inspect.signature(wrapper)
    params = {}
    for k, v in signature.parameters.items():
        annotation = v.annotation
        if k is not None and k != "self" and k != "ctx":
            params[k] = {
                "description": "Test",
                "type": 1,
                "required": True
            }
    return params


class SlashCommand:
    def __init__(self, name, description, wrapper):
        self.name = name
        self.callback = wrapper
        self.payload = {
            "name": name,
            "description": description,
        }

        options = []
        params = get_callback_params(wrapper)
        if len(params) > 0:
            for param, data in params.items():
                options.append(
                    {
                        "name": param,
                        "description": data["description"],
                        "type": data["type"],
                        "required": data["required"]
                    }
                )
        self.payload.update({
            "options": options
        })
