from dotenv import load_dotenv
import os

load_dotenv()

COMMAND_SIGN = os.environ.get("COMMAND_SIGN")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
AWS_TABLE = os.environ.get("AWS_TABLE")

TEXT_CHANNEL = "clout-net"