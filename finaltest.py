import requests
from textblob import TextBlob
from transformers import pipeline
# import numpy
import streamlit as st
# from streamlit_option_menu import option_menu as op
import plotly.graph_objects as go
import plotly_express as px
import spacy
from bs4 import BeautifulSoup
from PIL import Image
import base64

nlp = spacy.load("en_core_web_sm")

st.set_page_config(  # Alternate names: setup_page, page, layout
	layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
	initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
	page_title="HackTastic 4",  # String or None. Strings get appended with "• Streamlit".
	page_icon=None,  # String, anything supported by st.image, or None.
)
st.write('----')


def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """, unsafe_allow_html=True )

add_bg_from_local('bg.png')


# import visualization as visualization
c1, c2 = st.columns([3,10])
img = Image.open('Hacktastic_4.png')
with c1:
    st.image(img)
with c2:
    st.write("<h1 style='font-size: 70px;'><b>Decision Zero</b></h1>", unsafe_allow_html=True)
    st.write("<h5><i>Reputation  threat  detector</i></h1>", unsafe_allow_html=True)
st.write('----')
def fetch_negatives(url):
    req2 = requests.get(url)
    soup2 = BeautifulSoup(req2.content, "html.parser")

    raw_text = soup2.get_text()

    doc2 = nlp(raw_text)

    sentences = []
    temp_sents = list(doc2.sents)
    for sentence in temp_sents:
        sentences.append(sentence.text)
    final_sentences = []
    for sentence in sentences:
        test = sentence
        filter = ''.join([chr(i) for i in range(1, 32)])
        final_sentences.append(test.translate(str.maketrans('', '', filter)))

    negative_sentences = []
    print(len(final_sentences))
    for x in final_sentences:
        blob = TextBlob(x)
        if blob.sentiment.polarity < -0.1:
            negative_sentences.append(x)

    return negative_sentences

def piechart(dicti):
    fig = go.Figure(data=[go.Pie(labels=list(dicti.keys()), values=list(dicti.values()))])
    return fig


def showpiechart(fig):
    st.plotly_chart(fig)


def linechart(l):
    y = []
    for i in range(len(l)):
        y.append(i)
    fig = px.line(y=l, x=y, title="Reputation over time")
    st.plotly_chart(fig)


company_name = st.text_input("Enter company's name")
# company_name = 'twitter'
url = f"https://newsapi.org/v2/everything?q={company_name}&from=2022-12-15&sortBy=popularity&apiKey=4c184a1d776548cd8837883e938bd715&language=en"
#9314028317d8492aa3bb9a9a5bd38287
res = requests.get(url)
fox = res.json()
negcount = 0
poscount = 0
replist = []
l=[]
if (len(company_name) > 0):
    allArticles = fox["articles"]

    classifier = pipeline("sentiment-analysis")

    allArticlesLength = len(allArticles)

    negativeArticles = []

    with st.spinner("Loading"):
        f = open('analytics.csv', 'w')
        f.write('')
        f.close()
        f = open('analytics.csv', 'a')
        f.write('publisher,url,date,threat degree')

        for i in range(0, allArticlesLength):
            try:
                # deb = st.empty()
                title = allArticles[i]["title"]
                description = allArticles[i]["description"]
                tiltleRes = classifier(title)
                if (tiltleRes[0]['label'] == 'NEGATIVE'):
                    replist.append(-1 * (tiltleRes[0]['score']))
                else:
                    replist.append(tiltleRes[0]['score'])
                descriptionRes = classifier(description)
                if (tiltleRes[0]['label'] == "NEGATIVE" and tiltleRes[0]['score'] > 0.9 and descriptionRes[0][
                    'label'] == "NEGATIVE" and descriptionRes[0]['score'] > 0.9 and (
                        company_name.casefold() in title.casefold() or company_name.casefold() in description.casefold())):
                    negativeArticles.append(allArticles[i])
                    negcount += 1
                else:
                    poscount += 1
                name = allArticles[i]['source']
                name = name['name']
                date = allArticles[i]['publishedAt']
                date = date[0:10]
                s = f'''\n{name}, {allArticles[i]["url"]},{date} ,{replist[-1]}'''
                f.write(s)

            except:
                pass
        f.close()

    negativeArticlesLength = len(negativeArticles)

    if (negativeArticlesLength == 0):
        st.info("No negative articles found")
    else:

        def card(img_url, title, desc, url):
            r = f'''
            <a href={url} style="text-decoration: none;color: black;">
                <div class='my-3 col-md-4'>
                    <div class="card" style="width: 18rem;height:35rem">
                        <img src={img_url} class="card-img-top" alt="..." style="height:10rem">
                        <div class="card-body">
                            <h5 class="card-title" >{title}</h5>
                            <p class="card-text">{desc}</p>
                            <h4> <a href={url}> Read More >> </a> </h4>
                        </div>
                    </div>
                </div>
            </a>

            '''
            return r


        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        st.markdown('''
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-GLhlTQ8iRABdZLl6O3oVMWSktQOp6b7In1Zl3/Jr59b6EGGoI1aFkw7cmDA6j6gD" crossorigin="anonymous">
        ''', unsafe_allow_html=True)

        for i in range(0, negativeArticlesLength, 4):
            with col1:
                st.write(
                    card(negativeArticles[i]["urlToImage"], desc=negativeArticles[i]["description"],
                         title=negativeArticles[i]["title"],url=negativeArticles[i]["url"]), unsafe_allow_html=True)
                # st.write(negativeArticles[i]['url'])
                t = negativeArticles[i]['publishedAt']
                t = t[0:10]
                st.write(t)
                b = st.button("Read risk entities",key = i)
                if b:
                    l = fetch_negatives(negativeArticles[i]['url'])



            if (i + 1 < negativeArticlesLength):
                with col2:
                    st.write(
                        card(negativeArticles[i + 1]["urlToImage"], desc=negativeArticles[i + 1]["description"],
                             title=negativeArticles[i + 1]["title"],url=negativeArticles[i+1]["url"]), unsafe_allow_html=True)
                    t = negativeArticles[i+1]['publishedAt']
                    t = t[0:10]
                    st.write(t)
                    b = st.button("Read risk entities", key=i+1)
                    if b:
                        l = fetch_negatives(negativeArticles[i+1]['url'])



            if (i + 2 < negativeArticlesLength):
                with col3:
                    st.write(
                        card(negativeArticles[i + 2]["urlToImage"], desc=negativeArticles[i + 2]["description"],
                             title=negativeArticles[i + 2]["title"],url=negativeArticles[i+2]["url"]), unsafe_allow_html=True)
                    t = negativeArticles[i+2]['publishedAt']
                    t = t[0:10]
                    st.write(t)
                    b = st.button("Read risk entities", key=i+2)
                    if b:
                        l = fetch_negatives(negativeArticles[i+2]['url'])



            if (i + 3 < negativeArticlesLength):
                with col4:
                    st.write(
                        card(negativeArticles[i + 3]["urlToImage"], desc=negativeArticles[i + 3]["description"],
                             title=negativeArticles[i + 3]["title"],url=negativeArticles[i+3]["url"]), unsafe_allow_html=True)
                    t = negativeArticles[i+3]['publishedAt']
                    t = t[0:10]
                    st.write(t)
                    b = st.button("Read risk entities", key=i+3)
                    if b:
                        l = fetch_negatives(negativeArticles[i+3]['url'])

        for sent in l:
             st.write(sent)


        dict = {'Negative Responses': negcount, 'Positive Responses': poscount}
        fig = piechart(dict)
        showpiechart(fig)
        # linechart(replist)
else:
    st.error("Enter company's name first")