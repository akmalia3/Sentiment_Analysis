
import pandas as pd
import streamlit as st
import plotly.express as px
import swifter
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from wordcloud import WordCloud
from collections import Counter
from datetime import datetime

st.set_page_config(
    page_title="Dashboard Monitoring Sosmed",
    page_icon=":thermometer:",
    layout="wide",  # Use "wide" layout for a full-size dashboard
)

#st.subheader('Was the data helpful?')
# https://retro-tools.streamlit.app/
# https://bpmpkalsel-pmm-dashboard-71ttv1.streamlit.app/Platform_Merdeka_Mengajar

file_name = "ulasan-komentar-cleaning.xlsx"
df = pd.read_excel(file_name)
df = df.drop(['Unnamed: 0'], axis=1)

st.header('🌡️Sistem Pemantauan Media Sosial')
st.write('Sistem Pemantauan Media Sosial Dinas Kesehatan Kota Semarang')
#st.write(':angry:')
st.markdown("""---""")

df['Jenis Akun'].mask(df['Jenis Akun'] == 'Tidak diketahuai', 'Tidak diketahui', inplace=True)

nav3, nav4, nav5 = st.columns(3)
with nav3:
    sumber_data = st.selectbox("Pilih Sumber Data", options=df["Sumber"].unique())
        
with nav4:
    sentiment_data = st.multiselect("Pilih Sentiment", options=df["sentiment"].unique(), 
                                   default=df['sentiment'].unique())
        
with nav5:
    #data = pd.to_datetime(df['Tgl'], format="%Y-%m-%d", errors='coerce').dt.tz_localize(None)
    df['Tgl'] = pd.to_datetime(df['Tgl']).dt.date
    start = df['Tgl'].min()
    finish = df['Tgl'].max()
    start_date, end_date = st.date_input('Rentang Waktu',
                               (start, finish), 
                               start, 
                               finish,
                               format="YYYY.MM.DD")

# filter Tgl
output = (df['Tgl'] >= start_date) & (df['Tgl'] <= end_date)
# filter sumber, tamggal dan sentiment
df_selection = df.query("Sumber == @sumber_data & sentiment == @sentiment_data").loc[output]

right, left = st.tabs(['Ringkasan', 'Dataset'])
with left:
    st.write(df_selection)
    count = len(df_selection)
    ##this uses streamlit 'magic'!!!!
    f"Data bersumber dari {sumber_data} Dinas Kesehatan Kota Semarang, dengan jumlah komentar sebanyak", count

with right:
    # count data
    pos = df_selection['sentiment'].loc[df_selection['sentiment'] == 'positive']
    neg = df_selection['sentiment'].loc[df_selection['sentiment'] == 'negative']
    count = len(df_selection)
    
    b1, b2, b3 = st.columns([0.45,0.45,0.45])
    b1.metric("Jumlah Komentar", len(pos), "+ Positive")
    b2.metric("Jumlah Komentar", len(neg), "- Negative")
    b3.metric("Jumlah", count)

    # garis 
    st.markdown("""---""")

    df_selection['sentiment'].fillna(' ', inplace=True)
    df_selection['ngrams'].fillna(' ', inplace=True)
    df_selection['bigrams'].fillna(' ', inplace=True)
    df_selection['trigrams'].fillna(' ', inplace=True)
    
    col1, col2, col3 = st.columns([2,1,1])    
    with col1:
        # Visualisasi hasil sentiment
        color_custom = ['#3ca9ee', '#e14b32']
        sentiment = df_selection['sentiment'].value_counts()
        fig_sentiment = go.Figure()

        neg_df = df_selection[df_selection['sentiment'] == 'negative']
        pos_df = df_selection[df_selection['sentiment'] == 'positive']
        
        if not neg_df.empty:
            color = ['#e14b32']
            fig_sentiment.add_trace(go.Pie(labels=['Negative'], values=neg_df['sentiment'].value_counts(), 
                                           marker_colors=color, textinfo='label+percent', 
                                           hoverinfo='label+value', hole=0.3))
        if not pos_df.empty:
            color = ['#3ca9ee']
            fig_sentiment.add_trace(go.Pie(labels=['Positive'], values=pos_df['sentiment'].value_counts(), 
                                           marker_colors=color, textinfo='label+percent', 
                                           hoverinfo='value', hole=0.3))
        if not neg_df.empty and not pos_df.empty:
            fig_sentiment.add_trace(go.Pie(labels=['Positive','Negative'], values=sentiment,
                                      marker_colors=color_custom, textinfo='label+percent',
                                      hoverinfo='value', hole=0.3))
        
        fig_sentiment.update_layout(title=f"Persentase Sentimen {sumber_data}")
        st.plotly_chart(fig_sentiment, use_container_width=True)

    with col2:
        # frequent ngram word positive
        pos_review = df_selection['ngrams'].tolist()
        pos = ''.join(pos_review)
    
        text_pos = pos.split()
        freq_pos = Counter(text_pos)
        data2 = pd.DataFrame(freq_pos.most_common(), columns=['word', 'frequent'])

        custom_colors = [[0, '#CCCCCC'], [1, '#3ca9ee']]
        pos_freq = px.bar(data2.head(10), x='frequent', y='word', color='frequent', title="10 Kata yang Paling Sering Muncul", color_continuous_scale=custom_colors)
        pos_freq.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(pos_freq, use_container_width=True)

    with col3:
        # frequent ngram word negative
        neg_review = df_selection['bigrams'].tolist()
        neg = ''.join(neg_review)

        text_neg = neg.split()
        freq_neg = Counter(text_neg)
        data3 = pd.DataFrame(freq_neg.most_common(), columns=['word', 'frequent'])

        custom_colors = [[0, '#CCCCCC'], [1, '#e14b32']]
        neg_freq = px.bar(data3.head(10), x='frequent', y='word', title="10 Kata Bigram yang Paling Sering Muncul", color='frequent', color_continuous_scale=custom_colors)
        neg_freq.update_layout(yaxis={'categoryorder':'total descending'})
        st.plotly_chart(neg_freq, use_container_width=True)
        
    # Visualisasi Tgl komentar
    tgl_counts = df_selection['Tgl'].value_counts().reset_index()
    tgl_counts.columns = ['Tgl', 'Count']
    custom_colors = ['#dc6e55']
    fig_tgl = px.area(tgl_counts, x='Tgl', y='Count', title=f"Rentang Waktu Komentar {sumber_data}", color_discrete_sequence=custom_colors)
    st.plotly_chart(fig_tgl, use_container_width=True)
    
    jk_left, ja_middle, kt_right = st.columns([1,1,2])
    with jk_left:
        # Visualisasi jenis akun        
        jenis_akun = df_selection['Jenis Akun'].value_counts()
        labels = jenis_akun.keys()
        color = ['#61bdee', '#e14b32', '#dc6e55']
        fig_akun = go.Figure()
        fig_akun.add_trace(go.Pie(labels=labels, values=jenis_akun, marker_colors=color, textinfo='label+percent', hoverinfo='label+value'))

        fig_akun.update_layout(title=f'Persentase Jenis Akun {sumber_data}')
        st.plotly_chart(fig_akun, use_container_width=True)
        
        
    with ja_middle:
        # Visuaisasi jenis kelamin
        jenis_kelamin = df_selection['Jenis Kelamin'].value_counts()
        labels2 = jenis_kelamin.keys()
        color = ['#dc6e55', '#61bdee', '#a5d3eb']
        fig_jk = go.Figure()
        fig_jk.add_trace(go.Pie(labels=labels2, values=jenis_kelamin, marker_colors=color, textinfo='label+percent', hoverinfo='label+value'))
        fig_jk.update_layout(title=f'Persentase Jenis Kelamin {sumber_data}')
        st.plotly_chart(fig_jk, use_container_width=True)

    with kt_right:
    # Visualisasi Kategori
        custom_colors = [[0, '#CCCCCC'], [1, '#61bdee']]
        kategori = df_selection['Kategori'].value_counts()
        chart_kategori = px.bar(kategori, title=f"Kategori Pertanyaan pada {sumber_data}", color=kategori, color_continuous_scale=custom_colors) 
        st.plotly_chart(chart_kategori, use_container_width=True)

    # frequent ngrams
    df_selection['ngrams'].fillna(' ', inplace=True)
    ngram = ''.join(df_selection['ngrams'])
    
    # frequent bigrams
    df_selection['bigrams'].fillna(' ', inplace=True)
    bigram = ''.join(df_selection['bigrams'])
    
    # frequent trigram
    df_selection['trigrams'].fillna(' ', inplace=True)
    trigram = ''.join(df_selection['trigrams'])
    
    n, bi, tri = st.tabs(['Ngram', 'Bigram', 'Trigram'])
    with n:
        left, right = st.columns(2)
        with left:
            wordcloud = WordCloud(width = 2000, height = 1334,
                          random_state=1, background_color='white',#colormap='Pastel1',
                          collocations=False, normalize_plurals=False, collocation_threshold = 2, mode='RGBA', 
                          colormap='viridis').generate(ngram)#'PuBu_r'
            plt.figure(figsize=(10,10))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            plt.show()
            st.subheader('Wordcloud')
            st.pyplot(plt, use_container_width=True)
            #with right:
        with right:
            text = ngram.split()
            freq = Counter(text)
            data = pd.DataFrame(freq.most_common(), columns=['word', 'frequent'])
        
            fig_freq = px.bar(data.head(20), x='frequent', y='word',color='frequent', template='gridon', height=500)
            fig_freq.update_layout(yaxis={'categoryorder':'total ascending'})
            st.subheader('Frekuensi Kata')
            st.plotly_chart(fig_freq, use_container_width=True)

    with bi:
        bi_left, bi_right = st.columns(2)
        with bi_left:
            wordcloud_bigrams = WordCloud(width = 2000, height = 1334,
                                  random_state=1, background_color=None,colormap='Pastel1',
                                  collocations=False, normalize_plurals=False,
                                  collocation_threshold = 2).generate(bigram)

            plt.figure(figsize=(10,10))
            plt.imshow(wordcloud_bigrams, interpolation='bilinear')
            plt.axis("off")
            plt.show()
            st.subheader('Bigram Wordcloud')
            st.pyplot(plt)

        with bi_right:
            #with bigram_right:
            text_bi = bigram.split()
            freq_bi = Counter(text_bi)
            data_bi = pd.DataFrame(freq_bi.most_common(), columns=['word', 'frequent'])
            data_bi.style.background_gradient(cmap='Blues')
    
            fig_bi = px.bar(data_bi.head(20), x='frequent', y='word',
                color='frequent', template='seaborn')
            fig_bi.update_layout(yaxis={'categoryorder':'total ascending'})
            st.subheader('Bigram Frequent')
            st.plotly_chart(fig_bi, use_container_width=True)

    with tri:
        tri_right, tri_left = st.columns(2)
        with tri_right:
            wordcloud_trigrams = WordCloud(width = 2000, height = 1334,
                              random_state=1, background_color='white',colormap='plasma',
                              collocations=False, normalize_plurals=False,
                              collocation_threshold = 2).generate(trigram)
        # visualisasi dengan matplotlib
            plt.figure(figsize=(10,10))
            plt.imshow(wordcloud_trigrams, interpolation='bilinear')
            plt.axis("off")
            plt.show()
            st.subheader('Trigram Wordcloud')
            st.pyplot(plt)

        with tri_left:
            text_tri = trigram.split()
            freq_tri = Counter(text_tri)
            data_tri = pd.DataFrame(freq_tri.most_common(), columns=['word', 'frequent'])
            data_tri.style.background_gradient(cmap='Blues')
            
            fig_tri = px.bar(data_tri.head(20), x='frequent', y='word',
                             color='frequent', title="Top 40 Words Trigrams", template='plotly')
            fig_tri.update_layout(yaxis={'categoryorder':'total ascending'})
            st.subheader('Trigram Frequent')
            st.plotly_chart(fig_tri, use_container_width=True)
