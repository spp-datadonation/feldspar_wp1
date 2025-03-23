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


# split name at whitespace, dot, or underscore
def split_name(name):
    parts = re.split(r"[\s._]+", name)
    parts = [part.strip() for part in parts if part.strip()]
    return parts


# check if names in file
def check_name(names_to_check):
    # read the vornamen.txt file into names_set
    names_set = read_asset("vornamen.txt")

    # check if any name in names_to_check matches the names in the file
    for name in names_to_check:
        if name in names_set:
            return True

    return False


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
        elif dummy_decider == "picture_not_analyzed":
            translatedMessage = Translatable(
                {
                    "en": "Not analyzed",
                    "de": "Nicht analysiert",
                    "nl": "Niet geanalyseerd",
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


def get_postViewsPerDay(posts_viewed_dict, locale):
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


def get_videoViewsPerDay(videos_watched_dict, locale):
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


def extract_blocked_accounts(blocked_accounts_dict, locale):
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
        for t in blocked_accounts_dict["relationships_blocked_users"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_close_friends(close_friends_dict, locale):
    """extract connections/followers_and_following/close_friends -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of close friends",
            "de": 'Anzahl "enger Freunde"',
            "nl": "Aantal beste vrienden",
        },
        locale,
    )

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in close_friends_dict["relationships_close_friends"]
    ]  # get list with timestamps in epoch format
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


def extract_following(following_dict, locale):
    """extract connections/followers_and_following/following -> count"""

    tl_value = translate(
        {
            "en": "Count of followed accounts",
            "de": "Anzahl gefolger Konten",
            "nl": "Aantal gevolgde accounts",
        },
        locale,
    )

    if following_dict is None:
        count = 0
    else:
        following = [
            f for f in following_dict["relationships_following"]
        ]  # get count of following
        count = len(following)

    return pd.DataFrame([count], columns=[tl_value])


def extract_follow_requests_youve_received(follow_requests_youve_received_dict, locale):
    """extract connections/followers_and_following/follow_requests_you've_received_dict -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of received follow requests",
            "de": "Anzahl der Followeranfragen",
            "nl": "Aantal ontvangen volgverzoeken",
        },
        locale,
    )

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in follow_requests_youve_received_dict[
            "relationships_follow_requests_received"
        ]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_hide_story_from(hide_story_from_dict, locale):
    """extract connections/followers_and_following/hide_story_from -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of hidden stories",
            "de": "Anzahl der versteckten Stories",
            "nl": "Aantal verborgen verhalen",
        },
        locale,
    )

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in hide_story_from_dict["relationships_hide_stories_from"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_pending_follow_requests(pending_follow_requests_dict, locale):
    """extract connections/followers_and_following/pending_follow_requests -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of pending follow requests",
            "de": "Anzahl ignorierter Followeranfragen",
            "nl": "Aantal wachtende volggrequests",
        },
        locale,
    )

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in pending_follow_requests_dict["relationships_follow_requests_sent"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_recently_unfollowed_accounts(recently_unfollowed_accounts_dict, locale):
    """extract connections/followers_and_following/recently_unfollowed_accounts -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of recently unfollowed accounts",
            "de": "Anzahl der entfolgten Konten",
            "nl": "Aantal recent ontvolgde accounts",
        },
        locale,
    )

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in recently_unfollowed_accounts_dict["relationships_unfollowed_users"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_removed_suggestions(removed_suggestions_dict, locale):
    """extract connections/followers_and_following/removed_suggestions -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of removed suggestions",
            "de": "Anzahl der entfernten Vorschläge",
            "nl": "Aantal verwijderde suggesties",
        },
        locale,
    )

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in removed_suggestions_dict["relationships_dismissed_suggested_users"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_restricted_accounts(restricted_accounts_dict, locale):
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
        for t in restricted_accounts_dict["relationships_restricted_users"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_notification_of_privacy_policy_updates(
    notification_of_privacy_policy_updates_dict, locale
):
    """extract logged_information/policy_updates_and_permissions/notification_of_privacy_policy_updates -> day and value"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Consent status",
            "de": "Status der Einwilligung",
            "nl": "Toestemmingsstatus",
        },
        locale,
    )

    # extract and preprocess dates
    dates = [
        d["string_map_data"]["Impression Time"]["value"]
        for d in notification_of_privacy_policy_updates_dict[
            "policy_updates_and_permissions_notification_of_privacy_policy_updates"
        ]
    ]
    dates = [datetime.strptime(d, "%b %d, %Y %I:%M:%S%p") for d in dates]
    dates = [
        d.strftime("%d-%m-%Y") for d in dates
    ]  # use same format as in other tables

    consent_statuses = [
        v["string_map_data"]["Consent Status"]["value"]
        for v in notification_of_privacy_policy_updates_dict[
            "policy_updates_and_permissions_notification_of_privacy_policy_updates"
        ]
    ]

    result = pd.DataFrame({tl_date: dates, tl_value: consent_statuses})

    return result


def extract_account_information(account_information_dict, locale):
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
            in account_information_dict["profile_account_insights"][0][
                "string_map_data"
            ]
        ):
            value = account_information_dict["profile_account_insights"][0][
                "string_map_data"
            ][k]["value"]
            break

    return pd.DataFrame([translate("dummy", locale, value)], columns=[tl_value])


def extract_linked_meta_accounts(linked_meta_accounts_dict, locale):
    """extract personal_information/personal_information/linked_meta_accounts -> list of connected accounts"""

    tl_value1 = translate(
        {
            "en": "Connected accounts",
            "de": "Verbundene Konten",
            "nl": "Gekoppelde accounts",
        },
        locale,
    )
    tl_value2 = translate({"en": "None", "de": "Keine", "nl": "Geen"}, locale)

    accounts = []

    for a in linked_meta_accounts_dict["label_values"]:
        if "dict" in a and a["dict"]:
            account_name = a["title"]
            accounts.append(account_name)

    if not accounts:
        accounts = tl_value2

    accounts_df = pd.DataFrame({tl_value1: accounts})

    return accounts_df


def extract_personal_information(personal_information_dict, locale):
    """
    extract personal_information/personal_information/personal_information.json -> dummies whether user has profile image, email, phone, and private account
    + extract whether used name is real name if compared against list of names ("vornamen.txt")
    """

    tl_value = translate(
        {
            "en": [
                "Profile image",
                "Email",
                "Phone",
                "Private account",
                "Real name in profile",
            ],
            "de": [
                "Profilbild",
                "Email",
                "Telefon",
                "Privates Konto",
                "Echter Name im Profil",
            ],
            "nl": [
                "Profielafbeelding",
                "Email",
                "Telefoon",
                "Privé-account",
                "Echte naam in profiel",
            ],
        },
        locale,
    )

    # check if information present
    profile_image, email, phone, private_account = None, None, None, None

    for k in ["Profile Photo", "Profilbild"]:  # keys are language specific
        if k in personal_information_dict["profile_user"][0]["media_map_data"]:
            profile_image = (
                personal_information_dict["profile_user"][0]["media_map_data"][k]["uri"]
                != "False"
            )
            break

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

    # check if real name used in profile

    name_to_check = None
    real_name = False

    for k in ["Name"]:  # keys are language specific
        if k in personal_information_dict["profile_user"][0]["string_map_data"]:
            name_to_check = personal_information_dict["profile_user"][0][
                "string_map_data"
            ][k]["value"]
            break

    # split names to check
    names_to_check = split_name(name_to_check)

    # check if name in list of names
    real_name = check_name(names_to_check)

    result = pd.DataFrame(
        {
            tl_value[0]: [translate("dummy", locale, profile_image)],
            tl_value[1]: [translate("dummy", locale, email)],
            tl_value[2]: [translate("dummy", locale, phone)],
            tl_value[3]: [translate("dummy", locale, private_account)],
            tl_value[4]: [translate("dummy", locale, real_name)],
        }
    )

    return result


def extract_profile_changes(profile_changes_dict, locale):
    """extract personal_information/personal_information/profile_changes -> day and what was changed"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Type of chage made",
            "de": "Art der Änderung",
            "nl": "Soort wijziging gemaakt",
        },
        locale,
    )

    changed_dates, changed_values = None, None

    changes = [
        t["string_map_data"] for t in profile_changes_dict["profile_profile_change"]
    ]

    for k in ["Changed", "Ge\u00c3\u00a4ndert"]:  # keys are language specific
        if any(k in d for d in changes):
            changed_values = [t[k]["value"] for t in changes]
            break

    for k in ["Change Date", "Datum \u00c3\u00a4ndern"]:  # keys are language specific
        if any(k in d for d in changes):
            changed_dates = [epoch_to_date(t[k]["timestamp"]) for t in changes]
            break

    changes_df = pd.DataFrame({tl_date: changed_dates, tl_value: changed_values})

    return changes_df


def extract_comments_allowed_from(comments_allowed_from_dict, locale):
    """extract preferences/media_settings/comments_allowed_from -> value"""

    tl_value = translate(
        {"en": "Restrictions", "de": "Einschräkungen", "nl": "Beperkingen"}, locale
    )

    value = None

    for k in [
        "Comments Allowed From",
        "Kommentieren gestattet f\u00c3\u00bcr",
    ]:  # keys are language specific
        if (
            k
            in comments_allowed_from_dict["settings_allow_comments_from"][0][
                "string_map_data"
            ]
        ):
            value = comments_allowed_from_dict["settings_allow_comments_from"][0][
                "string_map_data"
            ][k]["value"]
            break

    return pd.DataFrame([value], columns=[tl_value])


def extract_comments_blocked_from(comments_blocked_from_dict, locale):
    """extract preferences/media_settings/comments_blocked_from -> count"""

    tl_value = translate(
        {
            "en": "Count of blocked accounts",
            "de": "Anzahl blockierter Konten",
            "nl": "Aantal geblokkeerde accounts",
        },
        locale,
    )

    if comments_blocked_from_dict is None:
        count = 0
    else:
        count = len(
            [f for f in comments_blocked_from_dict["settings_blocked_commenters"]]
        )

    return pd.DataFrame([count], columns=[tl_value])


def extract_consents(consents_dict, locale):
    """extract preferences/media_settings/consents -> day and value"""

    tl_date = translate("date", locale)
    tl_value = translate({"en": "Message", "de": "Nachricht", "nl": "Bericht"}, locale)
    # extract and preprocess dates
    date = epoch_to_date(consents_dict["timestamp"])

    consents = [v["label"] for v in consents_dict["label_values"]]

    result = pd.DataFrame({tl_date: date, tl_value: consents})

    return result


def extract_use_crossapp_messaging(use_cross_app_messaging_dict, locale):
    """extract preferences/media_settings/use_cross-app_messaging_dict -> value if enabled"""

    tl_value = translate(
        {
            "en": "Cross-app messaging",
            "de": "App-übergreifende Nachrichten",
            "nl": "Berichten tussen apps",
        },
        locale,
    )

    enabled = None

    for a in use_cross_app_messaging_dict["settings_upgraded_to_cross_app_messaging"]:
        for k in [
            "Aktualisierung auf App-\u00c3\u00bcbergreifendes Messaging durchgef\u00c3\u00bchrt"
        ]:  # keys are language specific
            if k in a["string_map_data"]:
                enabled = a["string_map_data"][k]["value"]

    return pd.DataFrame([translate("dummy", locale, enabled)], columns=[tl_value])


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


def extract_account_privacy_changes(account_privacy_changes_dict, locale):
    """extract security_and_login_information/login_and_account_creation/account_privacy_changes -> day and type-change"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {"en": "Type of change", "de": "Art des Wechsels", "nl": "Soort wijziging"},
        locale,
    )

    changes = [
        c
        for c in account_privacy_changes_dict["account_history_account_privacy_history"]
    ]
    titles = [t["title"] for t in changes]
    timestamps = []

    for c in changes:
        for k in ["Time", "Zeit"]:  # keys are language specific
            if k in c["string_map_data"]:
                timestamp = c["string_map_data"][k]["timestamp"]
                timestamps.append(epoch_to_date(timestamp))
                break

    changes_df = pd.DataFrame({tl_date: timestamps, tl_value: titles})

    aggregated_df = changes_df.groupby(tl_date)[tl_value].agg(list).reset_index()

    return aggregated_df


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


def extract_signup_information(signup_information_dict, locale):
    """extract security_and_login_information/login_and_account_creation/signup_information -> dummy if real name is used"""

    tl_value = translate(
        {
            "en": "Real Name at signup",
            "de": "Echter Name bei Anmeldung",
            "nl": "Echte naam bij aanmelding",
        },
        locale,
    )

    name_to_check = None
    real_name = False

    for k in ["Username", "Benutzername"]:  # keys are language specific
        if (
            k
            in signup_information_dict["account_history_registration_info"][0][
                "string_map_data"
            ]
        ):
            name_to_check = signup_information_dict[
                "account_history_registration_info"
            ][0]["string_map_data"][k]["value"]
            break

    # split names to check
    names_to_check = split_name(name_to_check)

    # check if name in list of names
    real_name = check_name(names_to_check)

    return pd.DataFrame([translate("dummy", locale, real_name)], columns=[tl_value])


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


def extract_archived_posts(archived_posts_dict, picture_info, locale):
    """extract your_instagram_activity/content/archived_posts -> count per day + info about face and location"""

    tl_value = translate(
        {
            "en": ["Date", "Liked location", "Face visible"],
            "de": ["Datum", "Verlikter Standort", "Gesicht sichtbar"],
            "nl": ["Datum", "Locatie leuk gevonden", "Zichtbaar gezicht"],
        },
        locale,
    )

    results = []

    for post in archived_posts_dict.get("ig_archived_post_media", []):
        for media in post.get("media", []):
            date = epoch_to_date(media.get("creation_timestamp", ""))
            uri = media.get("uri", "")
            has_latitude_data = any(
                "latitude" in exif_data
                for exif_data in media.get("media_metadata", {})
                .get("photo_metadata", {})
                .get("exif_data", [])
            )

            # check if the URI is in the picture_info dictionary
            face_visible = picture_info.get(uri, False)

            results.append(
                {
                    tl_value[0]: date,
                    tl_value[1]: translate("dummy", locale, has_latitude_data),
                    tl_value[2]: translate("dummy", locale, face_visible),
                }
            )

    archived_posts_df = pd.DataFrame(results)

    return archived_posts_df


def extract_posts_1(posts_1_dict, picture_info, locale):
    """extract your_instagram_activity/content/posts_1 -> count per day + info about face and location"""

    tl_value = translate(
        {
            "en": ["Date", "Liked location", "Face visible"],
            "de": ["Datum", "Verlikter Standort", "Gesicht sichtbar"],
            "nl": ["Datum", "Locatie leuk gevonden", "Zichtbaar gezicht"],
        },
        locale,
    )

    results = []

    # file can just be dict and not list if only one post
    if isinstance(posts_1_dict, dict):
        for media in posts_1_dict.get("media", []):
            date = epoch_to_date(media.get("creation_timestamp", ""))
            uri = media.get("uri", "")
            has_latitude_data = any(
                "latitude" in exif_data
                for exif_data in media.get("media_metadata", {})
                .get("photo_metadata", {})
                .get("exif_data", [])
            )

            # check if the URI is in the picture_info dictionary
            face_visible = picture_info.get(uri, False)

            results.append(
                {
                    tl_value[0]: date,
                    tl_value[1]: translate("dummy", locale, has_latitude_data),
                    tl_value[2]: translate("dummy", locale, face_visible),
                }
            )

    else:
        for post in posts_1_dict:
            for media in post.get("media", []):
                date = epoch_to_date(media.get("creation_timestamp", ""))
                uri = media.get("uri", "")
                has_latitude_data = any(
                    "latitude" in exif_data
                    for exif_data in media.get("media_metadata", {})
                    .get("photo_metadata", {})
                    .get("exif_data", [])
                )

                # check if the URI is in the picture_info dictionary
                face_visible = picture_info.get(uri, False)

                results.append(
                    {
                        tl_value[0]: date,
                        tl_value[1]: translate("dummy", locale, has_latitude_data),
                        tl_value[2]: translate("dummy", locale, face_visible),
                    }
                )

    posts_df = pd.DataFrame(results)

    return posts_df


def extract_profile_photos(profile_photos_dict, picture_info, locale):
    """extract your_instagram_activity/content/profile_photos -> info about face"""

    tl_value = translate(
        {"en": "Face visible", "de": "Gesicht sichtbar", "nl": "Gezicht zichtbaar"},
        locale,
    )

    uri = profile_photos_dict.get("ig_profile_picture", [])[0].get("uri", "")

    # check if the URI is in the picture_info dictionary
    face_visible = picture_info.get(uri, False)

    face_in_picture = True if face_visible >= 1 else False

    return pd.DataFrame(
        [translate("dummy", locale, face_in_picture)], columns=[tl_value]
    )


def extract_recently_deleted_content(
    recently_deleted_content_dict, picture_info, locale
):
    """extract your_instagram_activity/content/recently_deleted_content -> count per day + info about face and location"""

    tl_value = translate(
        {
            "en": ["Date", "Liked location", "Face visible"],
            "de": ["Datum", "Verlikter Standort", "Gesicht sichtbar"],
            "nl": ["Datum", "Locatie leuk gevonden", "Zichtbaar gezicht"],
        },
        locale,
    )

    results = []

    for post in recently_deleted_content_dict.get("ig_recently_deleted_media", []):
        for media in post.get("media", []):
            date = epoch_to_date(media.get("creation_timestamp", ""))
            uri = media.get("uri", "")
            has_latitude_data = any(
                "latitude" in exif_data
                for exif_data in media.get("media_metadata", {})
                .get("photo_metadata", {})
                .get("exif_data", [])
            )

            # Check if the URI is in the picture_info dictionary
            face_visible = picture_info.get(uri, False)

            results.append(
                {
                    tl_value[0]: date,
                    tl_value[1]: translate("dummy", locale, has_latitude_data),
                    tl_value[2]: translate("dummy", locale, face_visible),
                }
            )

    recently_deleted_content_df = pd.DataFrame(results)

    return recently_deleted_content_df


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


def extract_stories(stories_dict, picture_info, locale):
    """extract your_instagram_activity/content/stories -> count per day + info about face and location"""

    tl_value = translate(
        {
            "en": ["Date", "Liked location", "Face visible"],
            "de": ["Datum", "Verlikter Standort", "Gesicht sichtbar"],
            "nl": ["Datum", "Locatie leuk gevonden", "Zichtbaar gezicht"],
        },
        locale,
    )

    results = []

    for story in stories_dict.get("ig_stories", []):
        date = epoch_to_date(story.get("creation_timestamp", ""))
        uri = story.get("uri", "")
        has_latitude_data = any(
            "latitude" in exif_data
            for exif_data in story.get("media_metadata", {})
            .get("photo_metadata", {})
            .get("exif_data", [])
        )

        # check if the URI is in the picture_info dictionary
        face_visible = picture_info.get(uri, False)

        results.append(
            {
                tl_value[0]: date,
                tl_value[1]: translate("dummy", locale, has_latitude_data),
                tl_value[2]: translate("dummy", locale, face_visible),
            }
        )

    stories_df = pd.DataFrame(results)

    return stories_df


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


def extract_saved_collections(saved_collections_dict, locale):
    """extract your_instagram_activity/saved/saved_collections -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of saved content",
            "de": "Anzahl gespeicherter Beiträge",
            "nl": "Aantal opgeslagen inhoud",
        },
        locale,
    )

    dates = []

    # get list with timestamps in epoch format and skip all collection titles
    for t in saved_collections_dict["saved_saved_collections"]:
        for k in ["Added Time"]:  # keys are language specific
            if k in t["string_map_data"]:
                try:
                    dates.append(epoch_to_date(t["string_map_data"][k]["timestamp"]))
                except:
                    continue
                break

    if not dates:
        return pd.DataFrame(
            ['Keine Informationen: (Datei "saved_collections" hat keine Beiträge)']
        )

    dates_df = pd.DataFrame(dates, columns=[tl_date])  # convert to df

    aggregated_df = dates_df.groupby([tl_date])[
        tl_date
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name=tl_value)


def extract_saved_posts(saved_posts_dict, locale):
    """extract your_instagram_activity/saved/saved_posts -> count per day"""

    tl_date = translate("date", locale)
    tl_value = translate(
        {
            "en": "Count of saved content",
            "de": "Anzahl gespeicherter Beiträge",
            "nl": "Aantal opgeslagen inhoud",
        },
        locale,
    )

    dates = []

    # get list with timestamps in epoch format
    for t in saved_posts_dict["saved_saved_media"]:
        for k in ["Saved on"]:  # keys are language specific
            if k in t["string_map_data"]:
                dates.append(epoch_to_date(t["string_map_data"][k]["timestamp"]))
            break

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
