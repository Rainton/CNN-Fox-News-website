from flask import Flask, jsonify, request
from newsapi import NewsApiClient
import string
import json

app = Flask(__name__)
newsapi = NewsApiClient(api_key='6fe8231d03d44f71a91518bcdc21b4ea')
cnn_headlines = newsapi.get_top_headlines(sources='cnn', language='en', page_size=30)
fox_headlines = newsapi.get_top_headlines(sources='fox-news', language='en', page_size=30)
slide_headlines = newsapi.get_top_headlines(language='en', page_size=30)
all_headlines = newsapi.get_top_headlines(language='en', page_size=100)

cnn = []
fox = []
slide = []
word_map = {}
titles = []
categorys = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
sources = []
search = []

for c in categorys:
    sources.append(newsapi.get_sources(category=c, language='en', country='us'))
categorys.append('all')
sources.append(newsapi.get_sources(language='en', country='us'))

def split_word(s):
    words = s.split()
    remove = string.punctuation + string.digits
    table = str.maketrans('', '', remove)
    wordlist = []
    for w in words:
        w = w.translate(table)
        w = w.lower()
        if w != "" and not w.isdigit():
            wordlist.append(w)
    return wordlist


for headline in cnn_headlines['articles']:
    notEmpty = True
    for key in headline:
        if headline[key] is None or headline[key] == 'null' or headline[key] == '':
            notEmpty = False
            break
    if notEmpty:
        cnn.append(headline)
    if len(cnn) == 4:
        break

for headline in fox_headlines['articles']:
    notEmpty = True
    for key in headline:
        if headline[key] is None or headline[key] == 'null' or headline[key] == '':
            notEmpty = False
            break
    if notEmpty:
        fox.append(headline)
    if len(fox) == 4:
        break

for headline in slide_headlines['articles']:
    notEmpty = True
    for key in headline:
        if headline[key] is None or headline[key] == 'null' or headline[key] == '':
            notEmpty = False
            break
    if notEmpty:
        slide.append(headline)
    if len(slide) == 5:
        break

f = open("stopwords_en.txt")
lines = f.readlines()
stopwords = []
for line in lines:
    line = line.rstrip()
    stopwords.append(line)

remove = string.punctuation + string.digits
for headline in all_headlines['articles']:
    if headline['title'] is not None:
        word_list = split_word(headline['title'])
        for word in word_list:
            word = ''.join(c for c in word if c.isalnum())
            if word not in stopwords and word != '-':
                if word in word_map:
                    word_map[word] = word_map[word] + 1
                else:
                    word_map[word] = 1

sort_word_map = sorted(word_map.items(), key=lambda x: x[1], reverse=True)
filtered_sort_word_map = sort_word_map[0:25]
word_map_tuple = []
for submap in filtered_sort_word_map:
    word_map_tuple.append((submap[0].capitalize(), submap[1]))


@app.after_request
def after_request(resp):
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["Pragma"] = "no-cache"
    return resp
    

@app.route('/api/cnn', methods=['GET'])
def get_cnn():
    return jsonify({'cnn_headlines': cnn})


@app.route('/api/fox', methods=['GET'])
def get_fox():
    return jsonify({'fox_headlines': fox})


@app.route('/api/slide', methods=['GET'])
def get_slide():
    return jsonify({'slide': slide})


@app.route('/api/word_cloud', methods=['GET'])
def get_word_cloud():
    return dict(word_map_tuple)


@app.route('/api/source', methods=['GET'])
def get_source():
    return jsonify({categorys[0]: sources[0], categorys[1]: sources[1], categorys[2]: sources[2], categorys[3]: sources[3], categorys[4]: sources[4], categorys[5]: sources[5], categorys[6]: sources[6], categorys[7]: sources[7]})


@app.route('/api/search', methods=['GET'])
def get_search():
    return jsonify({'search': search})


@app.route('/', methods=['GET', 'POST'])
def homepage():
    if(request.method == 'POST'):
        keyword = request.form['keyword']
        fromDate = request.form['from']
        toDate = request.form['to']
        category = request.form['category']
        source = request.form['source']
        global search
        try:
            search = []
            if(source == 'all'):
                for i in range(0, 8):
                    if categorys[i] == category:
                        sourcelist = sources[i]['sources']
                        sourcestring = ""
                        for s in sourcelist:
                            sourcestring = sourcestring + s['id'] + ","
                        sourcestring = str(sourcestring[:-1])
                        search_headlines = newsapi.get_everything(q=keyword, from_param=fromDate, to=toDate, sources=sourcestring, language='en', sort_by='publishedAt')
                        break
            else:
                search_headlines = newsapi.get_everything(q=keyword, from_param=fromDate, to=toDate, sources=source, language='en', sort_by='publishedAt')
            for headline in search_headlines['articles']:
                notEmpty = True
                for key in headline:
                    if headline[key] is None or headline[key] == 'null' or headline[key] == '':
                        notEmpty = False
                        break
                if notEmpty:
                    search.append(headline)
                if(len(search) == 15):
                    break
        except Exception as e:
            eString = str(e)
            eJson = eval(eString)
            search.clear()
            search.append(eJson)
    return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run(debug=open)
