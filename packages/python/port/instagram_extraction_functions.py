from port.api.assets import *
from port.api.props import Translatable
import pandas as pd
from datetime import datetime, timezone, timedelta
import re

############################
# Helper functions for extraction
############################


# convert timespamp
def epoch_to_date(epoch_timestamp: str | int) -> str:
    """
    Convert epoch timestamp to an ISO 8601 string. Assumes UTC +1

    If timestamp cannot be converted raise CannotConvertEpochTimestamp
    """

    try:
        epoch_timestamp = int(epoch_timestamp)
        out = datetime.fromtimestamp(
            epoch_timestamp, tz=timezone(timedelta(hours=1))
        ).isoformat()  # timezone = utc + 1

    except:
        # fake date if unable to convert
        out = "01-01-1999"

    out = pd.to_datetime(out)
    return out.date().strftime(
        "%d-%m-%Y"
    )  # convertion to string for display in browser


# translate outputs
def translate(value, locale, dummy_decider=None):
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
        elif dummy_decider in [False, "False", None]:
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
# Extraction functions
############################


def extract_ads_viewed(ads_viewed_dict, locale):
    """extract ads_information/ads_and_topics/ads_viewed -> list of authors per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {"en": "Seen accounts", "de": "Gesehene Konten", "nl": "Geziene accounts"},
        locale,
    )

    timestamps = [
        t["string_map_data"]["Time"]["timestamp"]
        for t in ads_viewed_dict["impressions_history_ads_seen"]
    ]  # get list with timestamps in epoch format (if author exists)
    dates = [epoch_to_date(t) for t in timestamps]  # convert epochs to dates
    authors = [
        i["string_map_data"]["Author"]["value"]
        if "Author" in i["string_map_data"]
        else translate(
            {
                "en": "Unknown account",
                "de": "Unbekanntes Konto",
                "nl": "Onbekend account",
            },
            locale,
        )
        for i in ads_viewed_dict["impressions_history_ads_seen"]
    ]  # not for all viewed ads there is an author!

    adds_viewed_df = pd.DataFrame({tl_date: dates, tl_value: authors})

    aggregated_df = adds_viewed_df.groupby(tl_date)[tl_value].agg(list).reset_index()

    return aggregated_df


def extract_ads_clicked(ads_clicked_dict, locale):
    """extract ads_information/ads_and_topics/ads_clicked -> list of product names per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {"en": "Clicked ad", "de": "Angeklickte Werbung", "nl": "Geklikte advertentie"},
        locale,
    )

    timestamps = [
        t["string_list_data"][0]["timestamp"]
        for t in ads_clicked_dict["impressions_history_ads_clicked"]
    ]  # get list with timestamps in epoch format
    dates = [epoch_to_date(t) for t in timestamps]  # convert epochs to dates
    products = [i["title"] for i in ads_clicked_dict["impressions_history_ads_clicked"]]

    adds_clicked_df = pd.DataFrame({tl_date: dates, tl_value: products})

    aggregated_df = adds_clicked_df.groupby(tl_date)[tl_value].agg(list).reset_index()

    return aggregated_df


def extract_recently_viewed_items(recently_viewed_items_dict, locale):
    """extract your_instagram_activity/shopping/recently_viewed_items -> list of items"""

    tl_value = translate(
        {
            "en": "Recently viewed items",
            "de": "Kürzlich gesehene Einkaufsartikel",
            "nl": "Recent bekeken items",
        },
        locale,
    )

    items = recently_viewed_items_dict["checkout_saved_recently_viewed_products"]
    products = [p["string_map_data"]["Product Name"]["value"] for p in items]

    products_df = pd.DataFrame(products, columns=[tl_value])

    return products_df


def extract_posts_viewed(posts_viewed_dict, locale):
    """extract ads_information/ads_and_topics/posts_viewed -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of viewed posts",
            "de": "Anzahl der gesehenen Posts",
            "nl": "Aantal bekeken berichten",
        },
        locale,
    )

    timestamps = [
        t["string_map_data"]["Time"]["timestamp"]
        for t in posts_viewed_dict["impressions_history_posts_seen"]
    ]  # get list with timestamps in epoch format
    dates = [epoch_to_date(t) for t in timestamps]  # convert epochs to dates
    postViewedDates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = postViewedDates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_videos_watched(videos_watched_dict, locale):
    """extract ads_information/ads_and_topics/videos_watched -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of viewed videos",
            "de": "Anzahl der gesehenen Videos",
            "nl": "Aantal bekeken video's",
        },
        locale,
    )

    timestamps = [
        t["string_map_data"]["Time"]["timestamp"]
        for t in videos_watched_dict["impressions_history_videos_watched"]
    ]  # get list with timestamps in epoch format
    dates = [epoch_to_date(t) for t in timestamps]  # convert epochs to dates
    videosViewedDates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = videosViewedDates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_subscription_for_no_ads(subscription_for_no_ads_dict, locale):
    """extract ads_information/instagram_ads_and_businesses/subscription_for_no_ads -> dummy whether user has such a subscription"""

    tl_value = translate(
        {
            "en": "Subscription for no ads",
            "de": "Abo-Option für Werbefreiheit",
            "nl": "Abonnement zonder advertenties",
        },
        locale,
    )

    value = None

    if subscription_for_no_ads_dict["label_values"][0]["value"] == "Inaktiv":
        value = translate("dummy", locale, False)
    else:
        value = translate("dummy", locale, True)

    return pd.DataFrame([value], columns=[tl_value])


def extract_blocked_profiles(blocked_profiles_dict, locale):
    """extract connections/followers_and_following/blocked_accounts -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of blocked account",
            "de": "Anzahl blockierter Konten",
            "nl": "Aantal geblokkeerde accounts",
        },
        locale,
    )

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in blocked_profiles_dict["relationships_blocked_users"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_restricted_profiles(restricted_profiles_dict, locale):
    """extract connections/followers_and_following/restricted_accounts -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of restricted accounts",
            "de": "Anzahl der eingeschränkten Konten",
            "nl": "Aantal beperkte accounts",
        },
        locale,
    )

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in restricted_profiles_dict["relationships_restricted_users"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_post_comments_1(post_comments_1_dict, locale):
    """extract your_instagram_activity/comments/post_comments_1 -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of post comments",
            "de": "Anzahl der Post-Kommentare",
            "nl": "Aantal reacties op berichten",
        },
        locale,
    )

    # file can just be dict and not list if only one posted comment
    if isinstance(post_comments_1_dict, dict):
        dates = [
            epoch_to_date(post_comments_1_dict["string_map_data"]["Time"]["timestamp"])
        ]
    else:
        dates = [
            epoch_to_date(t["string_map_data"]["Time"]["timestamp"])
            for t in post_comments_1_dict
        ]  # get list with timestamps in epoch format

    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_reels_comments(reels_comments_dict, locale):
    """extract your_instagram_activity/comments/reels_comments -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of reel comments",
            "de": "Anzahl der Reel-Kommentare",
            "nl": "Aantal reacties op reels",
        },
        locale,
    )

    dates = [
        epoch_to_date(t["string_map_data"]["Time"]["timestamp"])
        for t in reels_comments_dict["comments_reels_comments"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_liked_posts(liked_posts_dict, locale):
    """extract your_instagram_activity/likes/liked_posts -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of liked posts",
            "de": 'Anzahl "geliker" Posts',
            "nl": "Aantal gelikete berichten",
        },
        locale,
    )

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in liked_posts_dict["likes_media_likes"]
    ]
    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_story_likes(story_likes_dict, locale):
    """extract your_instagram_activity/story_sticker_interactions/story_likes -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of liked stories",
            "de": 'Anzahl "gelikter" Stories',
            "nl": "Aantal gelikete stories ",
        },
        locale,
    )

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in story_likes_dict["story_activities_story_likes"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_liked_comments(liked_comments_dict, locale):
    """extract your_instagram_activity/likes/liked_comments -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of liked comments",
            "de": 'Anzahl "geliker" Kommentare',
            "nl": "Aantal gelikete reacties",
        },
        locale,
    )

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in liked_comments_dict["likes_comment_likes"]
    ]
    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_countdowns(countdowns_dict, locale):
    """extract your_instagram_activity/story_sticker_interactions/countdowns -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of reactions",
            "de": "Anzahl der Reaktionen",
            "nl": "Aantal reacties",
        },
        locale,
    )

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in countdowns_dict["story_activities_countdowns"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_emoji_sliders(emoji_sliders_dict, locale):
    """extract your_instagram_activity/story_sticker_interactions/emoji_sliders -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of reactions",
            "de": "Anzahl der Reaktionen",
            "nl": "Aantal reacties",
        },
        locale,
    )

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in emoji_sliders_dict["story_activities_emoji_sliders"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_polls(polls_dict, locale):
    """extract your_instagram_activity/story_sticker_interactions/polls -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of reactions",
            "de": "Anzahl der Reaktionen",
            "nl": "Aantal reacties",
        },
        locale,
    )

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in polls_dict["story_activities_polls"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_questions(questions_dict, locale):
    """extract your_instagram_activity/story_sticker_interactions/questions -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of reactions",
            "de": "Anzahl der Reaktionen",
            "nl": "Aantal reacties",
        },
        locale,
    )

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in questions_dict["story_activities_questions"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_quizzes(quizzes_dict, locale):
    """extract your_instagram_activity/story_sticker_interactions/quizzes -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of reactions",
            "de": "Anzahl der Reaktionen",
            "nl": "Aantal reacties",
        },
        locale,
    )

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in quizzes_dict["story_activities_quizzes"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_posts_1(posts_1_dict, locale):
    """extract your_instagram_activity/content/posts_1 -> count per day + info about location"""

    tl_value = translate(
        {
            "en": ["Date", "Linked location"],
            "de": ["Datum", "Verlikter Standort"],
            "nl": ["Datum", "Locatie leuk gevonden"],
        },
        locale,
    )

    results = []

    # file can just be dict and not list if only one post
    if isinstance(posts_1_dict, dict):
        for media in posts_1_dict.get("media", []):
            date = epoch_to_date(media.get("creation_timestamp", ""))
            has_latitude_data = any(
                "latitude" in exif_data
                for exif_data in media.get("media_metadata", {})
                .get("photo_metadata", {})
                .get("exif_data", [])
            )

            results.append(
                {
                    tl_value[0]: date,
                    tl_value[1]: translate("dummy", locale, has_latitude_data),
                }
            )

    else:
        for post in posts_1_dict:
            for media in post.get("media", []):
                date = epoch_to_date(media.get("creation_timestamp", ""))
                has_latitude_data = any(
                    "latitude" in exif_data
                    for exif_data in media.get("media_metadata", {})
                    .get("photo_metadata", {})
                    .get("exif_data", [])
                )

                results.append(
                    {
                        tl_value[0]: date,
                        tl_value[1]: translate("dummy", locale, has_latitude_data),
                    }
                )

    posts_df = pd.DataFrame(results)

    return posts_df


def extract_stories(stories_dict, locale):
    """extract your_instagram_activity/content/stories -> count per day + info about location"""

    tl_value = translate(
        {
            "en": ["Date", "Linked location"],
            "de": ["Datum", "Verlikter Standort"],
            "nl": ["Datum", "Locatie leuk gevonden"],
        },
        locale,
    )

    results = []

    for story in stories_dict.get("ig_stories", []):
        date = epoch_to_date(story.get("creation_timestamp", ""))
        has_latitude_data = any(
            "latitude" in exif_data
            for exif_data in story.get("media_metadata", {})
            .get("photo_metadata", {})
            .get("exif_data", [])
        )

        results.append(
            {
                tl_value[0]: date,
                tl_value[1]: translate("dummy", locale, has_latitude_data),
            }
        )

    stories_df = pd.DataFrame(results)

    return stories_df


def extract_reels(reels_dict, locale):
    """extract your_instagram_activity/content/reels -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {"en": "Count of reels", "de": "Anzahl der Reels", "nl": "Aantal reels"}, locale
    )

    dates = [
        epoch_to_date(media.get("creation_timestamp"))
        for reel in reels_dict.get("ig_reels_media", [])
        for media in reel.get("media", [])
    ]
    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_followers_1(followers_1_dict, locale):
    """extract connections/followers_and_following/followers_1 -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of followers",
            "de": "Anzahl der Follower",
            "nl": "Aantal volgers",
        },
        locale,
    )

    # file can just be dict and not list if only one follower
    if isinstance(followers_1_dict, dict):
        dates = [epoch_to_date(followers_1_dict["string_list_data"][0]["timestamp"])]
    else:
        dates = [
            epoch_to_date(t["string_list_data"][0]["timestamp"])
            for t in followers_1_dict
        ]

    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_instagram_profile_information(instagram_profile_information_dict, locale):
    """extract personal_information/personal_information/account_information -> dummy whether 'contact_syncing' is enabled"""

    tl_value = translate(
        {
            "en": "Contact syncing enabled",
            "de": "Kontaktsynchronisierung aktiviert",
            "nl": "Contact synchronisatie ingeschakeld",
        },
        locale,
    )

    value = None

    for k in [
        "Contact Syncing",
        "Kontaktsynchronisierung",
        "Synchronisation des contacts",
    ]:  # keys are language specific
        if (
            k
            in instagram_profile_information_dict["profile_account_insights"][0][
                "string_map_data"
            ]
        ):
            value = instagram_profile_information_dict["profile_account_insights"][0][
                "string_map_data"
            ][k]["value"]
            break

    return pd.DataFrame([translate("dummy", locale, value)], columns=[tl_value])


def extract_personal_information(personal_information_dict, locale):
    """
    extract personal_information/personal_information/personal_information.json -> dummies whether user has email, phone, and private account
    """

    tl_value = translate(
        {
            "en": [
                "Email",
                "Phone",
                "Private account",
            ],
            "de": [
                "Email",
                "Telefon",
                "Privates Konto",
            ],
            "nl": [
                "Email",
                "Telefoon",
                "Privé-account",
            ],
        },
        locale,
    )

    # check if information present
    email, phone, private_account = None, None, None

    for k in ["Email", "E-Mail-Adresse"]:  # keys are language specific
        if k in personal_information_dict["profile_user"][0]["string_map_data"]:
            email = (
                personal_information_dict["profile_user"][0]["string_map_data"][k][
                    "value"
                ]
                != "False"
            )
            break

    for k in [
        "Phone Confirmed",
        "Telefonnummer best\u00c3\u00a4tigt",
    ]:  # keys are language specific
        if k in personal_information_dict["profile_user"][0]["string_map_data"]:
            phone = (
                personal_information_dict["profile_user"][0]["string_map_data"][k][
                    "value"
                ]
                != "False"
            )
            break

    for k in ["Private Account", "Privates Konto"]:  # keys are language specific
        if k in personal_information_dict["profile_user"][0]["string_map_data"]:
            private_account = personal_information_dict["profile_user"][0][
                "string_map_data"
            ][k]["value"]
            break

    result = pd.DataFrame(
        {
            tl_value[0]: [translate("dummy", locale, email)],
            tl_value[1]: [translate("dummy", locale, phone)],
            tl_value[2]: [translate("dummy", locale, private_account)],
        }
    )

    return result


def extract_topics_df(topics_dict, locale):
    """extract preferences/your_topics -> list of topics"""

    tl_value = translate(
        {"en": "Your topics", "de": "Ihre Themen", "nl": "Uw onderwerpen"}, locale
    )
    topics_list = [
        t["string_map_data"]["Name"]["value"] for t in topics_dict["topics_your_topics"]
    ]
    topics_df = pd.DataFrame(topics_list, columns=[tl_value])

    return topics_df


def extract_login_activity(login_activity_dict, locale):
    """extract security_and_login_information/login_and_account_creation/login_activity -> time and user agent"""

    tl_date = translate("date", locale)
    tl_value1 = translate({"en": "Time", "de": "Uhrzeit", "nl": "Tijd"}, locale)
    tl_value2 = translate(
        {"en": "User agent", "de": "Gerät", "nl": "Gebruikersagent"}, locale
    )

    logins = login_activity_dict["account_history_login_history"]

    timestamps = [t["title"] for t in logins]
    dates = [str(datetime.fromisoformat(timestamp).date()) for timestamp in timestamps]
    times = [datetime.fromisoformat(timestamp).time() for timestamp in timestamps]

    user_agents = [t["string_map_data"]["User Agent"]["value"] for t in logins]

    login_df = pd.DataFrame({tl_date: dates, tl_value1: times, tl_value2: user_agents})

    return login_df


def extract_logout_activity(logout_activity_dict, locale):
    """extract security_and_login_information/login_and_account_creation/logout_activity -> time and user agent"""

    tl_date = translate("date", locale)
    tl_value1 = translate({"en": "Time", "de": "Uhrzeit", "nl": "Tijd"}, locale)
    tl_value2 = translate(
        {"en": "User agent", "de": "Gerät", "nl": "Gebruikersagent"}, locale
    )

    logouts = logout_activity_dict["account_history_logout_history"]

    timestamps = [t["title"] for t in logouts]
    dates = [str(datetime.fromisoformat(timestamp).date()) for timestamp in timestamps]
    times = [datetime.fromisoformat(timestamp).time() for timestamp in timestamps]

    user_agents = [t["string_map_data"]["User Agent"]["value"] for t in logouts]

    logout_df = pd.DataFrame({tl_date: dates, tl_value1: times, tl_value2: user_agents})

    return logout_df
