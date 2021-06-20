from ..functions.CaseClaim import caseClaim



async def run(plugin, ctx, case):
    # In case a user adds the # in front of the case
    case = case.split("#")[1] if len(case.split("#")) == 2 else case

    await caseClaim(plugin, ctx, case)