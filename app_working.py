from asyncio import run
import streamlit as st


import pickle
import pandas as pd
import streamlit.components.v1 as components

# Load data
try:
    songs_dict = pickle.load(open('songs_dict.pkl', 'rb'))
    df = pd.DataFrame(songs_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except:
    df = pd.read_csv("Hindi_Songs_Dataset.csv")

st.set_page_config(page_title="Song Recommender", layout="wide")

# ✅ CUSTOM CSS FOR AUDIO PLAYER (আপনার পছন্দের ফ্রন্টএন্ড স্টাইল)
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stAudio {
        width: 100%;
    }
    .custom-player-container {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }
    audio {
        width: 100%;
        height: 40px;
        filter: sepia(20%) saturate(70%) grayscale(1) contrast(99%) invert(12%);
    }
    </style>
    """, unsafe_allow_html=True)

st.title('🎵 Song Recommender System')

user_input = st.text_input('Enter your favourite song name')

# ✅ RECOMMEND FUNCTION
def recommend(song):
    song = song.strip().lower()

    try:
        col_name = 'song_name' if 'song_name' in df.columns else 'Song Name'

        matches = df[df[col_name].str.lower().str.contains(song, na=False)]

        if len(matches) == 0:
            return []

        index = matches.index[0]

        distance = similarity[index]
        songs_list = sorted(
            list(enumerate(distance)),
            reverse=True,
            key=lambda x: x[1]
        )[1:6]

        rec = []

        for i, score in songs_list:
            rec.append({
                "song": df.iloc[i][col_name],
                "artist": df.iloc[i]["artist"] if "artist" in df.columns else df.iloc[i]["Artist"],
                "thumbnail": df.iloc[i]["thumbnail"] if "thumbnail" in df.columns else None,
                "audio_url": df.iloc[i]["audio_url"] if "audio_url" in df.columns else None
            })

        return rec
    except Exception as e:
     st.error(f"Error: {e}")
    return []

# --- UI LOGIC: RECOMMENDATION ---
if st.button("Recommend"):
    try:
        col_name = 'song_name' if 'song_name' in df.columns else 'Song Name'
        art_name = 'artist' if 'artist' in df.columns else 'Artist'
        matches = df[df[col_name].str.lower().str.contains(user_input.lower(), na=False)]

        if len(matches) == 0:
            st.error("Song not found!")
            st.stop()

        idx = matches.index[0]

        st.subheader("🔍 You Searched for:")
        c1, c2 = st.columns([1, 3])

        with c1:
            if "thumbnail" in df.columns and pd.notna(df.iloc[idx]["thumbnail"]):
                st.image(df.iloc[idx]["thumbnail"], width=150)

        with c2:
            st.write(f"### {df.iloc[idx][col_name]}")
            st.write(f"**Artist:** {df.iloc[idx][art_name]}")

    except Exception as e:
        st.error(f"Error: {e}")
            
    audio_link = df.iloc[idx]["audio_url"] if "audio_url" in df.columns else None

    if audio_link:
            st.audio(audio_link)
    else:
            st.info("Direct audio link not found. Using Spotify instead.")

            spotify_query = f"{df.iloc[idx][col_name]} {df.iloc[idx][art_name]}".replace(" ", "%20")

            st.link_button(
                "🎵 Open in Spotify",
                f"https://open.spotify.com/search/{spotify_query}"
            )

    st.divider()

    st.subheader("✨ Recommended Songs")
    result = recommend(user_input)

    for item in result:
            with st.container():
                col1, col2 = st.columns([1, 3])

                with col1:
                    if item["thumbnail"]:
                        st.image(item["thumbnail"], width=120)

                with col2:
                    st.write(f"#### {item['song']}")
                    st.write(f"Artist: {item['artist']}")

                    if item["audio_url"]:
                        st.audio(item["audio_url"])
                    else:
                        query = f"{item['song']} {item['artist']}".replace(" ", "+")

                        st.link_button(
                            "🎵 Open in Spotify",
                            f"https://open.spotify.com/search/{query}"
                        )

# ==========================================
# ✅ ALL SONGS LIBRARY WITH CUSTOM PLAYER
# ==========================================
st.write("##")
st.divider()
st.subheader("📁 All Songs Library")

for index, row in df.iterrows():
    s_name = row['song_name'] if 'song_name' in df.columns else row['Song Name']
    a_name = row['artist'] if 'artist' in df.columns else row['Artist']
    thumb = row['thumbnail'] if 'thumbnail' in df.columns else None
    audio_file = row['audio_url'] if 'audio_url' in row else None

    # HTML/CSS কাস্টম কন্টেইনার
    st.markdown(f"""
        <div class="custom-player-container">
            <div style="display: flex; align-items: center;">
                <img src="{thumb if pd.notna(thumb) else 'https://cdn-icons-png.flaticon.com/512/3844/3844724.png'}" width="80" style="border-radius: 10px; margin-right: 20px;">
                <div>
                    <h4 style="margin: 0;">{s_name}</h4>
                    <p style="margin: 0; color: #aaa;">{a_name}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # অডিও প্লেয়ার সেকশন
    if pd.notna(audio_file):
        st.audio(audio_file)
    else:
        # Spotify button
        q = f"{s_name} {a_name}".replace(" ", "%20")

        st.link_button(
            "🎵 Open in Spotify",
            f"https://open.spotify.com/search/{q}"
        )