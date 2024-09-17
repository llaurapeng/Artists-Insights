
import create_data
import pandas as pd
import streamlit as st
import create_data as create_data

st.set_page_config(layout="wide")

st.title ('Insights into Any Musical Artist')

title = st.text_input("Artist Name: ", "Sabrina Carpenter")
st.write("The current artist is", title)




token = create_data.get_token ()


#dictionary that has the artist id, name, popularity, genre and followers
artist = create_data.search_for_artist (token, title)


#a list of dictionaries that have the name, popularity, and album name of the top songs
artist_top_song_info = create_data.artist_top_songs (token, artist['id'])

#a list of dictionaries has the related artists
related_artist_info = create_data.related_artist (token, artist['id'])


#add track features
artist_info = create_data.track_features (token, artist_top_song_info)

df = pd.DataFrame (artist_info)

df = df.sort_values (by = 'popularity', ascending = False)

st.write ('-----')
st.markdown(f"<h1 style='text-align: center;'>{artist['name']}</h1>", unsafe_allow_html=True)

image = artist ['images'][0]['url']


st.markdown(
    f"""
    <div style='text-align: center;'>
        <img src="{image}" alt='Centered Image' style='width: 200px; font-size: 100px; height: auto; border-radius: 150px;' />
    </div>
    """,
    unsafe_allow_html=True
)

followers = int (artist['followers'])
followers = "{:,}".format(followers)
                 
st.markdown(f"<h2 style='text-align: center;font-size: 20px;'>Followers: {followers} | Popularity: {artist['popularity']} </h2>", unsafe_allow_html=True)


st.write ('-----')

fig1 = create_data.track_viz (df)

fig2 = create_data.loudness_viz (df)
fig3 = create_data.popularity_viz (df)
fig3 = create_data.circle(df)

name = artist ['name'].replace (' ', '_')
wiki_url = f'https://en.wikipedia.org/wiki/{name}'
career_text, film_df, tel_df, awards_df = create_data.wiki_info (wiki_url)



left, right = st.columns ([3,1])

with left: 
    l, c, r = st.columns ([1,2,1])

    with c: 
        st.plotly_chart (fig1,use_container_width=True)
        with st.expander (label = '**How are the musical features calculated?**'):
            st.write ('**Acousticness:** A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the track is acoustic.')
            st.write ('**Danceability:** Danceability describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable.')
            st.write ('**Energy:** Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy.')
            st.write ('**Instrumentalness:** Predicts whether a track contains no vocals. "Ooh" and "aah" sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly "vocal". The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.')
            st.write ('**Liveness:** Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live.')

    l, c, c2, r = st.columns ([1,2,1.8,1])

    with c: 
        st.plotly_chart (fig2,use_container_width=True)


    with c2: 
        st.write ('')
        st.write ('')
        st.pyplot (fig3,use_container_width=True)

  
    
    def highlight(val):

        if str (val) == 'Won':  
            return 'background-color: #77DD77'
        elif str(val) == 'Nominated':
            return 'background-color: #9BF6FF'
        elif str(val)== 'Pending':
            return 'background-color: #BDB2FF'
        elif val == 'Finalist':
            return 'background-color: #FFC6FF'
        else: 
            return ''
        
    if awards_df is not None: 
        #AWARD DATA FRAME 
        st.dataframe(awards_df.style.applymap (highlight))



with right: 
    st.write ('')
    st.write ('')
    st.write ('Related Artists: ')
    ind = 0


    loopVal = int (len (related_artist_info) / 4)
    ind = 0
    for x in range (loopVal):

        one, two, three, four = st.columns (4)

        with one: 
            create_data.print_related_artist (related_artist_info, ind, artist['popularity'])
        ind+= 1
        with two: 
            create_data.print_related_artist (related_artist_info, ind,artist['popularity'])
        ind+= 1
        with three: 
            create_data.print_related_artist (related_artist_info, ind,artist['popularity'])
        ind+= 1
        with four: 
            create_data.print_related_artist (related_artist_info, ind,artist['popularity'])
        ind+= 1

with st.expander(label = 'Television and Films: '):

    table1, table2 = st.columns ([1,2])

    with table1: 

        if film_df is not None: 
            #df_filt = film_df.drop(columns=['Notes'])
            #df_filt = df_filt.reset_index(drop=True)
            st.dataframe(film_df.style)

        else:
            st.write ('There is no film details about this artist found.')

    with table2: 
        if tel_df is not None:
            st.dataframe(tel_df.style)
        else: 
            st.write ('There is no television details about this artist found.')

with st.expander(label = 'Career: '):
    if career_text is not None: 
        st.write (career_text)
    else: 
        st.write ('There is no career details about this artist found.')
