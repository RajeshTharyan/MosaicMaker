"""Build a uniform image grid by cover-cropping each tile to a shared cell size.

Cell size is the max width and max height among the source images. Each image is
scaled to cover that cell, then centre-cropped so tiles meet with no gaps or
letterboxing. Extra cells stay the background colour.
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Sequence

from PIL import Image, ImageOps

RGB = tuple[int, int, int]
Background = str | RGB


class GridTooSmallError(ValueError):
    """Raised when rows × cols cannot hold every image."""


@dataclass(frozen=True)
class MosaicStats:
    rows: int
    cols: int
    n_images: int
    unused_cells: int
    cell_width: int
    cell_height: int
    canvas_width: int
    canvas_height: int


def validate_grid(rows: int, cols: int, n_images: int) -> int:
    """Return grid capacity, or raise if the layout cannot hold `n_images`."""
    if rows < 1 or cols < 1:
        raise ValueError("rows and cols must be >= 1")
    if n_images < 1:
        raise ValueError("need at least one image")
    capacity = rows * cols
    if capacity < n_images:
        raise GridTooSmallError(
            f"Grid {rows}×{cols} holds {capacity} cells but {n_images} images were provided."
        )
    return capacity


def cell_size(images: Sequence[Image.Image]) -> tuple[int, int]:
    """Shared cell size: max width and max height among `images`."""
    if not images:
        raise ValueError("need at least one image")
    width = max(im.width for im in images)
    height = max(im.height for im in images)
    if width < 1 or height < 1:
        raise ValueError("images must have positive width and height")
    return width, height


def cover_crop(im: Image.Image, cell_w: int, cell_h: int) -> Image.Image:
    """Scale `im` to cover the cell, then centre-crop to `cell_w` × `cell_h`."""
    if cell_w < 1 or cell_h < 1:
        raise ValueError("cell size must be positive")
    if im.width < 1 or im.height < 1:
        raise ValueError("images must have positive width and height")
    fitted = ImageOps.fit(
        im,
        (cell_w, cell_h),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )
    return fitted.convert("RGB")


def mosaic_stats(
    images: Sequence[Image.Image],
    rows: int,
    cols: int,
) -> MosaicStats:
    """Geometry of the mosaic that `compose_mosaic` would produce."""
    capacity = validate_grid(rows, cols, len(images))
    cell_w, cell_h = cell_size(images)
    return MosaicStats(
        rows=rows,
        cols=cols,
        n_images=len(images),
        unused_cells=capacity - len(images),
        cell_width=cell_w,
        cell_height=cell_h,
        canvas_width=cols * cell_w,
        canvas_height=rows * cell_h,
    )


def compose_mosaic(
    images: Sequence[Image.Image],
    rows: int,
    cols: int,
    background: Background = "white",
) -> Image.Image:
    """Paste images left-to-right, top-to-bottom onto a uniform grid canvas."""
    stats = mosaic_stats(images, rows, cols)
    canvas = Image.new(
        "RGB",
        (stats.canvas_width, stats.canvas_height),
        background,
    )
    for idx, im in enumerate(images):
        tile = cover_crop(im, stats.cell_width, stats.cell_height)
        r, c = divmod(idx, cols)
        canvas.paste(tile, (c * stats.cell_width, r * stats.cell_height))
    return canvas


def to_png_bytes(im: Image.Image) -> bytes:
    """Encode `im` as PNG bytes for download or tests."""
    buf = BytesIO()
    im.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()
