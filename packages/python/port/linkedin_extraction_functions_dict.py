import port.linkedin_extraction_functions as ef

# defines which extraction functions are used and what titles are displayed
# patterns are the exact filenames found in the LinkedIn export

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
    "comments": {
        "extraction_function": ef.extract_comments,
        "patterns": ["Comments.csv"],
        "title": {
            "en": "How many comments have you made per day?",
            "de": "Wie viele Kommentare haben Sie pro Tag geschrieben?",
            "nl": "Hoeveel reacties heeft u per dag geplaatst?",
        },
    },
    "reactions": {
        "extraction_function": ef.extract_reactions,
        "patterns": ["Reactions.csv"],
        "title": {
            "en": "What types of reactions have you given and how often per day?",
            "de": "Welche Arten von Reaktionen haben Sie gegeben und wie oft pro Tag?",
            "nl": "Welke soorten reacties heb je gegeven en hoe vaak per dag?",
        },
    },
    "shares": {
        "extraction_function": ef.extract_shares,
        "patterns": ["Shares.csv"],
        "title": {
            "en": "How many posts have you shared per day?",
            "de": "Wie viele Beiträge haben Sie pro Tag geteilt?",
            "nl": "Hoeveel berichten heeft u per dag gedeeld?",
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
    "search_queries": {
        "extraction_function": ef.extract_search_queries,
        "patterns": ["SearchQueries.csv"],
        "title": {
            "en": "How many searches have you performed per day?",
            "de": "Wie viele Suchanfragen haben Sie pro Tag durchgeführt?",
            "nl": "Hoeveel zoekopdrachten heb je per dag uitgevoerd?",
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
    "member_follows": {
        "extraction_function": ef.extract_member_follows,
        "patterns": ["Member_Follows.csv"],
        "title": {
            "en": "How many LinkedIn members have you followed/unfollowed per day?",
            "de": "Wie vielen LinkedIn-Mitgliedern sind Sie pro Tag gefolgt bzw. nicht mehr gefolgt?",
            "nl": "Hoeveel LinkedIn-leden bent u per dag gaan volgen/ontvolgen?",
        },
    },
    "profile": {
        "extraction_function": ef.extract_profile,
        "patterns": ["Profile.csv"],
        "title": {
            "en": "What information is included in your profile?",
            "de": "Welche Informationen sind in Ihrem Profil enthalten?",
            "nl": "Welke informatie is opgenomen in je profiel?",
        },
    },
    "positions": {
        "extraction_function": ef.extract_positions,
        "patterns": ["Positions.csv"],
        "title": {
            "en": "What details are included in your job positions?",
            "de": "Welche Details sind in Ihren beruflichen Positionen enthalten?",
            "nl": "Welke details zijn opgenomen in je werkposities?",
        },
    },
    "device_usage": {
        "extraction_function": ef.extract_device_usage,
        "patterns": ["Logins.csv"],
        "title": {
            "en": "What user agents have you used to access LinkedIn?",
            "de": "Mit welchen User Agents haben Sie auf LinkedIn zugegriffen?",
            "nl": "Welke user agents heb je gebruikt om toegang te krijgen tot LinkedIn?",
        },
    },
    "saved_jobs": {
        "extraction_function": ef.extract_saved_jobs,
        "patterns": ["Saved Jobs.csv"],
        "title": {
            "en": "How many jobs have you saved per day?",
            "de": "Wie viele Jobs haben Sie pro Tag gespeichert?",
            "nl": "Hoeveel vacatures heb je per dag opgeslagen?",
        },
    },
}
