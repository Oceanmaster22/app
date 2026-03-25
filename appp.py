import streamlit as st
import instaloader
import os
import zipfile
from urllib.parse import urlparse

st.title("📸 Instagram Downloader")

def extract_username(url):
    try:
        path = urlparse(url).path
        return path.strip("/").split("/")[0]
    except:
        return None


profile_url = st.text_input("Profile URL")

if st.button("Download"):

    username = extract_username(profile_url)

    if not username:
        st.error("❌ Invalid URL")
        st.stop()

    L = instaloader.Instaloader()

    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except Exception as e:
        st.error(f"❌ Failed to load profile: {e}")
        st.stop()

    folder = f"temp_{username}"
    os.makedirs(folder, exist_ok=True)

    count = 0

    try:
        for post in profile.get_posts():
            L.download_post(post, target=folder)
            count += 1

            if count >= 20:   # safety limit for Streamlit Cloud
                break

    except Exception as e:
        st.error(f"Download error: {e}")
        st.stop()

    zip_path = f"{folder}.zip"

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for root, _, files in os.walk(folder):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)

    with open(zip_path, "rb") as f:
        st.download_button("⬇ Download ZIP", f, file_name=f"{username}.zip")

    st.success(f"Downloaded {count} posts")
