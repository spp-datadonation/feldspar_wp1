import port.api.props as props
from port.api.commands import CommandSystemDonate, CommandUIRender

# Import extraction functions and dictionaries for all platforms
from port.instagram_extraction_functions import *
from port.instagram_extraction_functions_dict import (
    extraction_dict as instagram_extraction_dict,
)
from port.linkedin_extraction_functions import *
from port.linkedin_extraction_functions_dict import (
    extraction_dict as linkedin_extraction_dict,
)
from port.youtube_extraction_functions import *
from port.youtube_extraction_functions_dict import (
    extraction_dict as youtube_extraction_dict,
)

import zipfile
import numpy as np
import pandas as pd
import time
import json
import os

############################
# MAIN FUNCTION INITIATING THE DONATION PROCESS
############################


def process(sessionId):
    locale = "de"
    key = "wp1-data-donation"
    meta_data = []
    meta_data.append(("debug", f"{key}: start"))

    # STEP 1: Select DDP and extract automatically required data
    data = None
    platform = None

    while True:
        meta_data.append(("debug", f"{key}: prompt file"))

        # Allow users to only upload zip-files and render file-input page
        promptFile = prompt_file("application/zip")
        fileResult = yield render_donation_page(promptFile, platform="")

        # If user input
        if fileResult.__type__ == "PayloadString":
            # First, identify which platform the data is from
            platform = identify_platform(fileResult.value)
            meta_data.append(
                (
                    "debug",
                    f"{key}: identified platform as {platform if platform else 'unknown'}",
                )
            )

            if platform == "instagram":
                check_ddp = check_if_valid_instagram_ddp(fileResult.value)
            elif platform == "linkedin":
                check_ddp = check_if_valid_linkedin_ddp(fileResult.value)
            elif platform == "youtube":
                check_ddp = check_if_valid_youtube_ddp(fileResult.value)
            else:
                # If platform could not be identified
                meta_data.append(
                    ("debug", f"{key}: unknown platform, cannot process file")
                )
                retry_result = yield render_donation_page(
                    retry_confirmation_unknown_platform(), platform=""
                )
                if retry_result.__type__ == "PayloadTrue":
                    meta_data.append(("debug", f"{key}: retry prompt file"))
                    continue
                else:
                    break

            if check_ddp == "valid":
                meta_data.append(
                    ("debug", f"{key}: extracting file for platform {platform}")
                )

                # Use the unified extract_data function with platform parameter
                extract_gen = extract_data(fileResult.value, locale, platform)

                while True:
                    try:
                        # Get the next progress update from the generator
                        message, percentage, data = next(extract_gen)
                        # Create a progress message for the UI
                        promptMessage = prompt_extraction_message(message, percentage)
                        # Render the progress page
                        yield render_donation_page(promptMessage, platform)
                    except StopIteration:
                        # The generator is exhausted, break the loop
                        break

                meta_data.append(
                    ("debug", f"{key}: extraction successful, go to consent form")
                )
                break

            elif (
                check_ddp == "invalid_no_json"
            ):  # for linkedin: checks basic vs. complete DDP
                meta_data.append(
                    (
                        "debug",
                        f"{key}: prompt confirmation to retry file selection (invalid_no_json for {platform})",
                    )
                )
                retry_result = yield render_donation_page(
                    retry_confirmation_no_json(platform), platform
                )

                if retry_result.__type__ == "PayloadTrue":
                    meta_data.append(("debug", f"{key}: retry prompt file"))
                    continue

            elif check_ddp == "invalid_no_ddp":
                meta_data.append(
                    (
                        "debug",
                        f"{key}: prompt confirmation to retry file selection (invalid_no_ddp for {platform})",
                    )
                )
                # Use platform-specific error messages
                retry_result = yield render_donation_page(
                    retry_confirmation_no_ddp(platform), platform
                )

                if retry_result.__type__ == "PayloadTrue":
                    meta_data.append(("debug", f"{key}: retry prompt file"))
                    continue

            else:
                meta_data.append(
                    (
                        "debug",
                        f"{key}: prompt confirmation to retry file selection (invalid_file)",
                    )
                )
                print(check_ddp)
                retry_result = yield render_donation_page(
                    retry_confirmation_no_ddp(platform), platform
                )

                if retry_result.__type__ == "PayloadTrue":
                    meta_data.append(("debug", f"{key}: retry prompt file"))
                    continue

    # STEP 2: Present user their extracted data and ask for consent
    if platform and data:
        meta_data.append(("debug", f"{key}: prompt consent"))
        # Render donation page with extracted data
        prompt = prompt_consent(data, meta_data, locale, platform)
        consent_result = yield render_donation_page(prompt, platform)

        # Send data if consent
        if consent_result.__type__ == "PayloadJSON":
            meta_data.append(("debug", f"{key}: donate consent data"))
            yield donate(f"{sessionId}-{key}", consent_result.value)

        # Send no data if no consent
        if consent_result.__type__ == "PayloadFalse":
            value = json.dumps('{"status" : "donation declined"}')
            yield donate(f"{sessionId}-{key}", value)


def identify_platform(filename):
    """
    Identify the platform based on the filename of the uploaded zip file.
    Returns: "instagram", "linkedin", "youtube", or None if not identified
    """
    try:
        # Get the name of the zip file (without path)
        zip_name = os.path.basename(filename)

        if zip_name.startswith("instagram-"):
            return "instagram"
        elif zip_name.startswith("Basic_LinkedInDataExport") or zip_name.startswith(
            "Complete_LinkedInDataExport"
        ):
            return "linkedin"
        elif zip_name.startswith("takeout-"):
            return "youtube"

        # If filename pattern doesn't match, try to check contents as a fallback
        with zipfile.ZipFile(filename, "r") as zip_ref:
            file_list = zip_ref.namelist()
            first_level_entries = {entry.split("/")[0] for entry in file_list if entry}

            # Check first level entries for platform-specific indicators
            if "ads_information" in first_level_entries:
                return "instagram"

            # LinkedIn typically has these files at root level
            if "Profile.csv" in file_list:
                return "linkedin"

            # YouTube/Google Takeout has a specific folder structure
            if "Takeout" in first_level_entries:
                return "youtube"

    except zipfile.BadZipFile:
        print("Invalid ZIP file.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return None


def check_if_valid_instagram_ddp(filename):
    """Check if the uploaded file is a valid Instagram data download package"""
    folder_name_check_ddp = "ads_information"
    file_name_check_html = "start_here.html"

    try:
        with zipfile.ZipFile(filename, "r") as zip_ref:
            found_folder_name_check_ddp = False
            found_file_name_check_html = False

            for file_info in zip_ref.infolist():
                if folder_name_check_ddp in file_info.filename:
                    found_folder_name_check_ddp = True

                if file_name_check_html in file_info.filename:
                    found_file_name_check_html = True

            if found_folder_name_check_ddp:
                if found_file_name_check_html:
                    print(
                        f"Folder '{folder_name_check_ddp}' found and file '{file_name_check_html}' found in the ZIP file. Seems like a Instagram HTML DDP."
                    )
                    return "invalid_no_json"

                else:
                    print(
                        f"Folder '{folder_name_check_ddp}' found and file '{file_name_check_html}' not found in the ZIP file. Seems like a real Instagram JSON DDP."
                    )
                    return "valid"

            else:
                print(
                    f"Folder '{folder_name_check_ddp}' not found. Does not seem like an Instagram DDP."
                )
                return "invalid_no_ddp"

    except zipfile.BadZipFile:
        print("Invalid ZIP file.")
        return "invalid_file_zip"

    except Exception as e:
        print(f"An error occurred: {e}")
        return "invalid_file_error"


def check_if_valid_linkedin_ddp(filename):
    """Check if the uploaded file is a valid LinkedIn data download package"""
    file_name_check_ddp = "Profile.csv"
    ddp_name_check_complete = "Complete_LinkedInDataExport"

    found_ddp_name_check_complete = False
    found_file_name_check_ddp = False

    if ddp_name_check_complete in filename:
        found_ddp_name_check_complete = True

    try:
        with zipfile.ZipFile(filename, "r") as zip_ref:
            for file_info in zip_ref.infolist():
                if file_name_check_ddp in file_info.filename:
                    found_file_name_check_ddp = True

            if found_file_name_check_ddp:
                if found_ddp_name_check_complete:
                    print(
                        f"Folder '{file_name_check_ddp}' found and ZIP file with '{ddp_name_check_complete}'. Seems like a real Complete LinkedIn DDP."
                    )
                    return "valid"
                else:
                    print(
                        f"Folder '{file_name_check_ddp}' found but ZIP file does not start with '{ddp_name_check_complete}'. Seems like a Basic LinkedIn DDP."
                    )
                    return "invalid_no_json"

            else:
                print(
                    f"Folder '{file_name_check_ddp}' not found. Does not seem like an LinkedIn DDP."
                )
                return "invalid_no_ddp"

    except zipfile.BadZipFile:
        print("Invalid ZIP file.")
        return "invalid_file_zip"

    except Exception as e:
        print(f"An error occurred: {e}")
        return "invalid_file_error"


def check_if_valid_youtube_ddp(filename):
    """Check if the uploaded file is a valid YouTube data download package"""
    folder_name_check_ddp = [
        "YouTube und YouTube Music",
        "YouTube and YouTube Music",
    ]  # language sensitive
    file_name_check_html = [
        "Wiedergabeverlauf.html",
        "watch-history.html",
    ]  # language sensitive

    try:
        with zipfile.ZipFile(filename, "r") as zip_ref:
            found_folder_name_check_ddp = False
            found_file_name_check_html = False

            for file_info in zip_ref.infolist():
                if any(
                    folder_name in file_info.filename
                    for folder_name in folder_name_check_ddp
                ):
                    found_folder_name_check_ddp = True

                if any(
                    file_name in file_info.filename
                    for file_name in file_name_check_html
                ):
                    found_file_name_check_html = True

            if found_folder_name_check_ddp:
                if found_file_name_check_html:
                    print(
                        f"Folder '{folder_name_check_ddp}' found and file '{file_name_check_html}' found in the ZIP file. Seems like a YouTube HTML DDP."
                    )
                    return "invalid_no_json"

                else:
                    print(
                        f"Folder '{folder_name_check_ddp}' found and file '{file_name_check_html}' not found in the ZIP file. Seems like a real YouTube JSON DDP."
                    )
                    return "valid"

            else:
                print(
                    f"Folder '{folder_name_check_ddp}' not found. Does not seem like an YouTube DDP."
                )
                return "invalid_no_ddp"

    except zipfile.BadZipFile:
        print("Invalid ZIP file.")
        return "invalid_file_zip"

    except Exception as e:
        print(f"An error occurred: {e}")
        return "invalid_file_error"


def extract_data(filename, locale, platform):
    """
    Takes a zip folder, extracts relevant content based on the platform,
    then extracts & processes relevant information and returns them as dataframes

    Parameters:
    - filename: path to the zip file
    - locale: language locale (e.g., "en", "de", "nl")
    - platform: "instagram", "linkedin", or "youtube"

    Returns:
    - Generator that yields progress updates and extracted data
    """
    data = []

    # Determine which extraction dictionary to use based on platform
    if platform == "instagram":
        extraction_dict = instagram_extraction_dict
        platform_name = "Instagram"
    elif platform == "linkedin":
        extraction_dict = linkedin_extraction_dict
        platform_name = "LinkedIn"
    elif platform == "youtube":
        extraction_dict = youtube_extraction_dict
        platform_name = "YouTube"

    for index, (file, entry) in enumerate(extraction_dict.items(), start=1):
        # Get list of possible file names (sometimes language sensitive)
        patterns = entry.get("patterns", [file])

        # Extract content based on platform
        if platform == "instagram":
            file_content, matched_pattern = extract_instagram_content_from_zip_folder(
                filename, file, patterns
            )
        elif platform == "linkedin":
            file_content, matched_pattern = extract_linkedin_content_from_zip_folder(
                filename, patterns
            )
        elif platform == "youtube":
            file_content, matched_pattern = extract_youtube_content_from_zip_folder(
                filename, patterns
            )

        if file_content is not None:
            try:
                # Call the extraction function with content
                file_df = entry["extraction_function"](file_content, locale)
            except Exception as e:
                # If extraction fails
                translatedMessage = props.Translatable(
                    {
                        "en": "Extraction failed - ",
                        "de": "Extrahierung fehlgeschlagen - ",
                        "nl": "Extractie mislukt - ",
                    }
                )

                file_df = pd.DataFrame(
                    [
                        f"{translatedMessage.translations[locale]}{file, type(e).__name__}: {matched_pattern}"
                    ],
                    columns=[str(file)],
                )
        else:
            translatedMessage1 = props.Translatable(
                {
                    "en": f'(File "{str(file)}" missing)',
                    "de": f'(Datei "{str(file)}" fehlt)',
                    "nl": f'(Bestand "{str(file)}" ontbreekt)',
                }
            )

            translatedMessage2 = props.Translatable(
                {
                    "en": "No information",
                    "de": "Keine Informationen",
                    "nl": "Geen informatie",
                }
            )

            file_df = pd.DataFrame(
                [translatedMessage1.translations[locale]],
                columns=[translatedMessage2.translations[locale]],
            )

        data.append(file_df)

        # Yield progress update
        translatedMessage = props.Translatable(
            {
                "en": f"Data extraction from {platform_name} file: ",
                "de": f"Daten-Extrahierung aus der {platform_name}-Datei: ",
                "nl": f"Gegevens extractie uit het {platform_name} bestand: ",
            }
        )

        yield (
            f"{translatedMessage.translations[locale]}{file}",
            (index / len(extraction_dict)) * 100,
            data,
        )

    # Yield final progress update and the extracted data
    translatedMessage = props.Translatable(
        {
            "en": f"{platform_name} data extraction completed",
            "de": f"{platform_name} Daten-Extrahierung abgeschlossen",
            "nl": f"{platform_name} Gegevens extractie voltooid",
        }
    )
    yield f"{translatedMessage.translations[locale]}", 100, data


def extract_instagram_content_from_zip_folder(zip_file_path, file_key, patterns):
    """
    Extract JSON content from Instagram data export zip file based on the file key.

    Parameters:
    - zip_file_path: Path to the zip file
    - file_key: The key from extraction_dict (e.g., 'messages', 'time_spent')
    - patterns: File patterns to look for (used as fallback)

    Special handling for:
    1. Message files - combines all conversations
    2. Time spent/sessions - loads posts_viewed and/or videos_watched
    """
    try:
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            # Get the list of file names in the zip file
            file_names = zip_ref.namelist()

            # Special handling for messages
            if file_key == "messages":
                # This is for messages - we need to find all message files
                all_messages_data = {"combined_messages": []}

                # Find all message files in the ZIP (look in both inbox and message_requests folders)
                message_files = []
                for name in file_names:
                    if name.endswith("message_1.json") and (
                        "/inbox/" in name or "/message_requests/" in name
                    ):
                        message_files.append(name)

                if not message_files:
                    print("No message files found")
                    return None, "message_1.json"

                for message_file in message_files:
                    try:
                        with zip_ref.open(message_file) as json_file:
                            json_content = json_file.read()
                            conversation_data = json.loads(json_content)

                            # Only process valid message files with participants
                            if (
                                "participants" in conversation_data
                                and len(conversation_data["participants"]) > 1
                                and "messages" in conversation_data
                            ):
                                # User is typically the second participant
                                user_name = conversation_data["participants"][1]["name"]

                                # Extract outgoing messages
                                for message in conversation_data["messages"]:
                                    if (
                                        message.get("sender_name") == user_name
                                        and "timestamp_ms" in message
                                    ):
                                        # Add to combined messages
                                        all_messages_data["combined_messages"].append(
                                            {
                                                "timestamp_ms": message["timestamp_ms"],
                                                "sender_name": "user1",  # Anonymize
                                                "conversation": message_file.split("/")[
                                                    -2
                                                ],  # Get conversation ID
                                            }
                                        )
                    except Exception as e:
                        print(f"Error reading message file {message_file}: {e}")
                        continue

                return all_messages_data, "message_1.json"

            # Special handling for time_spent and session_frequency which need posts_viewed and/or videos_watched
            if file_key == "time_spent" or file_key == "session_frequency":
                # We need to load either or both files
                posts_viewed_data = None
                videos_watched_data = None

                # Find and load posts_viewed.json
                for file_name in file_names:
                    if file_name.endswith(".json") and "posts_viewed" in file_name:
                        try:
                            with zip_ref.open(file_name) as json_file:
                                json_content = json_file.read()
                                posts_viewed_data = json.loads(json_content)
                                break
                        except Exception as e:
                            print(f"Error reading posts_viewed file {file_name}: {e}")

                # Find and load videos_watched.json
                for file_name in file_names:
                    if file_name.endswith(".json") and "videos_watched" in file_name:
                        try:
                            with zip_ref.open(file_name) as json_file:
                                json_content = json_file.read()
                                videos_watched_data = json.loads(json_content)
                                break
                        except Exception as e:
                            print(f"Error reading videos_watched file {file_name}: {e}")

                # Combine the data for the extraction function - work with either or both files
                if posts_viewed_data or videos_watched_data:
                    combined_data = {
                        "posts_viewed": posts_viewed_data or {},
                        "videos_watched": videos_watched_data or {},
                    }
                    return combined_data, "combined_viewing_data"
                else:
                    print("Could not find posts_viewed or videos_watched files")
                    return None, "combined_viewing_data"

            # Regular handling for search history
            if file_key == "search_history":
                for file_name in file_names:
                    if (
                        file_name.endswith(".json")
                        and "word_or_phrase_searches" in file_name
                    ):
                        try:
                            with zip_ref.open(file_name) as json_file:
                                json_content = json_file.read()
                                data = json.loads(json_content)
                                return data, "word_or_phrase_searches"
                        except Exception as e:
                            print(f"Error reading search file {file_name}: {e}")

            # Regular handling for other files
            for pattern in patterns:
                for file_name in file_names:
                    if file_name.endswith(".json") and pattern in file_name:
                        try:
                            # Read the JSON file
                            with zip_ref.open(file_name) as json_file:
                                json_content = json_file.read()
                                data = json.loads(json_content)
                                return data, pattern
                        except Exception as e:
                            print(f"Error reading file {file_name}: {e}")
                            continue  # Try the next matching file if there's an error

            # If we've checked all files and found no match
            print(f"No file matching pattern '{patterns}' found for key '{file_key}'")
            return None, None

    except Exception as e:
        print(f"Error extracting Instagram content: {e}")
        return None, None


def extract_linkedin_content_from_zip_folder(zip_file_path, patterns):
    """
    Extract content from LinkedIn data export zip file
    """
    try:
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            # Get the list of file names in the zip file
            file_names = zip_ref.namelist()

            # Look for matching files
            for pattern in patterns:
                # Create a list of matching files - use exact matching to avoid partial matches
                matching_files = []

                for file_name in file_names:
                    # Get just the filename (without directory)
                    base_name = file_name.split("/")[-1]

                    # Only match if the base name is exactly the pattern
                    if base_name == pattern:
                        matching_files.append(file_name)

                # If no exact matches, see if there are any files that end with the pattern
                if not matching_files:
                    for file_name in file_names:
                        if file_name.endswith("/" + pattern):
                            matching_files.append(file_name)

                # Process the first matching file we found
                for file_name in matching_files:
                    try:
                        # Read the CSV
                        with zip_ref.open(file_name) as csv_file:
                            # Handle notes section in LinkedIn CSV files
                            peek = csv_file.read(50).decode("utf-8", errors="ignore")
                            csv_file.seek(0)

                            if "Notes:" in peek:
                                # Skip notes lines until we find the header
                                lines = []
                                for line in csv_file:
                                    decoded = line.decode("utf-8", errors="ignore")
                                    if "First Name" in decoded or "Email" in decoded:
                                        lines.append(decoded)
                                        break

                                # Read the rest of the file
                                for line in csv_file:
                                    lines.append(line.decode("utf-8", errors="ignore"))

                                # Create CSV from cleaned data
                                from io import StringIO

                                csv_data = StringIO("".join(lines))
                                return pd.read_csv(csv_data), pattern
                            else:
                                # No notes, read directly
                                return pd.read_csv(csv_file), pattern
                    except Exception as e:
                        print(f"Error reading file {file_name}: {e}")
                        continue  # Try the next matching file if there's an error

            # If we've checked all files and found no match
            print(f"No file matching pattern '{patterns}' found")
            return None, None

    except Exception as e:
        print(f"Error extracting LinkedIn content: {e}")
        return None, None


def extract_youtube_content_from_zip_folder(zip_file_path, patterns):
    """
    Extract content from YouTube data export zip file using exact filenames
    """
    try:
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            # Get the list of file names in the zip file
            file_names = zip_ref.namelist()

            # Look for matching files
            for pattern in patterns:
                for file_name in file_names:
                    if pattern in file_name:
                        try:
                            # Process based on file extension
                            if file_name.endswith(".json"):
                                with zip_ref.open(file_name) as json_file:
                                    json_content = json_file.read()
                                    return json.loads(json_content), pattern
                            elif file_name.endswith(".csv"):
                                with zip_ref.open(file_name) as csv_file:
                                    return pd.read_csv(csv_file), pattern
                        except Exception as e:
                            print(f"Error reading file {file_name}: {e}")
                            continue  # Try the next matching file if there's an error

            # If we've checked all files and found no match
            print(f"No file matching pattern '{patterns}' found")
            return None, None

    except Exception as e:
        print(f"Error extracting YouTube content: {e}")
        return None, None


############################
# Render pages used in step 1
############################

# Define here for nicer capitalization
platform_names = {
    "instagram": "Instagram",
    "linkedin": "LinkedIn",
    "youtube": "YouTube",
}


def prompt_file(extensions):
    description = props.Translatable(
        {
            "en": "Please select your data export file. The file should be a ZIP file.",
            "de": "Wählen Sie Ihre heruntergeladene Datei. Die Datei sollte eine ZIP-Datei sein.",
            "nl": "Selecteer een zip-bestand.",
        }
    )

    return props.PropsUIPromptFileInput(description, extensions)


def render_donation_page(body, platform):
    # Use platform name (default to Instagram if not specified)

    header = props.PropsUIHeader(
        props.Translatable(
            {
                "en": f"Your {platform_names.get(platform, platform)} Data Donation",
                "de": f"Ihre {platform_names.get(platform, platform)} Datenspende",
                "nl": f"{platform_names.get(platform, platform)} Data Donation",
            }
        )
    )

    page = props.PropsUIPageDataSubmission(platform, header, body)
    return CommandUIRender(page)


def retry_confirmation_no_json(platform):
    if platform == "instagram":
        text = props.Translatable(
            {
                "en": 'Unfortunately, we cannot process your file. It seems like you submitted a HTML file of your Instagram data.\nPlease download your data from Instagram again and select the data format "JSON".',
                "de": 'Leider können wir Ihre Datei nicht verarbeiten. Es scheint so, dass Sie aus Versehen die HTML-Version Ihrer Instagram-Daten beantragt haben.\nBitte beantragen Sie erneut eine Datenspende bei Instagram und wählen Sie dabei "JSON" als Dateivormat aus (wie in der Anleitung beschrieben).',
                "nl": 'Helaas, kunnen we uw bestand niet verwerken. Het lijkt erop dat u een HTML-bestand van uw Instagram-gegevens heeft ingediend.\nDownload uw gegevens opnieuw van Instagram en selecteer het gegevensformaat "JSON".',
            }
        )
    elif platform == "linkedin":
        text = props.Translatable(
            {
                "en": "It seems that you have uploaded the incomplete data package that you received from LinkedIn after just 10 minutes. For this data donation, we kindly ask you to provide us with the data package that you normally receive after 24 hours. Please upload this complete data package.",
                "de": "Es scheint als haben Sie das unvollständige Datenpaket hochgeladen, dass Sie von LinkedIn bereits nach 10 Minuten bekommen haben. Für diese Datenspende bitten Sie wir uns das Datenpaket zu spenden, dass Sie normalerweise nach 24 Stunden erhalten.\nBitte laden Sie dieses vollständige Datenpaket noch.",
                "nl": "Het lijkt erop dat u het onvolledige datapakket heeft geüpload dat u van LinkedIn al na 10 minuten heeft ontvangen. Voor deze datadonatie vragen wij u vriendelijk om ons het datapakket te doneren dat u normaal gesproken na 24 uur ontvangt. Gelieve dit volledige datapakket te uploaden.",
            }
        )
    elif platform == "youtube":
        text = props.Translatable(
            {
                "en": 'Unfortunately, we cannot process your file. It seems that you accidentally requested the HTML version of your YouTube data. Please request a data donation from YouTube again and select "JSON" as the file format for the watch history (as described in the instructions).',
                "de": 'Leider können wir Ihre Datei nicht verarbeiten. Es scheint so, dass Sie aus Versehen die HTML-Version Ihrer YouTube-Daten beantragt haben.\nBitte beantragen Sie erneut eine Datenspende bei YouTube und wählen Sie dabei "JSON" als Dateivormat für den Wiedergabeverlauf aus (wie in der Anleitung beschrieben).',
                "nl": 'Het spijt ons, maar we kunnen uw bestand niet verwerken. Het lijkt erop dat u per ongeluk de HTML-versie van uw YouTube-gegevens heeft aangevraagd. Vraag alstublieft opnieuw een datadonatie aan bij YouTube en kies "JSON" als bestandsformaat voor de kijkgeschiedenis (zoals in de instructies beschreven).',
            }
        )

    ok = props.Translatable(
        {
            "en": "Try again with correct file",
            "de": "Erneut versuchen mit richtigen Daten",
            "nl": "Probeer opnieuw",
        }
    )

    return props.PropsUIPromptConfirm(text, ok)


def retry_confirmation_no_ddp(platform):
    text = props.Translatable(
        {
            "en": f"Unfortunately, we cannot process your file. Did you really select your downloaded {platform_names.get(platform, platform)} ZIP file?",
            "de": f"Leider können wir Ihre Datei nicht verarbeiten. Haben Sie wirklich Ihre {platform_names.get(platform, platform)}-Daten ausgewählt?",
            "nl": f"Helaas, kunnen we uw bestand niet verwerken. Weet u zeker dat u het juiste {platform_names.get(platform, platform)} bestand heeft gekozen?",
        }
    )

    ok = props.Translatable(
        {"en": "Try again", "de": "Erneut versuchen", "nl": "Probeer opnieuw"}
    )

    return props.PropsUIPromptConfirm(text, ok)


def retry_confirmation_unknown_platform():
    text = props.Translatable(
        {
            "en": "We could not identify the platform of your data file. Please make sure you have selected a ZIP file from the platform you requested your data from.",
            "de": "Wir konnten die Plattform Ihrer Datei nicht identifizieren. Bitte stellen Sie sicher, dass Sie eine ZIP-Datei von der angefragten Platform ausgewählt haben.",
            "nl": "We konden het platform van uw gegevensexportbestand niet identificeren. Zorg ervoor dat u een ZIP-bestand van platform.",
        }
    )

    ok = props.Translatable(
        {"en": "Try again", "de": "Erneut versuchen", "nl": "Probeer opnieuw"}
    )

    return props.PropsUIPromptConfirm(text, ok)


def prompt_extraction_message(message, percentage):
    description = props.Translatable(
        {
            "en": "One moment please. Information is now being extracted from the selected file.",
            "de": "Einen Moment bitte. Es werden nun Informationen aus der ausgewählten Datei extrahiert.",
            "nl": "Een moment geduld. Informatie wordt op dit moment uit het geselecteerde bestaand gehaald.",
        }
    )
    return props.PropsUIPromptProgress(description, message, percentage)


############################
# Render pages and functions used in step 2
############################


# Main content of consent page: display all extracted data
def prompt_consent(data, meta_data, locale, platform="Instagram"):
    print(meta_data)

    table_list = []

    # Initialize a list to store binary data (title and value pairs)
    binary_data = []

    if data is not None:  # can happen if user submits wrong file and still continues
        # Get the appropriate extraction dictionary based on platform
        if platform == "instagram":
            extraction_dict = instagram_extraction_dict
        elif platform == "linkedin":
            extraction_dict = linkedin_extraction_dict
        elif platform == "youtube":
            extraction_dict = youtube_extraction_dict
        else:
            # If platform is unknown, we can't process the data
            extraction_dict = {}

        for i, (file, description) in enumerate(extraction_dict.items()):
            df = data[i]
            # Check if the dataframe has only one row
            if len(df) == 1:
                # Extract the title from the translation
                translated_title = description["title"][locale]
                # Combine values from all columns into a single string
                combined_value = " |> ".join(
                    [f"{col}: {df.iloc[0][col]}" for col in df.columns]
                )
                binary_data.append([translated_title, combined_value])
            else:
                # Directly add multi-row dataframes to the table list
                table = props.PropsUIPromptConsentFormTable(
                    file,
                    props.Translatable({"en": file, "de": file, "nl": file}),
                    props.Translatable(description["title"]),
                    df,
                )
                table_list.append(table)

        # Create a dataframe for binary data if there are any single-row entries
        if binary_data:
            binary_df = pd.DataFrame(binary_data, columns=["Kategorie", "Daten"])
            table = props.PropsUIPromptConsentFormTable(
                "binary_results",
                props.Translatable(
                    {
                        "en": "Additional information",
                        "de": "Zusätzliche Informationen",
                        "nl": "Additional information",
                    }
                ),
                props.Translatable(
                    {
                        "en": f"Overview of additional {platform_names.get(platform, platform)} data",
                        "de": f"Übersicht von zusätzlichen {platform_names.get(platform, platform)} Informationen",
                        "nl": f"Binary {platform_names.get(platform, platform)} data",
                    }
                ),
                binary_df,
            )
            table_list.append(table)

    blocks = [
            props.PropsUIPromptConsentFormTable(
                table.id,
                table.title,
                table.description,
                table.data_frame,
            )
            for table in table_list
        ]
    # Create donation buttons
    blocks.append(
        props.PropsUIDataSubmissionButtons(
                    donate_question=props.Translatable(
                         {
                            "en": f"Do you want to donate the above {platform_names.get(platform, platform)} data?",
                            "de": f"Möchten Sie die obigen {platform_names.get(platform, platform)}-Daten spenden?",
                            "nl": f"Wilt u de bovenstaande {platform_names.get(platform, platform)} gegevens doneren?",
                        }
                    ),
                    donate_button=props.Translatable(
                        {
                            "en": "Yes, donate",
                            "de": "Ja, spenden",
                            "nl": "Ja, doneren",
                        }
                    ),
                ),
    )
    return blocks


# pass on user decision to donate or decline donation
def donate(key, json_string):
    return CommandSystemDonate(key, json_string)
