# 🤖 Developer Quote Instagram/Twitter Bot

This is a Instagram/Twitter bot that generates and posts/tweets developer quotes along with an image based on the description provided by the quote.

## 🚀 Technologies Used

- [OpenAI API](https://openai.com/)
- [Twitter](https://developer.twitter.com/en/docs/twitter-api)
- [Instagram](https://developers.facebook.com/docs/instagram-api)
- [Google Cloud Functions](https://cloud.google.com/functions)
- [Google Cloud Scheduler](https://cloud.google.com/scheduler)
- [Google Cloud Pub/Sub](https://cloud.google.com/pubsub)
- [Google Cloud Storage](https://cloud.google.com/storage)
- [MongoDB](https://www.mongodb.com/products/platform/cloud)
- [Python](https://www.python.org/)

## 📋 Prerequisites

- Python 3.6 or higher
- A Instagram business account
- A Meta account
- A Meta page linked to Instagram business account
- A Twitter Developer account with API keys and access tokens
- An OpenAI API key
- A MongoDB database

## 🛠️ Setup

To set up this project locally, you will need to:

1. Clone this repository: `git clone https://github.com/monproweb/dev-wisdom-daily.git`
2. Install the required packages using pip: `pip install -r requirements.txt`
3. Set the necessary environment variables:
   - `TWITTER_API_KEY` (Follow the [official documentation](https://developer.twitter.com/en/docs/authentication/oauth-1-0a) to create a Twitter Developer account and obtain API keys and access tokens)
   - `TWITTER_API_SECRET`
   - `TWITTER_ACCESS_TOKEN`
   - `TWITTER_ACCESS_TOKEN_SECRET`
   - `BEARER_TOKEN`
   - `OPENAI_API_KEY` (Follow the [official documentation](https://platform.openai.com/docs/quickstart) to obtain an OpenAI API key)
   - `TWITTER_ACCOUNT` (Set this to the username of the Twitter account you want to use for posting the tweets, e.g., "@DevWisdomDaily")
   - `MONGODB_USERNAME`
   - `MONGODB_PASSWORD`
   - `FACEBOOK_ACCESS_TOKEN`
   - `INSTAGRAM_USER_ID`
   - `GOOGLE_APPLICATION_CREDENTIALS`
4. Deploy the function to Google Cloud Functions using the following command:

    ```shell
    gcloud functions deploy trigger_tweet \
    --runtime python311 \
    --trigger-resource devwisdomdaily_tweet \
    --trigger-event google.pubsub.topic.publish \
    --entry-point trigger_tweet \
    --env-vars-file .env.json
    ```
5. Create a topic in Google Cloud Pub/Sub
6. Create a subscription for the topic
7. Create a Cloud Scheduler job to trigger the function with a Pub/Sub target

## 🎯 Usage

Once the project is set up, the bot will automatically tweet/post a new developer quote with an image at the specified intervals set up in the Cloud Scheduler job.

## 🤝 Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue. If you want to contribute code, please fork the repository and create a pull request.

## 🌟 Contributors

- [FastFingertips](https://github.com/FastFingertips)

## 📝 TODO

Threads with official Graph API

## 📄 License

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).
