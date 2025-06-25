# streamlit_mosaic.py
# -------------------------------------------------
# Combine any set of uploaded images into a grid.
# • User uploads files (drag-and-drop or file picker)
# • Specifies rows × columns
# • Click “Create Mosaic” → preview + download button
#
# Run with:
#   streamlit run streamlit_mosaic.py
# -------------------------------------------------

import streamlit as st
from PIL import Image
from io import BytesIO
import math

st.set_page_config(page_title="Image-Grid Combiner",
                   layout="centered")

st.title("🖼️ Image-Grid Combiner")

# --------------- upload images -------------------
files = st.file_uploader(
    "Upload image files (PNG, JPG, TIFF, …)",
    type=["png", "jpg", "jpeg", "bmp", "tif", "tiff"],
    accept_multiple_files=True
)

if files:
    # quick gallery thumbnail
    st.subheader("Preview of uploaded files")
    st.image([f for f in files], width=120, caption=[f.name for f in files])

    # ---------- grid parameters ------------------
    st.subheader("Grid settings")
    cols1, cols2 = st.columns(2)
    rows = cols1.number_input("Rows", min_value=1, value=2, step=1)
    cols = cols2.number_input("Columns", min_value=1, value=4, step=1)

    main_col = st.columns(1)[0]
    if rows * cols < len(files):
        main_col.error(f"Grid {rows}×{cols} holds {rows*cols} cells but "
                       f"{len(files)} images were uploaded.")
    else:
        if main_col.button("Create Mosaic", type="primary"):
            # ----------- build mosaic ---------------
            images = [Image.open(f).convert("RGB") for f in files]

            cell_w = max(im.width  for im in images)
            cell_h = max(im.height for im in images)

            canvas = Image.new("RGB", (cols * cell_w, rows * cell_h), "white")

            for idx, im in enumerate(images):
                r, c = divmod(idx, cols)
                x = c * cell_w + (cell_w - im.width)  // 2
                y = r * cell_h + (cell_h - im.height) // 2
                canvas.paste(im, (x, y))

            # show result
            st.success("Mosaic created👇")
            st.image(canvas, use_column_width=True)

            # prepare download
            buf = BytesIO()
            # use extension of first file
            ext = files[0].name.split(".")[-1].lower()
            save_format = "PNG" if ext == "png" else "JPEG"
            canvas.save(buf, format=save_format)
            buf.seek(0)

            st.download_button(
                label="Download combined image",
                data=buf,
                file_name=f"mosaic.{ext}",
                mime=f"image/{ext}"
            )
else:
    st.info("Upload at least one image to begin.")
