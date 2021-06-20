import re

ID_MATCHER = re.compile("<@!?([0-9]+)>")
START_WITH_INT_RE = re.compile(r"^(\d+)")
JUMP_LINK_RE = re.compile(r"https://(?:canary|ptb)?\.?discord(?:app)?.com/channels/\d*/(\d*)/(\d*)")
INVITE_RE = re.compile(r"(?:https?://)?(?:www\.)?(?:discord(?:\.| |\[?\(?\"?'?dot'?\"?\)?\]?)?(?:gg|io|me|li)|discord(?:app)?\.com/invite)/+((?:(?!https?)[\w\d-])+)", flags=re.IGNORECASE)
URL_RE = re.compile(r'((?:https?://)[a-z0-9]+(?:[-._][a-z0-9]+)*\.[a-z]{2,5}(?::[0-9]{1,5})?(?:/[^ \n<>]*)?)', re.IGNORECASE)