import streamlit as st
import pandas as pd
import pickle

# Load data
try:
    songs_dict = pickle.load(open('songs_dict.pkl', 'rb'))
    df = pd.DataFrame(songs_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except:
    df = pd.read_csv("Hindi_Songs_Dataset.csv")

# Simple, robust recommend function with fallback
def recommend(query, topn=10):
    """
    Return a list of recommendation dicts: {"song":..., "artist":..., "thumbnail":...}
    Uses precomputed 'similarity' if available; otherwise does a substring search on the dataframe.
    """
    q = (query or "").strip()
    if not q:
        return []

    recs = []

# Try using precomputed similarity matrix if present
    try:
        if 'similarity' in globals() and similarity is not None:
            # If similarity is a list-of-lists or numpy array-like
            # Determine song name column
            name_col = 'song_name' if 'song_name' in df.columns else 'Song Name' if 'Song Name' in df.columns else df.columns[0]
            # Find an index whose name contains the query (best-effort)
            lower_names = df[name_col].astype(str).str.lower().tolist()
            idx = None
            qlower = q.lower()

            # Exact match first
            for i, s in enumerate(lower_names):
                if s == qlower:
                    idx = i
                    break

            # If no exact match, try substring match
            if idx is None:
                for i, s in enumerate(lower_names):
                    if qlower in s:
                        idx = i
                        break

            # fallback to first item if nothing matched
            if idx is None and len(lower_names) > 0:
                idx = 0

            # If we have a valid index, compute similarity-based recommendations
            if idx is not None:
                sim_scores = list(enumerate(similarity[idx]))
                sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

                for i, score in sim_scores[:topn]:
                    row = df.iloc[i].to_dict()
                    recs.append({
                        "song": row.get('song_name') or row.get('Song Name') or row.get(df.columns[0]),
                        "artist": row.get('artist') or row.get('Artist') or "",
                        "thumbnail": row.get('thumbnail') if 'thumbnail' in row else None
                    })
                return recs
    except Exception:
        # any problem using similarity -> fall back to dataframe search
        pass

    # Fallback: substring search over song and artist columns
    try:
        name_col = 'song_name' if 'song_name' in df.columns else 'Song Name' if 'Song Name' in df.columns else df.columns[0]
        artist_col = 'artist' if 'artist' in df.columns else 'Artist' if 'Artist' in df.columns else (df.columns[1] if len(df.columns) > 1 else None)

        # EXACT MATCH FIRST
        exact = df[
            df[name_col].astype(str).str.lower() == q.lower()
        ]

        if len(exact) > 0:
            filtered = exact.head(topn)
        else:
            mask_name = df[name_col].astype(str).str.contains(
                q,
                case=False,
                na=False
            )

            if artist_col is not None:
                mask_artist = df[artist_col].astype(str).str.contains(
                    q,
                    case=False,
                    na=False
                )
                filtered = df[mask_name | mask_artist].head(topn)
            else:
                filtered = df[mask_name].head(topn)

        # Build recommendations from filtered results
        recs = []
        for _, row in filtered.iterrows():
            recs.append({
                "song": row.get('song_name') or row.get('Song Name') or row.get(df.columns[0]),
                "artist": row.get('artist') or row.get('Artist') or "",
                "thumbnail": row.get('thumbnail') if 'thumbnail' in row else None
            })

        # If we don't have enough results, append top rows until we reach topn (avoid exact duplicates)
        if len(recs) < topn:
            existing = {r['song'] for r in recs}
            for _, row in df.head(topn).iterrows():
                if len(recs) >= topn:
                    break
                candidate = {
                    "song": row.get('song_name') or row.get('Song Name') or row.get(df.columns[0]),
                    "artist": row.get('artist') or row.get('Artist') or "",
                    "thumbnail": row.get('thumbnail') if 'thumbnail' in row else None
                }
                if candidate['song'] not in existing:
                    recs.append(candidate)
                    existing.add(candidate['song'])

        # If still empty, return top rows as fallback
        if not recs:
            for _, row in df.head(topn).iterrows():
                recs.append({
                    "song": row.get('song_name') or row.get('Song Name') or row.get(df.columns[0]),
                    "artist": row.get('artist') or row.get('Artist') or "",
                    "thumbnail": row.get('thumbnail') if 'thumbnail' in row else None
                })
    except Exception:
        # final safety: return empty list
        return []

    return recs

# Image URLs
CENTER_BG_IMG = "https://direct-coffee-kpibh2wx.edgeone.app/wp6195787.jpg"
LEFT_PANEL_IMG = "https://testy-magenta-8wp0z4vq.edgeone.app/1889897.png"
BOTTOM_TUX_IMG = "https://shrill-red-lkwogsx4.edgeone.app/3243808.jpg"

# Page config
st.set_page_config(page_title="Song Recommender", layout="wide")

# ==========================
# CUSTOM CSS
# ==========================
st.markdown("""
<style>
.stApp {
    background: #07111f;
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

.hero-title {
    white-space: nowrap;
    line-height: 1.1;
    font-size: 75px;  /* boro kore dilo */
    font-weight: 900;
    text-align: center;
    background: linear-gradient(90deg, #00ff88, #00eaff, #7d7dff, #ff4df8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 15px cyan, 0 0 30px cyan, 0 0 60px cyan;
}

.terminal-box {
    background: rgba(0,0,0,.75);
    padding: 20px;
    border-radius: 20px;
    border: 2px solid #00ff88;
    box-shadow: 0 0 25px #00ff88;
}

.monitor-box {
    background: rgba(0,0,0,.75);
    padding: 20px;
    border-radius: 20px;
    border: 2px solid cyan;
    box-shadow: 0 0 25px cyan;
}

.stTextInput input {
    background: rgba(0,0,0,.85);
    border: 2px solid cyan;
    color: white;
    border-radius: 18px;

    height: 65px !important;
    font-size: 22px;

    padding-top: 0px !important;
    padding-bottom: 0px !important;
    padding-left: 20px !important;

    box-shadow: 0 0 10px cyan,
                0 0 25px rgba(0,255,255,.4);

    width:100%;
}
            /* Remove Streamlit anchor/link icon */
[data-testid="stHeaderActionElements"] {
    display: none !important;
}

a[aria-label="Anchor link"] {
    display: none !important;
}

.stButton button {
    background: linear-gradient(90deg, #00eaff, #7d7dff);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 14px 30px;
    font-size: 18px;
    font-weight: bold;
    box-shadow: 0 0 10px cyan, 0 0 30px rgba(0,255,255,.5);
}

.custom-player-container {
    background: rgba(0,0,0,.75);
    border: 2px solid cyan;
    border-radius: 18px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 0 20px cyan;
}
</style>
""", unsafe_allow_html=True)

# ==========================
st.markdown(r"""

<style>
.search-box{
    background:rgba(0,10,30,.85);
    border:1px solid #00d9ff;
    border-radius:20px;
    padding:20px;
    box-shadow:0 0 20px #00d9ff55;
    margin-bottom:20px;
}
/* UNIX STYLE HERO UI */

/* ========================== */



.result-card{
    background:rgba(0,10,30,.85);
    border:1px solid #9c4dff;
    border-radius:18px;
    padding:20px;
    margin-top:20px;
    box-shadow:0 0 20px rgba(156,77,255,.4);
}

.song-row{
    background:rgba(0,10,30,.85);
    border-bottom:1px solid rgba(0,255,255,.15);
    padding:12px;
    border-radius:10px;
    margin-bottom:8px;
}

.section-title{
    color:#00d9ff;
    font-size:32px;
    font-weight:800;
    margin-top:25px;
}
</style>

""", unsafe_allow_html=True)

# HEADER
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""

<div style='text-align:center;'>

<h1 style='
font-size:72px;
color:#7df9ff;
text-shadow:0 0 20px cyan,0 0 40px cyan;
margin-bottom:0px;'>
🎵 SONG RECOMMENDER SYSTEM
</h1>

<p style='
font-size:28px;
color:white;
margin-top:5px;'>
Discover. Play. Feel The Music.
</p>

</div>
""", unsafe_allow_html=True)

# TERMINAL + SYSTEM

left,right = st.columns([1,1])

with left:
    st.markdown(""" <div class='search-box'> <pre style='color:#00ff88'>
user@unix-system:~$ ls la

total 1024

dataset loaded...
model active...
spotify connected...
AI engine ready... </pre> </div>
""", unsafe_allow_html=True)

with right:
    st.markdown(""" <div class='search-box'> <pre style='color:#00ffcc'>
CPU  [|||||||||||] 42%
RAM  [|||||||||| ] 68%
SWAP [|||        ] 10%

Spotify Running
Recommendation Engine Online </pre> </div>
""", unsafe_allow_html=True)

# SEARCH AREA

search_left, search_right = st.columns([5,1])

with search_left:
    user_input = st.text_input(
        "",
        placeholder="🔍 Search for a song...",
        key="unix_search"
    )

with search_right:
    st.write("")
    search_btn = st.button(
        "🔍 SEARCH",
        use_container_width=True
    )

# RESULT
if search_btn and user_input:

    user_input = user_input.strip()

    rec_songs = recommend(user_input)

    if len(rec_songs) > 0:

        st.markdown(
            "<div class='section-title'>🔎 SEARCH RESULT</div>",
            unsafe_allow_html=True
        )

        for song in rec_songs[:5]:
         c1, c2 = st.columns([1,3])

        with c1:
            if song.get("thumbnail"):
                st.image(song["thumbnail"], width=130)

        with c2:
            st.markdown(f"### {song['song']}")
            st.write(f"🎤 {song.get('artist','')}")

            spotify_query = f"{song['song']} {song.get('artist','')}".replace(" ", "+")

            b1, b2 = st.columns(2)

            with b1:
                st.link_button(
                    "🟢 PLAY ON SPOTIFY",
                    f"https://open.spotify.com/search/{spotify_query}",
                    use_container_width=True
                )

            with b2:
                st.link_button(
                    "▶ YOUTUBE PLAY",
                    f"https://www.youtube.com/results?search_query={spotify_query}",
                    use_container_width=True
                )

                st.divider()

    else:
        st.error("No recommendations found.")
# LIBRARY
st.markdown("<br><br>", unsafe_allow_html=True)
# RECOMMENDED FOR YOU
if search_btn and user_input and len(rec_songs) > 0:

    st.markdown(
        "<div class='section-title'>⭐ RECOMMENDED FOR YOU</div>",
        unsafe_allow_html=True
    )

    for song in rec_songs[:5]:

        c1, c2 = st.columns([1,3])

        with c1:
            if song.get("thumbnail"):
                st.image(song["thumbnail"], width=100)

        with c2:
            st.markdown(f"**{song['song']}**")
            st.caption(song.get("artist",""))

        st.divider()

st.markdown(
"<div class='section-title'>🎵 ALL SONGS LIBRARY</div>",
unsafe_allow_html=True
)

for index,row in df.head(20).iterrows():

    song_name = (
    row['song_name']
    if 'song_name' in df.columns
    else row['Song Name']
    )

    artist_name = (
    row['artist']
    if 'artist' in df.columns
    else row['Artist']
    )

    c1,c2,c3 = st.columns([1,5,2])

    with c1:
        thumb = row.get('thumbnail',None)

        if pd.notna(thumb):
            st.image(thumb,width=80)

    with c2:
        st.markdown(f"**{song_name}**")
        st.caption(artist_name)

    with c3:
        q=f"{song_name} {artist_name}".replace(" ","+")
        st.link_button(
        "▶ YOUTUBE PLAY",
        f"https://www.youtube.com/results?search_query={q}"
        )