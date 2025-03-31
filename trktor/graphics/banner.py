import logging
import os
from logging import Logger
from typing import Dict, Union, List, Optional, Self

from PIL import ImageFont, Image, ImageDraw
from PIL.ImageFile import ImageFile

from trktor.graphics import TRANSPARENT_WHITE, TRANSPARENT_BLACK, Point2D, RGBAColor, MarginSet, ORIGIN, NO_MARGINS, \
    Dim2D
from trktor.graphics.utils import fontname


class Banner:
    _image: ImageFile
    _rtl_mode: bool = False
    _frames: List[Image] = []
    _queue: List[Image] = []
    _duration: int = 1
    _cursor: Point2D = ORIGIN
    _fonts: Dict[str, ImageFont] = {}
    _log: Logger = logging.getLogger(__name__)

    def __init__(self, base_image: Union[os.PathLike, str]):
        self._image = Image.open(base_image)
        self._duration = self._image.info.get("duration", 100)
        frame_count = getattr(self._image, "n_frames", 1)
        self._log.info(f"File {base_image} loaded as {self._image.format} (framecount={frame_count}, duration={self._duration})")

        if frame_count > 1:
            for frame in range(frame_count):
                self._image.seek(frame)
                self._frames.append(self._image.convert("RGBA"))
        self._log.info(f"Extracted {len(self._frames)} frames to memory")

    def _load_font(self, alias: str) -> ImageFont:
        return self._fonts[alias] if alias in self._fonts else ImageFont.load_default()

    def _get_anchor(self, margins: MarginSet) -> Point2D:
        return Point2D(x=self._cursor.x + margins.left, y=self._cursor.y + margins.top) if not self._rtl_mode \
            else Point2D(x=self._image.size[0] - margins.right, y=self._cursor.y + margins.top)

    def switch_ltr(self, mode: bool) -> Self:
        self._rtl_mode = mode
        return self

    def move_cursor(self, x: int = 0, y: int = 0) -> Self:
        self._cursor.x += x
        self._cursor.y += y
        return self

    def register_font(self, alias: str, path: Union[os.PathLike, str], size: int) -> Self:
        fnt: ImageFont

        if alias in self._fonts.keys():
            self._log.warning(f"Name {alias} already taken by {fontname(self._fonts[alias])}, overwriting")

        if not os.path.exists(path):
            self._log.error(f"Failed to find file {path} for {alias}")
            raise FileNotFoundError
        else:
            try:
                fnt = ImageFont.truetype(path, size)
            except OSError as e:
                self._log.error(f"Error opening {path} for {alias}: {e}")
                raise FileNotFoundError from e

            self._fonts[alias] = fnt
            self._log.info(f"Registered font {fontname(self._fonts[alias])} from {path} as {alias}")

        return self

    def text(self, text: str, font: str, *, margins: MarginSet = NO_MARGINS,  mask: Optional[Image] = None, colors: Optional[List[RGBAColor]] = None) -> Self:
        master = Image.new("RGBA", self._image.size, TRANSPARENT_WHITE)
        anchor = self._get_anchor(margins)

        fnt = self._load_font(font)
        primary = colors[0] if colors else "black"
        accent = colors[1] if colors and len(colors) > 1 else primary

        main = Image.new("RGBA", self._image.size, TRANSPARENT_WHITE)
        main_draw = ImageDraw.Draw(main)
        main_draw.text(ORIGIN, text, font = fnt, fill = colors[0])

        if not self._rtl_mode:
            _, _, right, _ = main.getbbox(alpha_only=True)
            anchor.x -= right

        master.alpha_composite(main, anchor)

        if mask is not None:
            mask_shape = mask.getbbox(alpha_only=True)
            overlay = Image.new("RGBA", self._image.size, TRANSPARENT_BLACK)
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.text(anchor, text, font = fnt, fill = accent)
            overlay.crop(mask_shape)
            master.alpha_composite(overlay)

        _, _, right, lower = master.getbbox(alpha_only=True)
        self._cursor = (right + margins.right, lower + margins.bottom)
        self._queue.append(master)
        return self

    def progress_bar(self, percentage: int, dimensions: Dim2D, *, margins: Optional[MarginSet], colors: Optional[List[RGBAColor]] = None) -> Self:
        master = Image.new("RGBA", self._image.size, TRANSPARENT_WHITE)
        anchor = self._get_anchor(margins)

        primary = colors[0] if colors else "black"
        accent = colors[1] if colors and len(colors) > 1 else primary

