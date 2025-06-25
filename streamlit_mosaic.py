# streamlit_mosaic_fullbleed.py
#
#   streamlit run streamlit_mosaic_fullbleed.py
#
# – Upload any mix of PNG/JPG/TIF…
# – Pick rows × columns
# – Click “Create Mosaic”
# – Preview fills browser width; “Download PNG” for the combined file
# -------------------------------------------------------------------------

import streamlit as st
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Mosaic", layout="centered")
st.title("🖼️ Image-Grid Combiner (full-bleed)")
st.markdown("By: **Prof. Rajesh Tharyan**")

# 1. Upload images
files = st.file_uploader(
    "Upload images (PNG, JPG, TIFF …)",
    type=["png", "jpg", "jpeg", "bmp", "tif", "tiff"],
    accept_multiple_files=True
)

if files:
    st.subheader("Preview")
    st.image(files, width=110, caption=[f.name for f in files])

    # 2. Grid layout
    cols1, cols2 = st.columns(2)
    rows = cols1.number_input("Rows", 1, 20, 2, 1)
    cols = cols2.number_input("Columns", 1, 20, 4, 1)

    if rows * cols < len(files):
        st.error(f"Grid {rows}×{cols} holds {rows*cols} cells but "
                 f"{len(files)} images were uploaded.")
    else:
        if st.button("Create Mosaic", type="primary"):
            # --- build mosaic -------------------------------------------
            imgs = [Image.open(f).convert("RGB") for f in files]

            # pick max dims to define a cell
            cell_w = max(im.width  for im in imgs)
            cell_h = max(im.height for im in imgs)

            # resize & centre-crop each to fill cell (no margin)
            processed = []
            for im in imgs:
                scale = max(cell_w / im.width, cell_h / im.height)
                w, h = int(im.width * scale), int(im.height * scale)
                im = im.resize((w, h), Image.LANCZOS)
                # centre crop to exact cell_w × cell_h
                left   = (w - cell_w) // 2
                upper  = (h - cell_h) // 2
                im = im.crop((left, upper, left + cell_w, upper + cell_h))
                processed.append(im)

            # blank canvas
            canvas = Image.new("RGB", (cols*cell_w, rows*cell_h), "white")

            for idx, im in enumerate(processed):
                r, c = divmod(idx, cols)
                canvas.paste(im, (c*cell_w, r*cell_h))

            st.success("Mosaic created")
            st.image(canvas, use_container_width=True)

            # download
            buf = BytesIO()
            canvas.save(buf, format="PNG")
            st.download_button(
                label="Download PNG",
                data=buf.getvalue(),
                file_name="mosaic.png",
                mime="image/png"
            )
else:
    st.info("Upload at least one image to begin.")
