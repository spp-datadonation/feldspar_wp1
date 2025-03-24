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


def extract_subscriptions(subscriptions_csv, locale):
    """Extract YouTube channel subscriptions"""

    # Define column name based on detected language
    if "Kanaltitel" in subscriptions_csv.columns:
        channel_column = "Kanaltitel"
    else:
        channel_column = "Channel title"  # English version

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
