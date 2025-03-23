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
        fileResult = yield render_donation_page(promptFile)

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
                    retry_confirmation_unknown_platform()
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

            elif check_ddp == "invalid_no_json":
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

                elif file_name_check_html in file_info.filename:
                    found_file_name_check_html = True

            if found_folder_name_check_ddp:
                if found_file_name_check_html:
                    print(
                        f"Folder '{folder_name_check_ddp}' found and file {file_name_check_html} found in the ZIP file. Seems like a Instagram HTML DDP."
                    )
                    return "invalid_no_json"

                else:
                    print(
                        f"Folder '{folder_name_check_ddp}' found and file {file_name_check_html} not found in the ZIP file. Seems like a real Instagram JSON DDP."
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


def check_if_valid_youtube_ddp(filename):
    """Check if the uploaded file is a valid YouTube data download package"""
    folder_name_check_ddp = "YouTube und YouTube Music"

    try:
        with zipfile.ZipFile(filename, "r") as zip_ref:
            found_folder_name_check_ddp = False

            for file_info in zip_ref.infolist():
                if folder_name_check_ddp in file_info.filename:
                    found_folder_name_check_ddp = True
                    break

            if found_folder_name_check_ddp:
                print(
                    f"Folder '{folder_name_check_ddp}' found in the ZIP file. Seems like a valid YouTube DDP."
                )
                return "valid"
            else:
                print(
                    f"Folder '{folder_name_check_ddp}' not found. Does not seem like a YouTube DDP."
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
    file_checks = ["Profile.csv", "Connections.csv"]  # Common LinkedIn export files

    try:
        with zipfile.ZipFile(filename, "r") as zip_ref:
            found_any_file = False

            for file_info in zip_ref.infolist():
                if any(check_file in file_info.filename for check_file in file_checks):
                    found_any_file = True
                    break

            if found_any_file:
                print(
                    f"LinkedIn files found in the ZIP file. Seems like a valid LinkedIn DDP."
                )
                return "valid"
            else:
                print(f"LinkedIn files not found. Does not seem like a LinkedIn DDP.")
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
    if platform.lower() == "instagram":
        extraction_dict = instagram_extraction_dict
        platform_name = "Instagram"
    elif platform.lower() == "linkedin":
        extraction_dict = linkedin_extraction_dict
        platform_name = "LinkedIn"
    elif platform.lower() == "youtube":
        extraction_dict = youtube_extraction_dict
        platform_name = "YouTube"

    for index, (file, v) in enumerate(extraction_dict.items(), start=1):
        # Extract content based on platform
        if platform.lower() == "instagram":
            file_content = extractInstagramContentFromZipFolder(filename, file)
        elif platform.lower() == "linkedin":
            file_content = extractLinkedInContentFromZipFolder(filename, file)
        elif platform.lower() == "youtube":
            file_content = extractYouTubeContentFromZipFolder(filename, file)
        else:
            file_content = None

        if file_content is not None:
            try:
                # Call the extraction function with content
                file_df = v["extraction_function"](file_content, locale)
            except Exception as e:
                # If extraction fails
                translatedMessage = props.Translatable(
                    {
                        "en": "extraction failed - ",
                        "de": "Extrahierung fehlgeschlagen - ",
                        "nl": "Extractie mislukt - ",
                    }
                )

                file_df = pd.DataFrame(
                    [
                        f"{translatedMessage.translations[locale]}{file, type(e).__name__}"
                    ],
                    columns=[str(file)],
                )
        else:
            translatedMessage1 = props.Translatable(
                {
                    "en": f'(file "{str(file)}" missing)',
                    "de": f'(Datei "{str(file)}" fehlt)',
                    "nl": f'(bestand "{str(file)}" ontbreekt)',
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


def extractInstagramContentFromZipFolder(zip_file_path, pattern):
    """Extract JSON content from Instagram data export zip file based on pattern"""
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        # Get the list of file names in the zip file
        file_names = zip_ref.namelist()

        file_json_dict = {}

        for file_name in file_names:
            if (file_name.endswith(".json")) and (pattern in file_name):
                try:
                    # Read the JSON file into a dictionary
                    with zip_ref.open(file_name) as json_file:
                        json_content = json_file.read()
                        data = json.loads(json_content)
                        file_json_dict[file_name] = data

                    break

                except:
                    return None

            # checks if loop is at last item
            if file_name == file_names[-1]:
                print(f"File {pattern}.json does not exist")
                return None

    return file_json_dict[file_name]


def extractLinkedInContentFromZipFolder(zip_file_path, exact_filename):
    """
    Extract content from LinkedIn data export zip file using exact filenames
    """
    try:
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            # Get the list of file names in the zip file
            file_names = zip_ref.namelist()

            # Check for exact match
            if exact_filename in file_names:
                file_path = exact_filename
            else:
                # Try to find the file in any directory
                matching_files = [
                    f for f in file_names if f.endswith("/" + exact_filename)
                ]
                if not matching_files:
                    print(f"No file found with name: {exact_filename}")
                    return None
                file_path = matching_files[0]

            # Process CSV file
            if file_path.endswith(".csv"):
                try:
                    with zip_ref.open(file_path) as csv_file:
                        # Skip the first line if it's a note
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
                            return pd.read_csv(csv_data)
                        else:
                            # No notes, read directly
                            return pd.read_csv(csv_file)

                except Exception as e:
                    print(f"Error reading CSV file {exact_filename}: {e}")
                    return pd.DataFrame()

            return None

    except Exception as e:
        print(f"Error extracting LinkedIn content: {e}")
        return None


def extractYouTubeContentFromZipFolder(zip_file_path, exact_filename):
    """
    Extract content from YouTube data export zip file using exact filenames
    """
    try:
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            # Get the list of file names in the zip file
            file_names = zip_ref.namelist()

            # Look for the exact filename in any directory
            matching_files = [f for f in file_names if f.endswith(exact_filename)]

            if not matching_files:
                print(f"No file found with name: {exact_filename}")
                return None

            # Use the first matching file
            file_path = matching_files[0]

            # Process based on file extension
            if file_path.endswith(".json"):
                with zip_ref.open(file_path) as json_file:
                    json_content = json_file.read()
                    return json.loads(json_content)
            elif file_path.endswith(".csv"):
                with zip_ref.open(file_path) as csv_file:
                    return pd.read_csv(csv_file)

            return None

    except Exception as e:
        print(f"Error extracting YouTube content: {e}")
        return None


############################
# Render pages used in step 1
############################


def prompt_file(extensions):
    description = props.Translatable(
        {
            "en": 'Please select your data export file from Instagram, LinkedIn, or YouTube. The file should be a ZIP file.\nFor Instagram, the file should be named like "instagram-username-date-random_combination.zip".\nFor LinkedIn, export your data from the LinkedIn privacy settings.\nFor YouTube, download your data from Google Takeout.\nThe data processing can take up to a minute. Please do NOT reload the page during this process.',
            "de": 'Wählen Sie Ihre heruntergeladene Datei von Instagram, LinkedIn oder YouTube aus. Die Datei sollte eine ZIP-Datei sein.\nFür Instagram sollte die Datei etwa so heißen: "instagram-ihr_nutzername-datum-zufallskombination.zip".\nFür LinkedIn exportieren Sie Ihre Daten aus den LinkedIn-Datenschutzeinstellungen.\nFür YouTube laden Sie Ihre Daten über Google Takeout herunter.',
            "nl": "Selecteer een zip-bestand van Instagram, LinkedIn of YouTube die u heeft opgeslagen op uw apparaat. De gegevensverwerking kan tot een minuut duren. Laad de pagina tijdens dit proces NIET opnieuw.",
        }
    )

    return props.PropsUIPromptFileInput(description, extensions)


def render_donation_page(body, platform="Instagram"):
    # Use platform name (default to Instagram if not specified)

    header = props.PropsUIHeader(
        props.Translatable(
            {
                "en": f"Your {platform} Data Donation",
                "de": f"Ihre {platform} Datenspende",
                "nl": f"{platform} Data Donation",
            }
        )
    )

    page = props.PropsUIPageDataSubmission(platform, header, body)
    return CommandUIRender(page)


def retry_confirmation_no_json(platform="Instagram"):
    text = props.Translatable(
        {
            "en": f'Unfortunately, we cannot process your file. It seems like you submitted a HTML file of your {platform} data.\nPlease download your data from {platform} again and select the data format "JSON".',
            "de": f'Leider können wir Ihre Datei nicht verarbeiten. Es scheint so, dass Sie aus Versehen die HTML-Version Ihrer {platform}-Daten beantragt haben.\nBitte beantragen Sie erneut eine Datenspende bei {platform} und wählen Sie dabei "JSON" als Dateivormat aus (wie in der Anleitung beschrieben).',
            "nl": f"Helaas, kunnen we uw bestand niet verwerken. Het lijkt erop dat u een HTML-bestand van uw {platform}-gegevens heeft ingediend.\nDownload uw gegevens opnieuw van {platform} en selecteer het gegevensformaat 'JSON'.",
        }
    )

    ok = props.Translatable(
        {
            "en": "Try again with JSON file",
            "de": "Erneut versuchen mit JSON-Datei",
            "nl": "Probeer opnieuw",
        }
    )

    return props.PropsUIPromptConfirm(text, ok)


def retry_confirmation_no_ddp(platform="Instagram"):
    text = props.Translatable(
        {
            "en": f"Unfortunately, we cannot process your file. Did you really select your downloaded {platform} ZIP file?",
            "de": f"Leider können wir Ihre Datei nicht verarbeiten. Haben Sie wirklich Ihre {platform}-Daten ausgewählt?",
            "nl": f"Helaas, kunnen we uw bestand niet verwerken. Weet u zeker dat u het juiste {platform} bestand heeft gekozen?",
        }
    )

    ok = props.Translatable(
        {"en": "Try again", "de": "Erneut versuchen", "nl": "Probeer opnieuw"}
    )

    return props.PropsUIPromptConfirm(text, ok)


def retry_confirmation_unknown_platform():
    text = props.Translatable(
        {
            "en": "We could not identify the platform of your data export file. Please make sure you have selected a ZIP file from Instagram, YouTube, or LinkedIn.",
            "de": "Wir konnten die Plattform Ihrer Datendatei nicht identifizieren. Bitte stellen Sie sicher, dass Sie eine ZIP-Datei von Instagram, YouTube oder LinkedIn ausgewählt haben.",
            "nl": "We konden het platform van uw gegevensexportbestand niet identificeren. Zorg ervoor dat u een ZIP-bestand van Instagram, YouTube of LinkedIn heeft geselecteerd.",
        }
    )

    ok = props.Translatable(
        {"en": "Try again", "de": "Erneut versuchen", "nl": "Probeer opnieuw"}
    )

    return props.PropsUIPromptConfirm(text, ok)


def retry_confirmation_platform_not_supported(platform):
    text = props.Translatable(
        {
            "en": f"Support for {platform} data extraction is not yet available. Please try uploading data from a different platform.",
            "de": f"Die Unterstützung für die Extraktion von {platform}-Daten ist noch nicht verfügbar. Bitte versuchen Sie, Daten von einer anderen Plattform hochzuladen.",
            "nl": f"Ondersteuning voor {platform} gegevensextractie is nog niet beschikbaar. Probeer gegevens van een ander platform te uploaden.",
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
    i = 0

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

        for file, v in extraction_dict.items():
            df = data[i]

            # Check if the dataframe has only one row
            if len(df) == 1:
                # Extract the title from the 'en' translation
                translated_title = v["title"][locale]
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
                    props.Translatable(v["title"]),
                    df,
                )
                table_list.append(table)

            i += 1

        # Create a dataframe for binary data if there are any single-row entries
        if binary_data:
            binary_df = pd.DataFrame(binary_data, columns=["Kategorie", "Daten"])
            table = props.PropsUIPromptConsentFormTable(
                "binary_results",
                props.Translatable(
                    {"en": "binary_results", "de": "Binäre Übersicht", "nl": "XXX"}
                ),
                props.Translatable(
                    {
                        "en": f"Overview of additional {platform} data",
                        "de": f"Übersicht von zusätzlichen {platform} Informationen",
                        "nl": f"Binary {platform} data",
                    }
                ),
                binary_df,
            )
            table_list.append(table)

    # Create donation buttons
    donation_question = props.Translatable(
        {
            "en": f"Do you want to donate the above {platform} data?",
            "de": f"Möchten Sie die obigen {platform}-Daten spenden?",
            "nl": f"Wilt u de bovenstaande {platform} gegevens doneren?",
        }
    )

    donate_button = props.Translatable(
        {
            "en": "Yes, donate",
            "de": "Ja, spenden",
            "nl": "Ja, doneren",
        }
    )

    return props.PropsUIPromptConsentForm(
        table_list,
        props.Translatable(
            {
                "en": f"Please review the extracted {platform} data below before donating.",
                "de": f"Bitte überprüfen Sie die extrahierten {platform}-Daten unten, bevor Sie spenden.",
                "nl": f"Bekijk de geëxtraheerde {platform} gegevens hieronder voordat u doneert.",
            }
        ),
        donation_question,
        donate_button,
    )


# pass on user decision to donate or decline donation
def donate(key, json_string):
    return CommandSystemDonate(key, json_string)
