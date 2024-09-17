import base64
import requests
from requests import post,get
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from bs4 import BeautifulSoup
from io import StringIO
import spotipy
import os



client_id= 'd05e0a5aada24e24b83cf88f56e5e933'
client_secret = '7f210846214549d3b427f13e9b9230ee'

def login ():
    url = 'http://localhost:8501'
    
    sp = spotipy.Spotify (auth_manager = SpotifyOAuth (
        client_id = client_id,
        client_secret = client_secret,
        redirect_uri = url,
        scope = 'playlist-modify-public playlist-modify-private'
    )) 



    return sp


def get_token():
    
    auth_string = client_id + ":"+client_secret
    auth_bytes = auth_string. encode ('utf-8')
    auth_base64 = str (base64.b64encode (auth_bytes),'utf-8')
    url = 'https://accounts.spotify.com/api/token'

    headers = {'Authorization': 'Basic '+ auth_base64,
               'Content-Type':'application/x-www-form-urlencoded'
    
    }
    
    data  ={'grant_type': 'client_credentials'}
    
    result = post (url, headers = headers, data = data)
    json_result = json.loads (result.content)
    token = json_result['access_token']
    return token

        
def get_auth_header (token):
    return {'Authorization': 'Bearer ' + token}

#SEARCH FOR THE ARTIST AND GET THE FOLLOWERS, IMAGES, POPULARITY, GENRES, ID, NAME

def search_for_artist (token, artist_name):
    info = {}
    url = 'https://api.spotify.com/v1/search'
    headers = get_auth_header (token)
    query = f'?q={artist_name}&type=artist&limit=1'

    query_url = url + query
    result = get (query_url, headers = headers)
    json_result = json.loads (result.content)['artists']['items']

    #print (json_result)
    if len (json_result) == 0:
        print ('no artist with this name exists...')
        return None

    info ['id'] = json_result [0]['id']
    info ['name'] = json_result [0]['name']
    info ['images'] = json_result [0]['images']
    info ['popularity'] = json_result [0]['popularity']
    info ['followers'] = json_result [0]['followers']['total']
    
    
    return info

#GET THE ARTIST'S TOP SONGS

def artist_top_songs(token, artist_id):
    headers = get_auth_header (token)
    url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks'
    result = get (url, headers = headers)
    json_results = json.loads (result.content)
    ret = json_results['tracks']

    #print (ret)
    top_song_info = []
    
    for ind in range (len (ret)): 
        info = {}
        
        #get name, popularity, album name, id

        info ['name'] = ret[ind]['name']
        info['popularity'] = ret[ind]['popularity']
        info ['album_name'] = ret[ind]['album']['name']
        info ['id'] = ret[ind]['id']

        top_song_info.append (info)
    return top_song_info

#GET RELATED ARTISTS name, popularity, image, id, genre, followers

def related_artist (token, artist_id):
    related_artist_infos = []
    headers = get_auth_header (token)
    url = f'https://api.spotify.com/v1/artists/{artist_id}/related-artists'
    result = get (url, headers = headers)
    json_results = json.loads (result.content)
    artists = json_results ['artists']

    for x in range (len (artists)):
        related_artist_info = {}
        related_artist_info['name'] = json_results ['artists'][x]['name']
        related_artist_info['popularity'] = json_results ['artists'][x]['popularity']
        related_artist_info['images'] = json_results ['artists'][x]['images']
        related_artist_info['id'] = json_results ['artists'][x]['id']
        related_artist_info['followers'] = json_results ['artists'][x]['followers']['total']
        related_artist_info['genres'] = json_results ['artists'][x]['genres']

        related_artist_infos.append (related_artist_info)

    return related_artist_infos

def track_features (token, info): 
    headers = get_auth_header (token)
    #go through every dictionary value in the list
    for song_ind in range (len (info)): 
        #extract the id
        song_id = info [song_ind]['id']
        url = f'https://api.spotify.com/v1/audio-features/{song_id}'
        result = get (url, headers = headers)
        json_results = json.loads (result.content)

        #put the track features into the dictionary
        info[song_ind]['acousticness'] = json_results['acousticness']
        
        #how suitable a track is for dancing 
        info[song_ind]['danceability'] = json_results['danceability']
        
        #measures how fast, loud, and noisy a track is 
        info[song_ind]['energy'] = json_results['energy']

        #speechiness detected the presence of spoken words in a track
        info[song_ind]['speechiness'] = json_results['speechiness']

        info[song_ind]['loudness'] = json_results['loudness']

        #measure the musical positivnessness
        info[song_ind]['valence'] = json_results['valence']
        
        
        
    return info


def track_viz(df):
    fig = go.Figure()

    fig.add_trace (go.Scatter (x=df["name"], 
                            y=df["acousticness"],
                            name = 'acousticness', 
                            line = dict (color = '#F3A6C8')
                            ))

    fig.add_trace (go.Scatter (x=df["name"], 
                            y=df["danceability"],
                            name = 'danceability', 
                            line = dict (color = '#AEB5FF')
                            ))
    fig.add_trace (go.Scatter (x=df["name"],
                            y=df["energy"], 
                            name = 'energy',
                            line = dict (color = '#81E3E1')
                            ))

    fig.add_trace (go.Scatter (x=df["name"],
                            y=df["valence"], 
                            name = 'valence',
                            line = dict (color = '#95C8F3')
                            ))

    fig.add_trace (go.Scatter (x=df["name"],
                            y=df["speechiness"], 
                            name = 'speechiness',
                            line = dict (color = '#FBAC87')
                            ))

    fig.update_layout(
        template='simple_white',  # Optional: Start with a built-in template
        title='Top Songs and Scores'
        #font=dict(family='Arial', size=14, color='white'),
        #plot_bgcolor='black',
        #paper_bgcolor='black'
    )

    return fig

def loudness_viz (df):
    sorted_loudness = df.sort_values (by = 'loudness', ascending = False)
    colors = ['#d7d7d7',] * len (df)
    colors [0] = '#CEFFC9'
    colors [len(df)-1] = '#ffcbd1' 


    fig2 = make_subplots (rows = 2, cols = 1)

    fig2.add_trace (go.Bar (x = sorted_loudness['name'],
                        y = sorted_loudness ['loudness'],
                        marker_color = colors),
                    row = 1, col = 1
                            
        )

    fig2.update_layout (template='simple_white',
                        title_text = 'Distribution of Loudness of Top Songs',
                        title_font=dict(size=15))

    return fig2

def popularity_viz (df):
    colors = ['#d7d7d7',] * len (df)
    colors [0] = '#CEFFC9'
    colors [len(df)-1] = '#ffcbd1'

    fig3= go.Figure (
        data = [go.Bar (x = df['name'],
                        y = df ['popularity'],
                        marker_color = colors)
                            ]
        )
                    

    fig3.update_layout (template='simple_white',
                        title_text = 'Distribution of Popularity of Top Songs')

    return fig3


def circle(df):
    categories = df ['name']
    values = np.array(df['popularity'])
    colors = plt.cm.rainbow(np.linspace(0, 1, len(values)))

    # Number of bars
    num_bars = len(categories)

    # Compute angle for each bar
    angles = np.linspace(0, 2 * np.pi, num_bars, endpoint=False).tolist()

    # The plot is made in a circular (polar) coordinate system
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    # Set the width of each bar
    width = 2 * np.pi / num_bars

    # Create bars
    bars = ax.bar(angles, values, width=width, color=colors, edgecolor='white', linewidth=2)

    # Add labels
    for bar, angle, label in zip(bars, angles, categories):
        rotation = np.rad2deg(angle)
        alignment = "right" if angle > np.pi / 2 else "left"
        ax.text(x=angle,  
                y=bar.get_height() * 0.5, 
                s=label,ha='center',
                  va='center', 
                  rotation=rotation, 
                  rotation_mode="anchor",
                  color='white',
                  fontweight='bold', )

    # Customize the plot (similar background and color style as the image)
    ax.set_facecolor('none')  # Transparent background for the plot area
    fig.patch.set_alpha(0.0)  # Transparent background for the entire figure

    # Remove all grid lines
    ax.grid(False)

    # Remove y-tick labels
    ax.set_yticklabels([])

    ax.spines['polar'].set_visible(False)

    # Remove x-tick labels
    ax.set_xticklabels([])

    ax.set_title('Popularity By Songs', fontsize=25, pad=40, color = 'white',
                 fontweight='bold',
                 fontfamily='Open Sans')


    ax.set_facecolor('white') 


    return fig


def print_related_artist (related_artist_info, ind, curr_pop):

    if len (related_artist_info[ind]['images']) !=0:
        image = related_artist_info[ind]['images'][0]['url']

        st.markdown(
        f"""
        <div style='text-align: center;'>
            <img src="{image}" alt='Centered Image' style='width: 200px; font-size: 100px; height: auto; border-radius: 150px;' />
        </div>
        """,
        unsafe_allow_html=True
        )
    name = related_artist_info[ind]['name']
    st.write (name)
    popularity = related_artist_info[ind]['popularity']
    st.metric (label = 'Popularity', value = int (popularity), delta = int (popularity) - int (curr_pop))



#WEBSCRAP WIKI INFO ------------------------------------------------------------------------------------------------------------------------------------------------
def wiki_info(wiki_url):
    response = requests.get (wiki_url)
    page_content = response.content
    soup = BeautifulSoup (page_content,'lxml')

    #CREATE AWARDS DATAFRAME ------------------------------------------------------------------------

    header = soup.find('h2', id='Awards_and_nominations')

    if header is not None:
        # Initialize the variable to hold the next table with the desired class
        next_table = None
        
        # Traverse the siblings of the header to find the next table with the specified class
        for sibling in header.find_all_next():
            if sibling.name == 'table' and len (sibling.find_all ('th')) != 0:
                #print ('found table')
                #print (sibling)
                next_table = sibling
                break

        next_table = str (next_table)
        next_table = StringIO (next_table)
        
        
        awards_df = pd.read_html (next_table)
        
        awards_df = pd.DataFrame (awards_df[0])

    else: 
        awards_df= None


    #CREATE TELEVISION DATAFRAME ------------------------------------------------------------------------
    
    header = soup.find('h3', id='Television')

    if header is not None:
        # Initialize the variable to hold the next table with the desired class
        next_table = None
        
        # Traverse the siblings of the header to find the next table with the specified class
        for sibling in header.find_all_next():
            if sibling.name == 'table' and len (sibling.find_all ('th')) != 0:
                #print ('found table')
                #print (sibling)
                next_table = sibling
                break
        
        
        tel_df = pd.read_html (str(next_table))
        
        tel_df = pd.DataFrame (tel_df[0])
    
    else: 
        tel_df= None

    #CREATE FILM DATAFRAME ------------------------------------------------------------------------

    header = soup.find('h3', id='Film')

    if header is not None: 
        # Initialize the variable to hold the next table with the desired class
        next_table = None
        
        # Traverse the siblings of the header to find the next table with the specified class
        for sibling in header.find_all_next():
            if sibling.name == 'table' and len (sibling.find_all ('th')) != 0:
                #print ('found table')
                #print (sibling)
                next_table = sibling
                break
        
        
        film_df = pd.read_html (str(next_table))
        
        film_df = pd.DataFrame (film_df[0])
    else: 
        film_df= None
        

    #CREATE CAREER DATAFRAME ------------------------------------------------------------------------
    career_text = ''
    header = soup.find('h2', id='Career')

    if header is None: 
        header = soup.find('h2', id='Life_and_career')

    if header is not None: 
        for sibling in header.find_all_next():
            if sibling.name == 'p':
                career_text+=  '\n' + sibling.get_text()
    else: 
        career_text= None
    return career_text, film_df, tel_df, awards_df



    

    

    




        
