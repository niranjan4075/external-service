import os
from dotenv import load_dotenv
load_dotenv()

class DbCred:
    user=os.getenv("user")
    password=os.getenv("password")
    host=os.getenv("host")
    port= os.getenv("port")
    db_name=os.getenv("db_name")
    db_url=f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


class SlackCred:
    slack_token=os.getenv("SLACK_BOT_TOKEN")
    slack_url=os.getenv("slack_url")
    channel_name=os.getenv("channel_name")
    slack_app_token=os.getenv("slack_app_token")