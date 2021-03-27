import discord
from discord import NotFound, Forbidden




def paginate(input, max_lines=23, max_chars=1200, prefix="", suffix=""):
    max_chars -= len(prefix) + len(suffix)
    lines = str(input).splitlines(keepends=True)
    pages = []
    page = ""
    count = 0
    for line in lines:
        if len(page) + len(line) > max_chars or count == max_lines:
            if page == "":
                # single 2k line, split smaller
                words = line.split(" ")
                for word in words:
                    if len(page) + len(word) > max_chars:
                        pages.append(f"{prefix}{page}{suffix}")
                        page = f"{word} "
                    else:
                        page += f"{word} "
            else:
                pages.append(f"{prefix}{page}{suffix}")
                page = line
                count = 1
        else:
            page += line
        count += 1
    pages.append(f"{prefix}{page}{suffix}")
    return pages
