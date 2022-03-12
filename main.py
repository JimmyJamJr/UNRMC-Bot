import discord
from discord.ext import commands
import datetime
import pytz
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dateutil.parser import parse

DAYS_OF_WEEK = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]

description = ""
command_prefixes = ("mc!", "MC!", "mc.", "MC.")
bot = commands.Bot(command_prefix=command_prefixes, description=description)

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

curr_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(curr_dir)

"""Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('calendar', 'v3', credentials=creds)


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command(name="debug")
async def debug(ctx):
    await ctx.send("Carl is the most attractive tutor at the math center.")

@bot.command(name="review", aliases=["r", "reviews", "reviewsessions", "rs", "RS", "Rs", "R", "Reviews", "Review"])
async def reviews(ctx, options : str):
    review_list = []

    if is_date(options):
        date = parse(options, fuzzy=False)
        date_end = date + datetime.timedelta(days=1)

        tz = pytz.timezone('US/Pacific')
        date_start = date.replace(tzinfo=tz).isoformat()
        date_end = date_end.replace(tzinfo=tz).isoformat()
        events_result = service.events().list(calendarId='2baddttpsiaa3l9ind6i7hqr78@group.calendar.google.com', timeMin = date_start,
                                              timeMax=date_end,
                                              maxResults=30, singleEvents=True,
                                              timeZone='US/Pacific',
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print("There are no reviews on " + date.strftime("%m/%d/%Y"))
        for event in events:
            if "Exam" in event['summary']:
                review_list.append(event)

        if len(review_list) == 0:
            print("There are no reviews on " + date.strftime("%m/%d/%Y"))
            await ctx.send("There are no reviews on " + date.strftime("%m/%d/%Y") + ".")
        else:
            await ctx.send("Reviews on **" + date.strftime("%m/%d/%Y (%a)") + "**:")
            for event in review_list:
                time = parse(event['start']['dateTime']).strftime("%I:%M %p")
                info = event['summary'].split(":")
                tutor = info[1].strip()
                review = info[0].split("-")

                label = review[0]
                professor = review[1]
                section = review[2]
                exam = review[3]

                await ctx.send("**📚 " + tutor + "**: " + time + " - " + label + " " + professor + " " + section + " " + exam + ".")

    else:
        date = datetime.datetime.today()
        date_end = date + datetime.timedelta(days=28)

        tz = pytz.timezone('US/Pacific')
        date_start = date.replace(tzinfo=tz).isoformat()
        date_end = date_end.replace(tzinfo=tz).isoformat()
        events_result = service.events().list(calendarId='2baddttpsiaa3l9ind6i7hqr78@group.calendar.google.com', timeMin = date_start,
                                              timeMax=date_end,
                                              maxResults=100, singleEvents=True,
                                              timeZone='US/Pacific',
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        for event in events:
            if options.upper() in event['summary'].upper():
                review_list.append(event)

        if len(review_list) == 0:
            print("There are no reviews for **" + options.title() + "** in the next 28 days.")
            await ctx.send("There are no reviews for **" + options.title() + "** in the next 28 days.")
        else:
            await ctx.send("**" + options.title() + "** has the following upcoming reviews:")
            for event in review_list:
                time = parse(event['start']['dateTime']).strftime("%m/%d/%Y (%a) %I:%M %p")
                info = event['summary'].split(":")
                tutor = info[1].strip()
                review = info[0].split("-")

                label = review[0]
                professor = review[1]
                section = review[2]
                exam = review[3]

                await ctx.send("**📚 " + time + "** - " + label + " " + professor + " " + section + " " + exam + ".")

bot.run('OTAzMDEzMTUzMTIwNjEyMzgy.YXmyiA.KCxWL1spduCzxx8kZlH4kLOUF2k')

