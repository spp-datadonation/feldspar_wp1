from port.api.assets import *
from port.api.props import Translatable
import pandas as pd
from datetime import datetime
import re

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


def parse_linkedin_date(date_str):
    """Convert LinkedIn date formats to standard format"""
    try:
        # Try different date formats
        for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y", "%B %d, %Y"):
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return date_str  # Return original if no format matches
    except:
        return "Unknown"


############################
# Extraction functions for LinkedIn data
############################


def extract_linkedin_messages(messages_csv, locale):
    """Extract LinkedIn messages data aggregated by day and member"""

    tl_date = translate("date", locale)
    tl_count = translate(
        {
            "en": "Number of messages",
            "de": "Anzahl der Nachrichten",
            "nl": "Aantal berichten",
        },
        locale,
    )
    tl_members = translate(
        {
            "en": "Number of unique contacts",
            "de": "Anzahl einzigartiger Kontakte",
            "nl": "Aantal unieke contacten",
        },
        locale,
    )

    # Check if DataFrame is empty or None
    if messages_csv is None or messages_csv.empty:
        return pd.DataFrame(
            {
                tl_date: ["N/A"],
                tl_count: ["No message data available"],
                tl_members: ["N/A"],
            }
        )

    # Try to find date column
    date_col = None
    for col in messages_csv.columns:
        if "DATE" in col.upper() or "DATUM" in col.upper():
            date_col = col
            break

    # Try to find sender column
    sender_col = None
    for col in messages_csv.columns:
        if "FROM" in col.upper() or "VON" in col.upper() or "SENDER" in col.upper():
            sender_col = col
            break

    if not date_col or not sender_col:
        return pd.DataFrame(
            {
                tl_date: ["N/A"],
                tl_count: [f"Total messages: {len(messages_csv)}"],
                tl_members: ["Column not found"],
            }
        )

    # Process each day
    try:
        messages_csv[date_col] = pd.to_datetime(messages_csv[date_col], errors="coerce")
        # Use date part only
        messages_csv["DATE_STD"] = messages_csv[date_col].dt.strftime("%Y-%m-%d")

        # Remove NaT values
        messages_csv = messages_csv.dropna(subset=["DATE_STD"])

        if messages_csv.empty:
            return pd.DataFrame(
                {
                    tl_date: ["N/A"],
                    tl_count: ["Date parsing error"],
                    tl_members: ["N/A"],
                }
            )

        # Group by date and count messages and unique members
        daily_counts = (
            messages_csv.groupby("DATE_STD")
            .agg(
                message_count=("DATE_STD", "count"),
                members=(sender_col, lambda x: len(set(x))),
            )
            .reset_index()
        )

        # Create result DataFrame
        result_df = pd.DataFrame(
            {
                tl_date: daily_counts["DATE_STD"],
                tl_count: daily_counts["message_count"],
                tl_members: daily_counts["members"],
            }
        )

        return result_df

    except Exception as e:
        print(f"Error processing messages data: {e}")
        return pd.DataFrame(
            {tl_date: ["N/A"], tl_count: ["Processing error"], tl_members: ["N/A"]}
        )


def extract_linkedin_connections(connections_csv, locale):
    """Extract LinkedIn connections data with proper date formatting and field checks"""

    tl_date = translate("date", locale)
    tl_count = translate(
        {
            "en": "Number of connections",
            "de": "Anzahl der Verbindungen",
            "nl": "Aantal connecties",
        },
        locale,
    )
    tl_has_names = translate(
        {
            "en": "Has full name",
            "de": "Hat vollständigen Namen",
            "nl": "Heeft volledige naam",
        },
        locale,
    )
    tl_has_url = translate(
        {"en": "Has profile URL", "de": "Hat Profil-URL", "nl": "Heeft profiel-URL"},
        locale,
    )
    tl_has_email = translate(
        {"en": "Has email", "de": "Hat E-Mail", "nl": "Heeft e-mail"}, locale
    )
    tl_has_company = translate(
        {"en": "Has company", "de": "Hat Unternehmen", "nl": "Heeft bedrijf"}, locale
    )
    tl_has_position = translate(
        {"en": "Has position", "de": "Hat Position", "nl": "Heeft functie"}, locale
    )

    # Check if DataFrame is empty or None
    if connections_csv is None or connections_csv.empty:
        return pd.DataFrame(
            {
                tl_date: ["N/A"],
                tl_count: ["No data available"],
                tl_has_names: ["N/A"],
                tl_has_url: ["N/A"],
                tl_has_email: ["N/A"],
                tl_has_company: ["N/A"],
                tl_has_position: ["N/A"],
            }
        )

    # Process connections data
    results = []

    # Find the date column - in your case it's "Connected On"
    date_column = "Connected On"
    if date_column not in connections_csv.columns:
        for col in connections_csv.columns:
            if "Connect" in col or "Date" in col:
                date_column = col
                break

    if date_column not in connections_csv.columns:
        return pd.DataFrame(
            {
                tl_date: ["N/A"],
                tl_count: [f"Total connections: {len(connections_csv)}"],
                tl_has_names: ["Column not found"],
                tl_has_url: ["Column not found"],
                tl_has_email: ["Column not found"],
                tl_has_company: ["Column not found"],
                tl_has_position: ["Column not found"],
            }
        )

    # Process each connection date
    grouped_connections = connections_csv.groupby(date_column)
    for date, group in grouped_connections:
        # Convert date to standard format (based on your "23 Mar 2025" format)
        try:
            date_obj = pd.to_datetime(date, format="%d %b %Y")
            std_date = date_obj.strftime("%Y-%m-%d")
        except:
            std_date = str(date)

        # Count connections for this date
        count = len(group)

        # Calculate percentages for each field
        has_names = (
            (group["First Name"].notna()) & (group["Last Name"].notna())
        ).mean()
        has_url = group["URL"].notna().mean()
        has_email = group["Email Address"].notna().mean()
        has_company = group["Company"].notna().mean()
        has_position = group["Position"].notna().mean()

        results.append(
            {
                tl_date: std_date,
                tl_count: count,
                tl_has_names: f"{has_names:.1%}",
                tl_has_url: f"{has_url:.1%}",
                tl_has_email: f"{has_email:.1%}",
                tl_has_company: f"{has_company:.1%}",
                tl_has_position: f"{has_position:.1%}",
            }
        )

    if not results:
        return pd.DataFrame(
            {
                tl_date: ["N/A"],
                tl_count: [f"Total connections: {len(connections_csv)}"],
                tl_has_names: ["No data by date"],
                tl_has_url: ["No data by date"],
                tl_has_email: ["No data by date"],
                tl_has_company: ["No data by date"],
                tl_has_position: ["No data by date"],
            }
        )

    return pd.DataFrame(results)


def extract_linkedin_interests(ad_targeting_csv, locale):
    """Extract LinkedIn member interests from Ad_Targeting data"""

    tl_interest = translate(
        {
            "en": "LinkedIn Interest",
            "de": "LinkedIn-Interesse",
            "nl": "LinkedIn-interesse",
        },
        locale,
    )

    # Check if DataFrame is empty or None
    if ad_targeting_csv is None or ad_targeting_csv.empty:
        return pd.DataFrame({tl_interest: ["No interest data available"]})

    # Based on your data, "Member Interests" appears to be the column name
    interest_col = "Member Interests"
    if interest_col not in ad_targeting_csv.columns:
        # Try to find a column with "Interest" in the name
        for col in ad_targeting_csv.columns:
            if "Interest" in col:
                interest_col = col
                break

    if interest_col not in ad_targeting_csv.columns:
        return pd.DataFrame({tl_interest: ["No interests column found in data"]})

    # Process the interests
    all_interests = []

    # Get the first non-empty value from the column
    for _, row in ad_targeting_csv.iterrows():
        if pd.notna(row[interest_col]):
            value = str(row[interest_col]).strip()
            if value:
                # Your data appears to have multiple items in the cell
                # Try to split by different separators
                items = []
                for item in value.split(";"):
                    items.extend(i.strip() for i in item.split("  ") if i.strip())
                all_interests.extend(items)

    # If no interests found, try "Member Skills" as fallback
    if not all_interests and "Member Skills" in ad_targeting_csv.columns:
        for _, row in ad_targeting_csv.iterrows():
            if pd.notna(row["Member Skills"]):
                value = str(row["Member Skills"]).strip()
                if value:
                    items = []
                    for item in value.split(";"):
                        items.extend(i.strip() for i in item.split("  ") if i.strip())
                    all_interests.extend(items)

    if not all_interests:
        return pd.DataFrame({tl_interest: ["No interests found in data"]})

    # Remove duplicates and create DataFrame
    unique_interests = sorted(set(all_interests))
    result_df = pd.DataFrame({tl_interest: unique_interests})

    return result_df
