from datetime import datetime

from pymongo import MongoClient


class Mongo:
    def __init__(
        self,
        host="localhost",
        user="root",
        password="example",
        database="manifestacoes",
        port=27017,
    ):
        uri = f"mongodb://{user}:{password}@{host}:{port}/"
        self.db = MongoClient(uri)[database]

    @property
    def tweets(self):
        tweets = self.db.tweets.find()
        yield from (self.serialize(tweet) for tweet in tweets)

    @property
    def first_tweet(self):
        tweet = self.db.tweets.find_one()
        return self.serialize(tweet)

    @staticmethod
    def serialize(tweet):
        keys = (
            "created_at",
            "id_str",
            "text",
            "source",
            "in_reply_to_status_id_str",
            "in_reply_to_user_id_str",
            "in_reply_to_screen_name",
            "quote_count",
            "reply_count",
            "retweet_count",
            "favorite_count",
            "lang",
        )
        data = {key: tweet.get(key) for key in keys}

        # Convert date/time to Rows format
        twitter = "%a %b %d %H:%M:%S %z %Y"
        rows = "%Y-%m-%d %H:%M:%S"
        if data.get("created_at"):
            data["created_at"] = datetime.strptime(
                data["created_at"], twitter
            ).strftime(rows)

        user_keys = (
            "id_str",
            "name",
            "screen_name",
            "location",
            "description",
            "verified",
            "followers_count",
            "friends_count",
            "listed_count",
            "statuses_count",
            "created_at",
            "default_profile",
            "default_profile_image",
        )
        data.update(
            {f"user_{key}": tweet.get("user", {}).get(key) for key in user_keys}
        )

        quoted_status_keys = ("id_str", "created_at")
        data.update(
            {
                f"quoted_status_{key}": tweet.get("quoted_status", {}).get(key)
                for key in quoted_status_keys
            }
        )

        quoted_status_user_keys = ("id_str", "screen_name")
        data.update(
            {
                f"quoted_status_user_{key}": (
                    tweet.get("quoted_status", {}).get("user", {}).get(key)
                )
                for key in quoted_status_user_keys
            }
        )

        return data
