import feedparser
import openai
import requests
from bs4 import BeautifulSoup

# Parse the RSS feed for the Azure blog
NewsFeed = feedparser.parse("https://azure.microsoft.com/en-us/blog/feed/")

# Get the second entry in the feed (most recent post)
entry = NewsFeed.entries[1]

# Set up OpenAI API credentials
openai.api_type = "azure"
openai.api_key = "YOUR_API_KEY"
openai.api_base = "https://YOUR_DEPLOYMENT_ID.openai.azure.com/"
openai.api_version = "2023-09-15-preview"

# Define function to get the latest news from the blog
def get_latest_news():
    url = entry.link
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="main")
    news_elems = results.find_all("p")
    news = ""
    for news_elem in news_elems:
        news += news_elem.text + " "
    return news

# Get the latest news and format it for input to the GPT-35-turbo API
news = get_latest_news()
prompt = "Summarise the following article into 50 words and formatted as a paragraph: " + " ".join(news) + "50 word summary in a paragraph:"

# Call the GPT-35-turbo API to summarize the news
chat_completion = openai.Completion.create(
    deployment_id="YOUR_DEPLOYMENT_ID", 
    model="YOUR_MODEL_NAME",
    prompt=prompt,
    max_tokens=100,
    temperature=0.7,
    top_p=1,
    frequency_penalty=0.5,
    presence_penalty=0.5,
    stop=["\n\n"]
)

# Print the summary to the console
print(chat_completion.choices[0].text)
