import port.linkedin_extraction_functions as ef

# defines which extraction functions are used and what titles are displayed
# dict-keys are the exact filenames found in the LinkedIn export

extraction_dict = {
    "connections": {
        "extraction_function": ef.extract_connections,
        "patterns": ["Connections.csv"],
        "title": {
            "en": "How many connections have you made per day and what information do they have?",
            "de": "Wie viele Verbindungen haben Sie pro Tag hergestellt und welche Informationen haben diese?",
            "nl": "Hoeveel connecties heb je per dag gemaakt en welke informatie hebben ze?",
        },
    },
    "messages": {
        "extraction_function": ef.extract_messages,
        "patterns": ["messages.csv"],
        "title": {
            "en": "How many messages have you exchanged per day and with how many people?",
            "de": "Wie viele Nachrichten haben Sie pro Tag ausgetauscht und mit wie vielen Personen?",
            "nl": "Hoeveel berichten heb je per dag uitgewisseld en met hoeveel mensen?",
        },
    },
    "interests": {
        "extraction_function": ef.extract_interests,
        "patterns": ["Ad_Targeting.csv"],
        "title": {
            "en": "What interests has LinkedIn inferred about you?",
            "de": "Welche Interessen hat LinkedIn über Sie abgeleitet?",
            "nl": "Welke interesses heeft LinkedIn over je afgeleid?",
        },
    },
}
