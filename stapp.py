import os
import glob
import streamlit as st

from image_recieve_tets import classify_image, upload_to_wasabi, download_from_wasabi, retrieve_metadata

image_file_types = ('*.jpg', '*png', '*.jpeg')


def get_media_list():
    files = []
    for t in image_file_types:
        files.extend(glob.glob(f"image_store/{t}"))
    return files


st.title("Photo Label Sorter app")

uploaded_files = st.file_uploader(
    "Upload Photos", accept_multiple_files=True, type=['png', 'jpg']
)

for uploaded_file in uploaded_files:
    # file_details = {"FileName":uploaded_file.name,"FileType":uploaded_file.type}
    fname = uploaded_file.name
    with open(fname,"wb") as f: 
      f.write(uploaded_file.getbuffer())         
    st.success("Saved File")
    st.image(fname, caption=fname)

    st.write("Classifying.............")
    predicted_class = classify_image(fname)
    st.write(f"Image classified as: {predicted_class}")

    wasabi_url = upload_to_wasabi(fname, fname, predicted_class)


    files = []
    for t in image_file_types:
        files.extend(glob.glob(t))
    for i in files:
      os.remove(i)

    if wasabi_url:
        st.success(f"Image uploaded to: {wasabi_url}")
        # retrieve_metadata(fname)

query = st.text_input("Enter query (query feature not added yet)", "")

file_names = ["car.jpg", "file_7.jpg"]




st.button("Reset images", type="primary")
if st.button("See images"):
    st.write("Why hello there")

    for fname in file_names:
        download_path = 'image_store/' + fname
        download_from_wasabi(fname, download_path)
        st.success(f"image downloaded to {download_path}")

    media = get_media_list()
    for fname in media:
        st.image(fname, caption=fname)

else:
    for i in file_names:
        try:
              os.remove(i)
        except FileNotFoundError:
            pass

