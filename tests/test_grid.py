"""Unit tests for mosaic composition. No Streamlit, no network."""

from io import BytesIO

import pytest
from PIL import Image, ImageDraw

from mosaic.grid import (
    GridTooSmallError,
    cell_size,
    compose_mosaic,
    cover_crop,
    mosaic_stats,
    to_png_bytes,
    validate_grid,
)

RED = (220, 20, 20)
GREEN = (20, 180, 40)
BLUE = (30, 80, 220)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def solid(color, size=(10, 10)) -> Image.Image:
    return Image.new("RGB", size, color)


def pixel(im: Image.Image, x: int, y: int):
    return im.getpixel((x, y))


def test_validate_grid_returns_capacity():
    assert validate_grid(2, 4, 5) == 8


def test_validate_grid_rejects_too_many_images():
    with pytest.raises(GridTooSmallError, match="holds 4 cells"):
        validate_grid(2, 2, 5)


def test_validate_grid_rejects_non_positive_shape():
    with pytest.raises(ValueError, match=">= 1"):
        validate_grid(0, 3, 1)
    with pytest.raises(ValueError, match=">= 1"):
        validate_grid(2, 0, 1)


def test_validate_grid_rejects_empty_image_list():
    with pytest.raises(ValueError, match="at least one"):
        validate_grid(2, 2, 0)


def test_cell_size_is_max_width_and_max_height():
    images = [solid(RED, (10, 40)), solid(GREEN, (30, 12))]
    assert cell_size(images) == (30, 40)


def test_cell_size_rejects_empty():
    with pytest.raises(ValueError, match="at least one"):
        cell_size([])


def test_cover_crop_output_matches_cell():
    im = solid(BLUE, (8, 20))
    cropped = cover_crop(im, 16, 10)
    assert cropped.size == (16, 10)
    assert cropped.mode == "RGB"


def test_cover_crop_fills_cell_without_letterbox():
    """A solid source should fill every pixel of the cell (no white bars)."""
    cropped = cover_crop(solid(RED, (4, 12)), 10, 10)
    extrema = cropped.getextrema()
    assert extrema == ((RED[0], RED[0]), (RED[1], RED[1]), (RED[2], RED[2]))


def test_cover_crop_rejects_non_positive_cell():
    with pytest.raises(ValueError, match="positive"):
        cover_crop(solid(RED), 0, 10)


def test_compose_mosaic_canvas_and_layout():
    images = [solid(RED, (10, 10)), solid(GREEN, (10, 10)), solid(BLUE, (10, 10))]
    canvas = compose_mosaic(images, rows=2, cols=2)
    assert canvas.size == (20, 20)
    assert pixel(canvas, 5, 5) == RED
    assert pixel(canvas, 15, 5) == GREEN
    assert pixel(canvas, 5, 15) == BLUE
    assert pixel(canvas, 15, 15) == WHITE


def test_compose_mosaic_uses_independent_max_dims():
    images = [solid(RED, (10, 20)), solid(GREEN, (30, 10))]
    canvas = compose_mosaic(images, rows=1, cols=2)
    assert canvas.size == (60, 20)
    stats = mosaic_stats(images, 1, 2)
    assert stats.cell_width == 30
    assert stats.cell_height == 20
    assert stats.unused_cells == 0


def test_mosaic_stats_counts_unused_cells():
    stats = mosaic_stats([solid(RED, (5, 5))], rows=2, cols=3)
    assert stats.n_images == 1
    assert stats.unused_cells == 5
    assert stats.canvas_width == 15
    assert stats.canvas_height == 10


def test_compose_mosaic_row_major_order():
    colors = [RED, GREEN, BLUE, BLACK]
    images = [solid(c, (4, 4)) for c in colors]
    canvas = compose_mosaic(images, rows=2, cols=2)
    assert pixel(canvas, 1, 1) == RED
    assert pixel(canvas, 5, 1) == GREEN
    assert pixel(canvas, 1, 5) == BLUE
    assert pixel(canvas, 5, 5) == BLACK


def test_compose_mosaic_raises_when_grid_too_small():
    with pytest.raises(GridTooSmallError):
        compose_mosaic([solid(RED), solid(GREEN), solid(BLUE)], rows=1, cols=2)


def test_to_png_bytes_round_trips():
    im = solid(BLUE, (12, 8))
    data = to_png_bytes(im)
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    loaded = Image.open(BytesIO(data))
    assert loaded.size == (12, 8)
    assert loaded.convert("RGB").getpixel((0, 0)) == BLUE


def test_cover_crop_keeps_centre_of_marked_image():
    """A centred mark should survive cover-crop; corners may be discarded."""
    im = Image.new("RGB", (20, 10), WHITE)
    draw = ImageDraw.Draw(im)
    draw.rectangle((9, 4, 10, 5), fill=BLACK)
    cropped = cover_crop(im, 10, 10)
    assert cropped.size == (10, 10)
    assert BLACK in {cropped.getpixel((x, y)) for x in range(10) for y in range(10)}
