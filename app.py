from flask import Flask, render_template, request
from textblob import TextBlob
import pandas as pd
import altair as alt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

def convert_to_df(sentiment):
    sentiment_dict = {'polarity': sentiment.polarity, 'subjectivity': sentiment.subjectivity}
    sentiment_df = pd.DataFrame(sentiment_dict.items(), columns=['metric', 'value'])
    return sentiment_df

def analyze_token_sentiment(docx):
    analyzer = SentimentIntensityAnalyzer()
    pos_list = []
    neg_list = []
    neu_list = []
    for i in docx.split():
        res = analyzer.polarity_scores(i)['compound']
        if res > 0.1:
            pos_list.append((i, res))
        elif res <= -0.1:
            neg_list.append((i, res))
        else:
            neu_list.append(i)
    
    result = {'positives': pos_list, 'negatives': neg_list, 'neutral': neu_list}
    return result

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        raw_text = request.form['text']
        if raw_text:
            sentiment = TextBlob(raw_text).sentiment
            result_df = convert_to_df(sentiment)

            # Generate Matplotlib plot
            img = io.BytesIO()
            result_df.plot(kind='bar', x='metric', y='value', color=['blue', 'orange'])
            plt.title('Sentiment Analysis')
            plt.xlabel('Metric')
            plt.ylabel('Value')
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()

            token_sentiments = analyze_token_sentiment(raw_text)

            return render_template('result.html', 
                                   sentiment=sentiment, 
                                   plot_url=plot_url,
                                   token_sentiments=token_sentiments)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
