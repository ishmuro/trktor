import logging
import os
from typing import List, Union, Tuple, Optional

from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(format="%(message)s", level=logging.INFO)
log = logging.getLogger(__name__)
DEFAULT_CONFIG = "./config.toml"
IMAGE_SRC = "./assets/banner.gif"
TEXT_MASK_SRC = "./assets/text_mask.png"
H_FONT_PATH = "./assets/fonts/Druk Wide Cyr Medium.otf"
C_FONT_PATH = "./assets/fonts/Montserrat-Medium.ttf"

TRANSPARENT_RGBA = (255, 255, 255, 0)

FONT_SIZE = 42

BAR_LENGTH = 620
BAR_HEIGHT = 50
BAR_RIGHT_MARGIN = 20
BAR_OUTLINE_WIDTH = 5

AA_FACTOR = 1

cursor_y = 0

def add_offset(y: int) -> int:
    return cursor_y + y


def load_font(font_path: Union[os.PathLike, str], size: int) -> ImageFont:
    fnt: ImageFont
    if os.path.exists(font_path):
        try:
            fnt =  ImageFont.truetype(font_path, size=size)
        except OSError:
            log.warning(f"Font file {font_path} not found, loading default font.")
            fnt =  ImageFont.load_default()
    else:
        fnt =  ImageFont.load_default()

    log.info(f"Font loaded: {fnt.font.family} {fnt.font.style} ({fnt.size})")
    return fnt


def draw_ellipse(image: Image, bounds: Tuple[int, int, int, int], width: int = 1, outline: str = "white") -> Image:
    mask = Image.new("L", size=[int(dim * AA_FACTOR) for dim in image.size], color = "black")
    draw = ImageDraw.Draw(mask)

    for offset,fill in (width/-2.0, "white"), (width/2.0, "black"):
        left, top = [(val + offset) * AA_FACTOR for val in bounds[:2]]
        right, bot = [(val - offset) * AA_FACTOR for val in bounds[2:]]
        draw.ellipse([left, top, right, bot], fill=fill)

    if AA_FACTOR != 1:
        mask = mask.resize(image.size, Image.Resampling.LANCZOS)

    image.paste(outline, mask=mask)


def add_nickname(banner: Image, name: str, font: ImageFont, mask: Optional[Image] = None) -> Tuple[Image, int]:
    # Main text layer
    text_layer = Image.new("RGBA", banner.size, (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_layer)
    text_draw.text((10, 10), name, font=font, fill="black")

    banner.alpha_composite(text_layer, (0, cursor_y))

    if mask is not None:
        # Secondary text layer for accents, has priority over main
        overlay_layer = Image.new("RGBA", current_frame.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay_layer)
        overlay_draw.text((10, 10), name, font=font, fill="white")

        mask_shape = mask.getbbox(alpha_only=True)
        overlay_layer = overlay_layer.crop(mask_shape)

        banner.alpha_composite(overlay_layer, (0, cursor_y))

    _, upper, _, lower = text_layer.getbbox(alpha_only=True)

    return banner, int(lower) - int(upper)

def draw_progressbar(banner: Image, percent: int) -> Image:
    layer = Image.new("RGBA", banner.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(layer)

    main_layer = Image.new("RGBA", banner.size, (255, 255, 255, 0))
    main_draw = ImageDraw.Draw(main_layer)

    x0 = banner.size[0] - BAR_RIGHT_MARGIN - BAR_LENGTH
    y0 = BAR_HEIGHT // 4
    x1 = banner.size[0] - BAR_RIGHT_MARGIN
    y1 = BAR_HEIGHT // 4 + BAR_HEIGHT
    radius = BAR_HEIGHT // 2

    fx1 = x1 - (100 - percent) * 0.01 * BAR_LENGTH

    draw.rounded_rectangle([x0, y0, fx1, y1], radius=radius, fill=(220, 105, 66), outline=None)
    main_draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill="black", outline=None)

    mask = Image.new("L", banner.size, color="white")
    mask_draw = ImageDraw.Draw(mask)

    mx0, my0 = [(val + BAR_OUTLINE_WIDTH) for val in [x0, y0]]
    mx1, my1 = [(val - BAR_OUTLINE_WIDTH) for val in [x1, y1]]
    mradius = (my1 - my0) // 2

    mask_draw.rounded_rectangle([mx0, my0, mx1, my1], radius=mradius, fill="black")

    layer.paste(main_layer, mask=mask)
    banner.alpha_composite(layer, (0, cursor_y))

    return banner

def add_rank(banner: Image, rank: int, font: ImageFont) -> Image:
    layer = Image.new("RGBA", banner.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(layer)
    draw.text((40, 10), f"Rank: {rank}", font=font, fill="black")

    banner.alpha_composite(layer, (0, cursor_y))

    return banner



if __name__ == "__main__":
    with Image.open(IMAGE_SRC) as img, Image.open(TEXT_MASK_SRC) as text_mask:
        frame_count = getattr(img, "n_frames", 1)
        duration = img.info.get("duration", 100)
        log.info(f"File loaded: {img.filename} as {img.format} (framecount={frame_count}, duration={duration})")

        hfont = load_font(H_FONT_PATH, FONT_SIZE)
        cfont = load_font(C_FONT_PATH, FONT_SIZE)

        modified_frames: List[Image] = []

        for frame in range(frame_count):
            cursor_y = 0
            img.seek(frame)
            current_frame = img.convert("RGBA")

            current_frame, height = add_nickname(current_frame, "Super Duper Long Nickname", hfont, mask=text_mask)
            cursor_y = add_offset(height + 15)
            current_frame = add_rank(current_frame, 9999, cfont)
            current_frame = draw_progressbar(current_frame, 70)

            modified_frames.append(current_frame)

        modified_frames[0].save("./result.gif", save_all=True, append_images=modified_frames[1:], duration=duration, loop=0, optimize=False)
        modified_frames[0].save("./preview.png", save_all=True)