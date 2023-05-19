def positive_news():
    import pandas as pd
    import json 
    import requests
    import re
    from bs4 import BeautifulSoup
    import nltk
    nltk.download('vader_lexicon')
    from nltk.sentiment import SentimentIntensityAnalyzer
    from datetime import datetime, timedelta
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    def extract_date(text):
        pattern = r'Last Updated : (\w+)\s(\d+)\s(\d{4})'
        match = re.search(pattern, text)
        if match:
            day = match.group(2)
            month = match.group(1)
            year = match.group(3)
            month_mapping = {'January': '01','February': '02','March': '03','April': '04','May': '05','June': '06',
                             'July': '07','August': '08','September': '09','October': '10','November': '11','December': '12'}
            if month in month_mapping:
                month = month_mapping[month]
            date = f"{day}/{month}/{year}"
            return date
        else:
            return None
    def extract_time(text):
        pattern = r'\| (\d+:\d+ [APM]{2})'
        match = re.search(pattern, text)
        if match:
            time_str = match.group(1)
            return time_str
        else:
            return None

    current_date = datetime.now().date()
    previous_date = current_date - timedelta(days=1)

    def analyze_sentiment(text):
        sid = SentimentIntensityAnalyzer()
        sentiment_scores = sid.polarity_scores(text)
        return sentiment_scores['compound']

    dfs = []  # List to store individual DataFrames

    for i in range(1,5):
        url = f'https://www.business-standard.com/amp/markets-news/page-{i}'
        res = requests.get(url)
        soup = BeautifulSoup(res.content, features="html.parser")
        elements = soup.find_all('p', {"class": "jsx-5e3ce470021cdb2 listing__title color-gray my-12 font-merriweather-bold"})
        news_list = []
        unclean_date = []
        time_list = []
        for element in elements:
            next_sibling = element.next_sibling
            news_list.append(next_sibling.text)
        for d in soup.find_all('span', {"class": "jsx-ac030cb10580a41f"}):
            unclean_date.append(extract_date(d.text))
            time_list.append(extract_time(d.text))

        script_tag = soup.find_all("script")[19]
        json_data = json.loads(script_tag.string)

        urls = [item["url"] for item in json_data["itemListElement"]]

        df_temp = pd.DataFrame({"news": news_list, "date": unclean_date, "Time": time_list, "Url": urls})
        dfs.append(df_temp)

    df = pd.concat(dfs, ignore_index=True)
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    df['Sentiment Score'] = df['news'].apply(analyze_sentiment)


    filtered_df = df.loc[(df['date'] <= pd.to_datetime(current_date)) & (df['date'] >= pd.to_datetime(previous_date)) & (df['Sentiment Score'] > 0.5)]
    sender_email = "karan.ahirwar1996@gmail.com"
    receiver_email = ["anitaahirwar2112@gmail.com", sender_email]
    password = "uccrgtqdnusrpmnk"
    table_html = filtered_df.to_html(index=False)

    # Create the email message
    msg = MIMEMultipart()
    
    positive_news_count = len(filtered_df)
    msg["Subject"] = f"✨ Daily Positive News Digest - {current_date} ({positive_news_count} uplifting articles out of {len(df)})✨"

    msg["From"] = sender_email
    msg["To"] = ", ".join(receiver_email)

    # HTML Template for the email content
    html_template = """
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
        }}
        h1 {{
            color: #336699;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        th, td {{
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f2f2f2;
        }}
    </style>
</head>
<body>
    <h1>Positive News - {current_date}</h1>
    {table}
</body>
</html>
"""


    # Set the message content with HTML template and table
    email_content = html_template.format(current_date=current_date, table=table_html)
    message = MIMEText(email_content, 'html')
    msg.attach(message)
    
    # Send the email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

    return filtered_df
positive_news()
