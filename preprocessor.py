import re
import pandas as pd

def preprocess(data):
    # Updated regex pattern to correctly match 24-hour timestamps
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{2}:\d{2})\s-\s'

    # Extract timestamps
    dates = re.findall(pattern, data)  

    # Split chat data at timestamps (ignores first empty split part)
    messages = re.split(pattern, data)[1:]  

    # Ensure dates and messages have the same length
    if len(dates) != len(messages):
        # Fix misalignment by removing empty messages or merging broken ones
        while len(messages) > len(dates):
            messages[-2] += " " + messages[-1]  # Merge last two messages
            messages.pop()

    # Final validation
    if len(dates) != len(messages):
        raise ValueError(f"❌ Still mismatched: {len(dates)} timestamps vs {len(messages)} messages.")

    # Create DataFrame
    df = pd.DataFrame({'message_date': dates, 'user_message': messages})

    # Convert to datetime format
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %H:%M', errors='coerce')
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Extract user and message text
    users, msg_texts = [], []
    for msg in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', msg, maxsplit=1)
        if len(entry) > 1:
            users.append(entry[1])  # Extracted username
            msg_texts.append(entry[2])  # Message text
        else:
            users.append('group_notification')
            msg_texts.append(entry[0])  # System messages or media files

    df['user'] = users
    df['message'] = msg_texts
    df.drop(columns=['user_message'], inplace=True)

    # Extracting date and time components
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Creating a "period" column for hour ranges
    df['period'] = df['hour'].apply(lambda h: f"{h:02d}-{(h+1)%24:02d}")

    return df
