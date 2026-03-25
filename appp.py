import streamlit as st
import instaloader
import os
import zipfile
from urllib.parse import urlparse

st.set_page_config(page_title="Instagram Downloader", layout="centered")

st.title("📸 Instagram Profile Downloader")


# ----------------------------
# SAFE USERNAME EXTRACTION
# ----------------------------
def extract_username(url):
    try:
        parsed = urlparse(url)

        # remove query params like ?igsh=xxxx
        path = parsed.path.strip("/")

        if not path:
            return None

        username = path.split("/")[0]

        # extra cleanup safety
        username = username.split("?")[0].split("#")[0]

        return username

    except:
        return None


# ----------------------------
# SIDEBAR LOGIN
# ----------------------------
st.sidebar.header("🔐 Login (recommended)")
ig_user = st.sidebar.text_input("Instagram username")
ig_pass = st.sidebar.text_input("Instagram password", type="password")


# ----------------------------
# INPUT
# ----------------------------
profile_url = st.text_input("Enter Instagram Profile URL")

limit = st.slider("Max posts to download", 1, 50, 10)


# ----------------------------
# MAIN ACTION
# ----------------------------
if st.button("Download"):

    username = extract_username(profile_url)

    if not username:
        st.error("❌ Invalid Instagram URL")
        st.stop()

    st.info(f"Target user: @{username}")

    L = instaloader.Instaloader(
        download_pictures=True,
        download_videos=True,
        download_video_thumbnails=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False
    )

    # ----------------------------
    # LOGIN (IMPORTANT)
    # ----------------------------
    if ig_user and ig_pass:
        try:
            L.login(ig_user, ig_pass)
            st.success("✅ Logged in successfully")
        except Exception as e:
            st.error(f"❌ Login failed: {e}")
            st.stop()
    else:
        st.warning("⚠️ No login provided — may fail for some profiles")


    # ----------------------------
    # GET PROFILE
    # ----------------------------
    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except Exception as e:
        st.error(f"❌ Profile not found or blocked: {e}")
        st.stop()


    # ----------------------------
    # DOWNLOAD POSTS
    # ----------------------------
    folder = f"temp_{username}"
    os.makedirs(folder, exist_ok=True)

    count = 0
    progress = st.progress(0)
    status = st.empty()

    try:
        for post in profile.get_posts():
            L.download_post(post, target=folder)

            count += 1
            status.text(f"Downloaded {count} posts...")
            progress.progress(min(count / limit, 1.0))

            if count >= limit:
                break

    except Exception as e:
        st.error(f"❌ Download error: {e}")
        st.stop()


    # ----------------------------
    # ZIP FILE
    # ----------------------------
    zip_path = f"{folder}.zip"

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for root, _, files in os.walk(folder):
            for file in files:
                full_path = os.path.join(root, file)
                zipf.write(full_path, arcname=file)


    # ----------------------------
    # DOWNLOAD BUTTON
    # ----------------------------
    with open(zip_path, "rb") as f:
        st.download_button(
            "⬇ Download ZIP",
            f,
            file_name=f"{username}.zip"
        )

    st.success(f"🎉 Done! {count} posts downloaded")
