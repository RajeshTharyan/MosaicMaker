"""Browser UI for MosaicMaker. Core composition lives in `mosaic.grid`.

    streamlit run streamlit_mosaic.py
"""

from __future__ import annotations

from PIL import Image, UnidentifiedImageError
import streamlit as st

from mosaic.grid import GridTooSmallError, compose_mosaic, mosaic_stats, to_png_bytes

st.set_page_config(page_title="Mosaic", layout="centered")
st.title("🖼️ Mosaic")
st.markdown("By: **Prof. Rajesh Tharyan**")

if "mosaic_png" not in st.session_state:
    st.session_state.mosaic_png = None
if "mosaic_key" not in st.session_state:
    st.session_state.mosaic_key = None

files = st.file_uploader(
    "Upload images (PNG, JPG, TIFF …)",
    type=["png", "jpg", "jpeg", "bmp", "tif", "tiff"],
    accept_multiple_files=True,
)


def _source_key(uploads, rows: int, cols: int):
    return (tuple((f.name, f.size) for f in uploads), rows, cols)


def _load_rgb(uploads) -> list[Image.Image]:
    images = []
    for upload in uploads:
        upload.seek(0)
        try:
            images.append(Image.open(upload).convert("RGB"))
        except (UnidentifiedImageError, OSError, ValueError):
            st.error(f"Could not read {upload.name} as an image.")
            st.stop()
    return images


if not files:
    st.session_state.mosaic_png = None
    st.session_state.mosaic_key = None
    st.info("Upload at least one image to begin.")
else:
    st.subheader("Preview")
    st.image(files, width=110, caption=[f.name for f in files])

    cols1, cols2 = st.columns(2)
    rows = int(cols1.number_input("Rows", 1, 20, 2, 1))
    cols = int(cols2.number_input("Columns", 1, 20, 4, 1))

    current_key = _source_key(files, rows, cols)
    if st.session_state.mosaic_key != current_key:
        st.session_state.mosaic_png = None
        st.session_state.mosaic_key = None

    if rows * cols < len(files):
        st.error(
            f"Grid {rows}×{cols} holds {rows * cols} cells but "
            f"{len(files)} images were uploaded."
        )
    else:
        if st.button("Create Mosaic", type="primary"):
            images = _load_rgb(files)
            try:
                canvas = compose_mosaic(images, rows, cols)
            except GridTooSmallError as exc:
                st.error(str(exc))
            else:
                stats = mosaic_stats(images, rows, cols)
                st.session_state.mosaic_png = to_png_bytes(canvas)
                st.session_state.mosaic_key = current_key
                st.session_state.mosaic_stats = stats

        if st.session_state.mosaic_png:
            st.success("Mosaic created")
            stats = st.session_state.get("mosaic_stats")
            if stats is not None:
                st.caption(
                    f"{stats.canvas_width}×{stats.canvas_height} px · "
                    f"cell {stats.cell_width}×{stats.cell_height} · "
                    f"{stats.n_images} image(s)"
                    + (
                        f" · {stats.unused_cells} empty cell(s)"
                        if stats.unused_cells
                        else ""
                    )
                )
            st.image(st.session_state.mosaic_png, use_container_width=True)
            st.download_button(
                label="Download PNG",
                data=st.session_state.mosaic_png,
                file_name="mosaic.png",
                mime="image/png",
            )
