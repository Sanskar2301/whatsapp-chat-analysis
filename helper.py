from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
import os

# Initialize URL Extractor
extract = URLExtract()

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Fetch the number of messages
    num_messages = df.shape[0]

    # Fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # Fetch number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # Fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    df = df[df['user'] != "group_notification"]
    x = df['user'].value_counts().head()
    df = (df['user'].value_counts() / df.shape[0] * 100).round(2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x, df
def most_common_words(selected_user, df):
    stop_words = set()
    if os.path.exists("stop_hinglish.txt"):
        with open("stop_hinglish.txt", "r") as f:
            stop_words = set(f.read().split())

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification'].copy()
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []
    for message in temp['message']:
        words.extend([word.lower() for word in message.split() if word not in stop_words])
    most_common_df = pd.DataFrame(list(Counter(words).most_common(20)))

    return most_common_df


def extract_emojis(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    # Ensure 'message' column has no NaN values
    df = df.dropna(subset=['message'])

    # Extract emojis using emoji.emoji_list()
    emojis = []
    df['message'] = df['message'].apply(lambda x: x.encode('utf-8').decode('utf-8') if isinstance(x, str) else x)
    for message in df['message']:
        extracted = [e['emoji'] for e in emoji.emoji_list(message)]
        emojis.extend(extracted)

    # Count occurrences
    emoji_counts = Counter(emojis)
    
    # Convert to DataFrame
    emoji_df = pd.DataFrame(emoji_counts.most_common(), columns=['emoji', 'count'])

    return emoji_df

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    timeline['time'] = timeline['month'] + " " + timeline['year'].astype(str)

    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()
def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    
    heatmap_data = df.pivot_table(index='day_name', columns='hour', values='message', aggfunc='count').fillna(0)

    return heatmap_data
