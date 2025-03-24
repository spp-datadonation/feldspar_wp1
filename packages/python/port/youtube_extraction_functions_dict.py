import port.youtube_extraction_functions as ef

# defines which extraction functions are used and what titles are displayed
# dict-keys are the exact filenames found in the YouTube export

extraction_dict = {
    "watch_history": {
        "extraction_function": ef.extract_watch_history,
        "patterns": ["Wiedergabeverlauf.json", "watch-history.json"],
        "title": {
            "en": "How many videos have you watched per day?",
            "de": "Wie viele Videos haben Sie pro Tag angesehen?",
            "nl": "Hoeveel video's heb je per dag bekeken?",
        },
    },
    "subscriptions": {
        "extraction_function": ef.extract_subscriptions,
        "patterns": ["Abos.csv", "subscriptions.csv"],
        "title": {
            "en": "Which channels are you subscribed to?",
            "de": "Welche Kanäle haben Sie abonniert?",
            "nl": "Op welke kanalen ben je geabonneerd?",
        },
    },
}
