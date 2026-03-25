import streamlit as st
from downloader import download_instagram_images
import os

st.set_page_config(page_title="Instagram Downloader", layout="centered")

st.title("📸 Instagram Profile Downloader")

profile_url = st.text_input("Instagram Profile URL")
download_path = st.text_input("Download Folder", "./downloads")

st.sidebar.header("🔐 Login (optional)")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.button("Download"):
    if not profile_url:
        st.error("Please enter a profile URL")
    else:
        os.makedirs(download_path, exist_ok=True)

        progress = st.progress(0)
        status = st.empty()

        def update_progress(count):
            status.text(f"Downloaded {count} posts...")
            progress.progress(min(count / 50, 1.0))  # rough scaling

        try:
            count, user = download_instagram_images(
                profile_url,
                download_path,
                username if username else None,
                password if password else None,
                progress_callback=update_progress
            )

            st.success(f"Done! Downloaded {count} posts from @{user}")

        except Exception as e:
            st.error(f"Error: {e}")
