import re

ID_MATCHER = re.compile("<@!?([0-9]+)>")
START_WITH_INT_RE = re.compile(r"^(\d+)")
JUMP_LINK_RE = re.compile(r"https://(?:canary|ptb)?\.?discord(?:app)?.com/channels/\d*/(\d*)/(\d*)")