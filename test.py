import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

# response = requests.get(
#     "https://ipv4.webshare.io/",
#     proxies={
#         "http": "http://jpovzjzy:yasrdx3ydzsl@142.147.128.93:6593/",
#         "https": "http://jpovzjzy:yasrdx3ydzsl@142.147.128.93:6593/",
#     },
# ).text
#
# print(response)
#

###################################
ytt_api = YouTubeTranscriptApi(
    proxy_config=WebshareProxyConfig(
        proxy_username="jpovzjzy",
        proxy_password="yasrdx3ydzsl",
    )
)
# ytt_api = YouTubeTranscriptApi()
fetched_transcript = ytt_api.fetch("Dv3RRAx7G6E")

# is iterable
for snippet in fetched_transcript:
    print(snippet.text)

# indexable
last_snippet = fetched_transcript[-1]

# provides a length
snippet_count = len(fetched_transcript)

#################################

# from langchain_community.document_loaders import YoutubeLoader
#
# loader = YoutubeLoader.from_youtube_url(
#     "https://www.youtube.com/watch?v=Dv3RRAx7G6E", add_video_info=False
# )
# print(loader.load())
