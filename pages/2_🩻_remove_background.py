import streamlit as st
from io import BytesIO
from PIL import Image
from rembg import remove, new_session

st.set_page_config(
    page_title="Remove Background",
    page_icon="🩻",
)

st.title("Remove background from your image")
st.write(
    ":dog: Try uploading an image to watch the background magically removed. Full quality images can be downloaded from the sidebar. This code is open source and available [here](<https://github.com/tyler-simons/BackgroundRemoval>) on GitHub. Special thanks to the [rembg library](<https://github.com/danielgatis/rembg>) :grin:"
)
st.sidebar.write("## Upload and download :gear:")

# Create the columns
col1, col2 = st.columns(2)


# Download the fixed image
def convert_image(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im


# Package the transform into a function
def fix_image(upload):
    image = Image.open(upload)
    col1.write("Original Image :camera:")
    col1.image(image)

    rembg_session = new_session(model_name="u2net_human_seg")
    fixed = remove(image, session=rembg_session)
    col2.write("Fixed Image :wrench:")
    col2.image(fixed)
    st.sidebar.markdown("\n")
    st.sidebar.download_button(
        "Download fixed image", convert_image(fixed), "fixed.png", "image/png"
    )


# Create the file uploader
my_upload = st.sidebar.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

# Fix the image!
if my_upload is not None:
    fix_image(upload=my_upload)
