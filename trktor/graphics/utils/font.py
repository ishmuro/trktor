from PIL.ImageFont import ImageFont


def fontname(fnt: ImageFont) -> str:
    return f"{fnt.font.family} {fnt.font.style} ({fnt.font.size})"