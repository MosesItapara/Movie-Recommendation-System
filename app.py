import streamlit as st
import pickle
import requests
import random

st.set_page_config(page_title="CineMatch", page_icon="🎬", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0f;
    color: #f0ece4;
}
.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 100%);
}
h1.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    color: #f0ece4;
    margin-bottom: 0.2rem;
    letter-spacing: -0.5px;
}
p.hero-sub {
    color: #7a7a8a;
    font-size: 1rem;
    margin-bottom: 2.5rem;
}
.banner-scroll {
    display: flex;
    overflow-x: auto;
    gap: 12px;
    padding: 10px 0 16px 0;
    scrollbar-width: thin;
    scrollbar-color: #d4a843 #13131f;
    margin-bottom: 2rem;
}
.banner-scroll::-webkit-scrollbar { height: 4px; }
.banner-scroll::-webkit-scrollbar-track { background: #13131f; }
.banner-scroll::-webkit-scrollbar-thumb { background: #d4a843; border-radius: 4px; }
.banner-poster {
    flex: 0 0 auto;
    width: 130px;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #1e1e2e;
    transition: transform 0.2s;
}
.banner-poster:hover { transform: scale(1.05); border-color: #d4a843; }
.banner-poster img { width: 100%; display: block; }
.movie-card {
    background: #13131f;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    overflow: hidden;
    text-align: center;
}
.movie-card img { width: 100%; border-radius: 12px 12px 0 0; }
.movie-card .title {
    font-size: 0.85rem;
    font-weight: 500;
    color: #f0ece4;
    padding: 10px 8px;
    line-height: 1.3;
}
div[data-testid="stButton"] > button {
    background: #d4a843 !important;
    color: #0a0a0f !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.6rem 2.5rem !important;
}
.section-label {
    font-size: 0.75rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #d4a843;
    margin-bottom: 1.2rem;
    margin-top: 2.5rem;
}
</style>
""", unsafe_allow_html=True)

TMDB_API_KEY = "3120a42abec2919e7e738e6820199ac6"

movies = pickle.load(open("movies_list.pkl", 'rb'))
similarity = pickle.load(open("similarity.pkl", 'rb'))
movies_list = movies['title'].values


def fetch_poster(movie_title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_title}"
    response = requests.get(url)
    data = response.json()
    if data.get('results'):
        for result in data['results']:
            if result.get('poster_path'):
                return f"https://image.tmdb.org/t/p/w500{result['poster_path']}"
    return None


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda v: v[1])
    rec_movies, rec_posters = [], []
    for i in distance[1:6]:
        title = movies.iloc[i[0]].title
        rec_movies.append(title)
        rec_posters.append(fetch_poster(title) or "https://via.placeholder.com/300x450/13131f/7a7a8a?text=No+Poster")
    return rec_movies, rec_posters


# --- Banner ---
@st.cache_data
def get_banner_posters():
    sample = random.sample(list(movies_list), 20)
    posters = []
    for title in sample:
        p = fetch_poster(title)
        if p:
            posters.append(p)
        if len(posters) == 15:
            break
    return posters

banner_posters = get_banner_posters()
banner_html = '<div class="banner-scroll">'
for p in banner_posters:
    banner_html += f'<div class="banner-poster"><img src="{p}" /></div>'
banner_html += '</div>'
st.markdown(banner_html, unsafe_allow_html=True)

# --- Main UI ---
st.markdown('<h1 class="hero-title">CineMatch</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Discover movies tailored to your taste</p>', unsafe_allow_html=True)

col_select, col_btn = st.columns([4, 1])
with col_select:
    selectvalue = st.selectbox("", movies_list, label_visibility="collapsed")
with col_btn:
    st.write("")
    recommend_btn = st.button("Find Movies →")

if recommend_btn:
    movie_names, movie_posters = recommend(selectvalue)
    st.markdown('<p class="section-label">Recommended for you</p>', unsafe_allow_html=True)
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"""
            <div class="movie-card">
                <img src="{movie_posters[i]}" alt="{movie_names[i]}"/>
                <div class="title">{movie_names[i]}</div>
            </div>
            """, unsafe_allow_html=True)