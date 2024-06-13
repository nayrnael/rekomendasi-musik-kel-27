import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns

# Memuat data dari file Excel
df = pd.read_excel('udinbang.xlsx')

# Fungsi untuk mengambil daftar penyanyi dan lagu dari dataset
def get_song_list(df):
    return df[['artist', 'nama_track']]

def get_song_info_by_id(track_id, df):
    song_info = df[df['track_id'] == track_id].iloc[0]
    return song_info

def get_songs_by_query(query, df):
    songs = df[
        df['track_id'].str.contains(query, case=False, na=False) |
        df['artist'].str.contains(query, case=False, na=False) |
        df['nama_album'].str.contains(query, case=False, na=False) |
        df['nama_track'].str.contains(query, case=False, na=False)
    ]
    return songs

def recommend_songs_by_genre(track_id, df, n_recommendations=3):
    song_info = get_song_info_by_id(track_id, df)
    track_genre = song_info['track_genre']
    similar_songs = df[(df['track_genre'] == track_genre) & (df['track_id'] != track_id)]
    recommendations = similar_songs.sort_values(by='popularity', ascending=False).head(n_recommendations)
    return recommendations

def recommend_songs_by_artist(track_id, df, n_recommendations=3):
    song_info = get_song_info_by_id(track_id, df)
    artist = song_info['artist']
    similar_songs = df[(df['artist'] == artist) & (df['track_id'] != track_id)]
    recommendations = similar_songs.sort_values(by='popularity', ascending=False).head(n_recommendations)
    return recommendations

def recommend_songs_by_danceability_energy_tempo(track_id, df, n_recommendations=3):
    song_info = get_song_info_by_id(track_id, df)
    similar_songs = df[
        (df['danceability'] >= song_info['danceability'] - 0.1) & (df['danceability'] <= song_info['danceability'] + 0.1) &
        (df['energy'] >= song_info['energy'] - 0.1) & (df['energy'] <= song_info['energy'] + 0.1) &
        (df['tempo'] >= song_info['tempo'] - 10) & (df['tempo'] <= song_info['tempo'] + 10) &
        (df['track_id'] != track_id)
    ]
    recommendations = similar_songs.sort_values(by='popularity', ascending=False).head(n_recommendations)
    return recommendations

# Menampilkan informasi lagu menggunakan kartu
def display_song_info(song_info):
    st.markdown(f"""
    <div style='padding:10px;border:1px solid #ddd;border-radius:10px;margin-bottom:10px;box-shadow:0 4px 8px 0 rgba(0, 0, 0, 0.2);'>
        <h4>{song_info['nama_track']} - {song_info['artist']}</h4>
        <p><strong>Album:</strong> {song_info['nama_album']}</p>
        <p><strong>Popularity:</strong> {song_info['popularity']}</p>
        <p><strong>Explicit:</strong> {song_info['explicit']}</p>
        <p><strong>Danceability:</strong> {song_info['danceability']}</p>
        <p><strong>Energy:</strong> {song_info['energy']}</p>
        <p><strong>Loudness:</strong> {song_info['loudness']}</p>
        <p><strong>Mode:</strong> {song_info['mode']}</p>
        <p><strong>Tempo:</strong> {song_info['tempo']}</p>
        <p><strong>Genre:</strong> {song_info['track_genre']}</p>
    </div>
    """, unsafe_allow_html=True)

def display_recommendations(recommendations, header):
    st.subheader(header)
    num_recommendations = len(recommendations)
    rows = num_recommendations // 3 + (num_recommendations % 3 > 0)
    
    for row in range(rows):
        cols = st.columns(3)
        for i in range(3):
            idx = row * 3 + i
            if idx < num_recommendations:
                with cols[i]:
                    display_song_info(recommendations.iloc[idx])


# Fungsi utama untuk halaman 'Sistem Rekomendasi Musik'
def main():
    st.title('Sistem Rekomendasi Musik')
    st.subheader('Cari Lagu dan Rekomendasi')
    
    # Input dari pengguna
    query = st.text_input('Masukkan Track ID, Artist, Album Name, atau Track Name:')

    if query:
        # Mencari lagu berdasarkan query
        songs = get_songs_by_query(query, df)
        
        if not songs.empty:
            st.write('Lagu yang ditemukan:')
            selected_song = st.selectbox('Pilih lagu:', songs['nama_track'] + ' - ' + songs['artist'])
            
            if selected_song:
                track_id = songs[songs['nama_track'] + ' - ' + songs['artist'] == selected_song]['track_id'].values[0]
                song_info = get_song_info_by_id(track_id, df)
                
                st.subheader('Informasi Lagu')
                display_song_info(song_info)

                st.subheader('Rekomendasi Lagu')

                recommendations_genre = recommend_songs_by_genre(track_id, df)
                recommendations_artist = recommend_songs_by_artist(track_id, df)
                recommendations_det = recommend_songs_by_danceability_energy_tempo(track_id, df)

                display_recommendations(recommendations_genre, 'Rekomendasi Berdasarkan Genre')
                display_recommendations(recommendations_artist, 'Rekomendasi Berdasarkan Artist')
                display_recommendations(recommendations_det, 'Rekomendasi Berdasarkan Danceability, Energy, dan Tempo')
        else:
            st.write('No songs found.')

# Fungsi untuk halaman 'Penjelasan Dataset'
def penjelasan_dataset():
    
    st.title('Dataset Spotify')
    st.write('Dataset yang digunakan diperolah dari platform Kaggle yang berisi 77 ribu baris dan 9 atribut.')
    # Menjelaskan Content-Based Filtering
    st.write("""
    ### Content-Based Filtering
    Merupakan jenis sistem rekomendasi yang mampu memberikan rekomendasi item yang sangat personal kepada setiap pengguna berdasarkan karakteristik konten. Sistem ini menggunakan perhitungan cosine similarity dengan mengukur jarak antara 2 vektor dalam ruang berdimensi tinggi dengan rumus sebagai berikut:

    $$
    \\text{cos}(x, y) = \\frac{x \cdot y}{||x|| \cdot ||y||}
    $$

    Jika menggunakan rumus ini, maka kita akan mendapatkan nilai antara -1 hingga 1. Semakin mendekati 1 maka kedua item tersebut akan semakin berbeda. Metode ini sangat cocok untuk merekomendasikan musik berdasarkan beberapa atribut lainnya seperti genre, nama artis, nama album, dan tingkat popularitas.
    """)

    st.dataframe(df)

    # Menampilkan visualisasi data
    st.subheader('Visualisasi Data')

    # Visualisasi 1: 10 Nama Artist dengan Lagu Terbanyak
    st.write('### 10 Nama Artist dengan Lagu Terbanyak')
    artist_counts = df['artist'].value_counts().head(10)
    st.bar_chart(artist_counts)

    # Visualisasi 2: 10 Lagu dengan Popularity Tertinggi
    st.write('### 10 Lagu dengan Popularity Tertinggi')
    top_tracks = df[['nama_track', 'popularity']].sort_values(by='popularity', ascending=False).head(10)
    top_tracks = top_tracks.set_index('nama_track')  # Set the track names as the index for the bar chart
    st.bar_chart(top_tracks)

    # Visualisasi 3: Diagram Pie untuk Kolom Explicit
    st.write('### Diagram Pie untuk Kolom Explicit')
    explicit_counts = df['explicit'].value_counts().reset_index()
    explicit_counts.columns = ['explicit', 'count']

    fig = px.pie(explicit_counts, values='count', names='explicit', title='Distribusi Explicit (True/False)',
                labels={'explicit': 'Explicit', 'count': 'Count'}, 
                color_discrete_sequence=px.colors.qualitative.Set3)

    st.plotly_chart(fig)

    # Visualisasi 4: Diagram Pie untuk 5 Genre Terbanyak
    st.write('### Diagram Pie untuk 5 Genre Terbanyak')
    genre_counts = df['track_genre'].value_counts().head(5).reset_index()
    genre_counts.columns = ['track_genre', 'count']

    fig = px.pie(genre_counts, values='count', names='track_genre', title='Top 5 Genre Terbanyak',
                labels={'track_genre': 'Genre', 'count': 'Count'},
                color_discrete_sequence=px.colors.qualitative.Set3)

    st.plotly_chart(fig)

# List halaman yang tersedia
pages = {
    'Sistem Rekomendasi Musik': main,
    'Dataset': penjelasan_dataset,
}

# Sidebar untuk navigasi antar halaman
current_page = st.sidebar.radio('Navigator', list(pages.keys()))

# Tampilkan konten halaman yang dipilih
pages[current_page]()