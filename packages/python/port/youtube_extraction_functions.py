from port.api.assets import *
from port.api.props import Translatable
import pandas as pd
from datetime import datetime, timezone, timedelta
import re
import json

############################
# Helper functions for extraction
############################


def translate(value, locale, dummy_decider=None):
    """Translate outputs"""
    if value == "date":
        translatedMessage = Translatable(
            {
                "en": "Date",
                "de": "Datum",
                "nl": "Datum",
            }
        )
        return translatedMessage.translations[locale]

    if value == "dummy":
        if dummy_decider in [True, "True"]:
            translatedMessage = Translatable(
                {
                    "en": "Yes",
                    "de": "Ja",
                    "nl": "Ja",
                }
            )
        elif dummy_decider in [False, "False"]:
            translatedMessage = Translatable(
                {
                    "en": "No",
                    "de": "Nein",
                    "nl": "Nee",
                }
            )
        else:
            translatedMessage = Translatable(
                {
                    "en": str(dummy_decider),
                    "de": str(dummy_decider),
                    "nl": str(dummy_decider),
                }
            )
        return translatedMessage.translations[locale]

    else:
        translatedMessage = Translatable(value)
        return translatedMessage.translations[locale]


############################
# Extraction functions for YouTube data
############################


def extract_watch_history(watch_history_json, locale):
    """Extract YouTube watch history"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Number of videos watched",
            "de": "Anzahl der gesehenen Videos",
            "nl": "Aantal bekeken video's",
        },
        locale,
    )

    # Initialize list to store dates
    dates = []

    # Process each entry in the watch history
    for entry in watch_history_json:
        if "time" in entry and "titleUrl" in entry:  # Make sure it's a video entry
            # Extract date (YYYY-MM-DD) from ISO timestamp
            date_str = entry["time"].split("T")[0]
            dates.append(date_str)

    # Create DataFrame with dates
    dates_df = pd.DataFrame(dates, columns=[tl_date])

    # Aggregate by date to count videos watched per day
    aggregated_df = dates_df.groupby(tl_date).size().reset_index(name=tl_value)

    return aggregated_df


def extract_comments(comments_csv, locale):
    """Extract YouTube comment history and count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Number of comments",
            "de": "Anzahl der Kommentare",
            "nl": "Aantal reacties",
        },
        locale,
    )

    # Find the date column
    date_column = None
    for possible_column in [
        "Zeitstempel der Erstellung des Kommentars",
        "Comment Create Timestamp",
    ]:  # language sensitive
        if possible_column in comments_csv.columns:
            date_column = possible_column
            break

    if date_column is None:
        return pd.DataFrame(
            {
                tl_date: ["N/A"],
                tl_value: [f"Total comments: {len(comments_csv)}"],
            }
        )

    # Convert dates to a consistent format
    comments_csv[date_column] = pd.to_datetime(
        comments_csv[date_column], errors="coerce"
    )
    # Extract just the date portion (without time)
    comments_csv["formatted_date"] = comments_csv[date_column].dt.strftime("%Y-%m-%d")

    # Remove entries with NaT values
    comments_csv = comments_csv.dropna(subset=["formatted_date"])

    # Count comments per day
    daily_counts = (
        comments_csv.groupby("formatted_date").size().reset_index(name=tl_value)
    )
    daily_counts.rename(columns={"formatted_date": tl_date}, inplace=True)

    return daily_counts


def extract_subscriptions(subscriptions_csv, locale):
    """Extract YouTube channel subscriptions"""

    # Define column name
    if "Kanaltitel" in subscriptions_csv.columns:  # language sensitive
        channel_column = "Kanaltitel"
    else:
        channel_column = "Channel Title"

    tl_channel = translate(
        {
            "en": "Subscribed Channel",
            "de": "Abonnierter Kanal",
            "nl": "Geabonneerd kanaal",
        },
        locale,
    )

    # Create DataFrame with just the channel names
    subscriptions_df = pd.DataFrame({tl_channel: subscriptions_csv[channel_column]})

    return subscriptions_df


def extract_search_history(search_history_json, locale):
    """Extract YouTube search history and count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Number of searches",
            "de": "Anzahl der Suchen",
            "nl": "Aantal zoekopdrachten",
        },
        locale,
    )

    # Initialize list to store dates
    dates = []

    # Process each entry in the search history
    for entry in search_history_json:
        if "time" in entry:  # Make sure it has a timestamp
            # Extract date (YYYY-MM-DD) from ISO timestamp
            date_str = entry["time"].split("T")[0]
            dates.append(date_str)

    if not dates:
        return pd.DataFrame(
            {
                tl_date: ["N/A"],
                tl_value: ["No valid search dates found"],
            }
        )

    # Create DataFrame with dates
    dates_df = pd.DataFrame(dates, columns=[tl_date])

    # Aggregate by date to count searches per day
    aggregated_df = dates_df.groupby(tl_date).size().reset_index(name=tl_value)

    return aggregated_df
