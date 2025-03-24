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
# Extraction functions for LinkedIn data
############################


def extract_connections(connections_csv, locale):
    """Extract LinkedIn connections data with absolute counts instead of percentages"""

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
            "en": "With full name",
            "de": "Mit vollständigem Namen",
            "nl": "Met volledige naam",
        },
        locale,
    )
    tl_has_url = translate(
        {"en": "With profile URL", "de": "Mit Profil-URL", "nl": "Met profiel-URL"},
        locale,
    )
    tl_has_email = translate(
        {"en": "With email", "de": "Mit E-Mail", "nl": "Met e-mail"}, locale
    )
    tl_has_company = translate(
        {"en": "With company", "de": "Mit Unternehmen", "nl": "Met bedrijf"}, locale
    )
    tl_has_position = translate(
        {"en": "With position", "de": "Mit Position", "nl": "Met functie"}, locale
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

        # Calculate absolute counts for each field (not percentages)
        has_names = sum((group["First Name"].notna()) & (group["Last Name"].notna()))
        has_url = sum(group["URL"].notna())
        has_email = sum(group["Email Address"].notna())
        has_company = sum(group["Company"].notna())
        has_position = sum(group["Position"].notna())

        results.append(
            {
                tl_date: std_date,
                tl_count: count,
                tl_has_names: has_names,
                tl_has_url: has_url,
                tl_has_email: has_email,
                tl_has_company: has_company,
                tl_has_position: has_position,
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


def extract_reactions(reactions_csv, locale):
    """Extract LinkedIn reactions data (likes, celebrates, supports, etc.)"""

    tl_date = translate("date", locale)
    tl_type = translate(
        {
            "en": "Reaction Type",
            "de": "Reaktionstyp",
            "nl": "Reactietype",
        },
        locale,
    )
    tl_count = translate(
        {
            "en": "Count",
            "de": "Anzahl",
            "nl": "Aantal",
        },
        locale,
    )

    # Check if DataFrame is empty or None
    if reactions_csv is None or reactions_csv.empty:
        return pd.DataFrame(
            {
                tl_date: ["N/A"],
                tl_type: ["N/A"],
                tl_count: ["No reaction data available"],
            }
        )

    # Find the date and type columns
    date_column = None
    type_column = None

    for col in reactions_csv.columns:
        if "Date" in col or "Time" in col:
            date_column = col
        if "Type" in col or "Typ" in col or "Reaction" in col:
            type_column = col

    if not date_column or not type_column:
        return pd.DataFrame(
            {
                tl_date: ["N/A"],
                tl_type: ["Column not found"],
                tl_count: [f"Total reactions: {len(reactions_csv)}"],
            }
        )

    # Process reaction data
    try:
        # Convert dates to a standard format
        processed_df = reactions_csv.copy()

        # Format the date to ensure it's in readable format, not as timestamp
        processed_df["formatted_date"] = pd.to_datetime(
            processed_df[date_column]
        ).dt.strftime("%Y-%m-%d")

        # Group by date and reaction type
        grouped_reactions = (
            processed_df.groupby(["formatted_date", type_column])
            .size()
            .reset_index(name=tl_count)
        )
        grouped_reactions.rename(
            columns={"formatted_date": tl_date, type_column: tl_type}, inplace=True
        )

        return grouped_reactions

    except Exception as e:
        print(f"Error processing reactions data: {e}")
        return pd.DataFrame(
            {tl_date: ["N/A"], tl_type: ["Processing error"], tl_count: ["N/A"]}
        )


def extract_messages(messages_csv, locale):
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


def extract_search_queries(search_queries_csv, locale):
    """Extract LinkedIn search queries data aggregated by day"""

    tl_date = translate("date", locale)
    tl_count = translate(
        {
            "en": "Number of searches",
            "de": "Anzahl der Suchanfragen",
            "nl": "Aantal zoekopdrachten",
        },
        locale,
    )

    # Check if DataFrame is empty or None
    if search_queries_csv is None or search_queries_csv.empty:
        return pd.DataFrame(
            {
                tl_date: ["N/A"],
                tl_count: ["No search data available"],
            }
        )

    # Find the time/date column
    time_column = None
    for col in search_queries_csv.columns:
        if "Time" in col or "Zeit" in col or "Date" in col:
            time_column = col
            break

    if not time_column:
        return pd.DataFrame(
            {
                tl_date: ["N/A"],
                tl_count: [f"Total searches: {len(search_queries_csv)}"],
            }
        )

    # Process search data
    try:
        # Create a copy to avoid SettingWithCopyWarning
        processed_df = search_queries_csv.copy()

        # Convert dates to a standard readable format
        processed_df["formatted_date"] = pd.to_datetime(
            processed_df[time_column], format="%Y/%m/%d %H:%M:%S UTC", errors="coerce"
        ).dt.strftime("%Y-%m-%d")

        # Count searches per day
        daily_counts = (
            processed_df.groupby("formatted_date").size().reset_index(name=tl_count)
        )
        daily_counts.rename(columns={"formatted_date": tl_date}, inplace=True)

        return daily_counts

    except Exception as e:
        print(f"Error processing search queries data: {e}")
        return pd.DataFrame(
            {tl_date: ["N/A"], tl_count: [f"Processing error: {str(e)}"]}
        )


def extract_interests(ad_targeting_csv, locale):
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


def extract_profile(profile_csv, locale):
    """Extract LinkedIn profile information and create binary indicators"""

    tl_field = translate(
        {
            "en": "Profile Information",
            "de": "Profilinformationen",
            "nl": "Profielinformatie",
        },
        locale,
    )
    tl_has_value = translate(
        {
            "en": "Has Value",
            "de": "Hat Wert",
            "nl": "Heeft waarde",
        },
        locale,
    )

    # Check if DataFrame is empty or None
    if profile_csv is None or profile_csv.empty:
        return pd.DataFrame(
            {
                tl_field: ["N/A"],
                tl_has_value: ["No profile data available"],
            }
        )

    # Important profile fields to check
    important_fields = [
        ("First Name", "Vorname", "Voornaam"),
        ("Last Name", "Nachname", "Achternaam"),
        ("Address", "Adresse", "Adres"),
        ("Birth Date", "Geburtsdatum", "Geboortedatum"),
        ("Zip Code", "Postleitzahl", "Postcode"),
    ]

    # Check each field
    results = []
    for fields in important_fields:
        field_found = False
        field_name = fields[0]  # Use English as default

        # Try to find the field in any language
        for field in fields:
            if field in profile_csv.columns:
                field_name = field
                field_found = True
                break

        if field_found:
            # Check if the field has a value (at least one non-null entry)
            has_value = profile_csv[field_name].notna().any()
            results.append(
                {
                    tl_field: field_name,
                    tl_has_value: translate("dummy", locale, has_value),
                }
            )
        else:
            results.append(
                {tl_field: field_name, tl_has_value: translate("dummy", locale, False)}
            )

    return pd.DataFrame(results)


def extract_positions(positions_csv, locale):
    """Extract LinkedIn positions information as binary indicators"""

    tl_has_company = translate(
        {
            "en": "Has Company Name",
            "de": "Hat Firmenname",
            "nl": "Heeft Bedrijfsnaam",
        },
        locale,
    )
    tl_has_title = translate(
        {
            "en": "Has Title",
            "de": "Hat Titel",
            "nl": "Heeft Titel",
        },
        locale,
    )
    tl_has_description = translate(
        {
            "en": "Has Description",
            "de": "Hat Beschreibung",
            "nl": "Heeft Beschrijving",
        },
        locale,
    )
    tl_has_location = translate(
        {
            "en": "Has Location",
            "de": "Hat Standort",
            "nl": "Heeft Locatie",
        },
        locale,
    )
    tl_has_dates = translate(
        {
            "en": "Has Employment Dates",
            "de": "Hat Beschäftigungsdaten",
            "nl": "Heeft Werkperiode",
        },
        locale,
    )

    # Check if DataFrame is empty or None
    if positions_csv is None or positions_csv.empty:
        return pd.DataFrame(
            {
                tl_has_company: ["N/A"],
                tl_has_title: ["N/A"],
                tl_has_description: ["N/A"],
                tl_has_location: ["N/A"],
                tl_has_dates: ["N/A"],
            }
        )

    # Find the needed columns
    company_col = None
    title_col = None
    description_col = None
    location_col = None
    start_date_col = None
    end_date_col = None

    # Try to find column names across languages
    for col in positions_csv.columns:
        if "Company" in col or "Firma" in col:
            company_col = col
        if "Title" in col or "Titel" in col:
            title_col = col
        if "Description" in col or "Beschreibung" in col:
            description_col = col
        if "Location" in col or "Standort" in col:
            location_col = col
        if "Started" in col or "Begonnen" in col:
            start_date_col = col
        if "Finished" in col or "Beendet" in col:
            end_date_col = col

    # Create a summary DataFrame with the counts and percentages
    result = pd.DataFrame(
        {
            tl_has_company: [
                translate(
                    "dummy",
                    locale,
                    company_col is not None
                    and any(pd.notnull(positions_csv[company_col])),
                )
            ],
            tl_has_title: [
                translate(
                    "dummy",
                    locale,
                    title_col is not None and any(pd.notnull(positions_csv[title_col])),
                )
            ],
            tl_has_description: [
                translate(
                    "dummy",
                    locale,
                    description_col is not None
                    and any(pd.notnull(positions_csv[description_col])),
                )
            ],
            tl_has_location: [
                translate(
                    "dummy",
                    locale,
                    location_col is not None
                    and any(pd.notnull(positions_csv[location_col])),
                )
            ],
            tl_has_dates: [
                translate(
                    "dummy",
                    locale,
                    (
                        start_date_col is not None
                        and any(pd.notnull(positions_csv[start_date_col]))
                    )
                    or (
                        end_date_col is not None
                        and any(pd.notnull(positions_csv[end_date_col]))
                    ),
                )
            ],
        }
    )

    return result


def extract_device_usage(security_challenges_csv, locale):
    """Extract device usage information from security challenges data"""

    tl_date = translate("date", locale)
    tl_user_agent = translate(
        {
            "en": "User Agent",
            "de": "User Agent",
            "nl": "User Agent",
        },
        locale,
    )
    tl_country = translate(
        {
            "en": "Country",
            "de": "Land",
            "nl": "Land",
        },
        locale,
    )

    # Check if DataFrame is empty or None
    if security_challenges_csv is None or security_challenges_csv.empty:
        return pd.DataFrame(
            {
                tl_date: ["N/A"],
                tl_user_agent: ["No device data available"],
                tl_country: ["N/A"],
            }
        )

    # This is a special case as the CSV may have data spread across multiple columns
    # due to commas in the user agent string

    # Try to reconstruct the data
    results = []

    try:
        # First, identify the important columns
        challenge_date_col = None
        user_agent_col = None
        country_col = None

        for col in security_challenges_csv.columns:
            if "Challenge Date" in col or "Datum" in col:
                challenge_date_col = col
            if "User Agent" in col or "Agent" in col:
                user_agent_col = col
            if "Country" in col or "Land" in col:
                country_col = col

        # If we couldn't find the columns by name, try to use positional logic
        if not challenge_date_col and len(security_challenges_csv.columns) > 0:
            challenge_date_col = security_challenges_csv.columns[
                0
            ]  # Usually first column

        if not country_col and len(security_challenges_csv.columns) > 3:
            country_col = security_challenges_csv.columns[3]  # Often the 4th column

        for _, row in security_challenges_csv.iterrows():
            # Get the date (format: "Sat Apr 29 16:38:10 UTC 2023" or similar)
            if challenge_date_col:
                date_str = str(row[challenge_date_col])
                date_parts = date_str.split()
                if len(date_parts) >= 3:
                    date_str = f"{date_parts[1]} {date_parts[2]}, {date_parts[-1]}"

            else:
                date_str = "Unknown Date"

            # Get country
            country = "Unknown"
            if country_col and pd.notna(row[country_col]):
                country = row[country_col]

            # Try to find the user agent by looking through all cells in the row
            user_agent = "Unknown"
            for col, value in row.items():
                if isinstance(value, str) and (
                    "Mozilla" in value or "AppleWebKit" in value
                ):
                    user_agent = value
                    break

            results.append(
                {tl_date: date_str, tl_user_agent: user_agent, tl_country: country}
            )

        return pd.DataFrame(results)

    except Exception as e:
        print(f"Error processing device usage data: {e}")
        return pd.DataFrame(
            {
                tl_date: ["N/A"],
                tl_user_agent: [f"Processing error: {str(e)}"],
                tl_country: ["N/A"],
            }
        )
