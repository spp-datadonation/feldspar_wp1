import port.instagram_extraction_functions as ef

# defines which extraction functions are used and what titles are displayed
# dict-keys are names of files or paths to that file if filename in path (like in personal_information/personal_information)

extraction_dict = {
    "ads_seen": {
        "extraction_function": ef.extract_ads_seen,
        "patterns": ["ads_viewed"],
        "title": {
            "en": "How often did you see ads? [per day]",
            "de": "Wie oft haben Sie Werbung angesehen? [pro Tag]",
            "nl": "Hoe vaak heb je advertenties gezien? [per dag]",
        },
    },
    "ads_clicked": {
        "extraction_function": ef.extract_ads_clicked,
        "patterns": ["ads_clicked"],
        "title": {
            "en": "On how many ads did you click? [per day]",
            "de": "Wie oft haben Sie Werbung angeklickt? [pro Tag]",
            "nl": "Hoeveel productnamen (advertenties) heb je aangeklikt? [per dag]",
        },
    },
    "recently_viewed_items": {
        "extraction_function": ef.extract_recently_viewed_items,
        "patterns": ["recently_viewed_items"],
        "title": {
            "en": "Which shopping items have you recently viewed?",
            "de": "Welche Einkaufsartikel haben Sie sich kürzlich angesehen?",
            "nl": "Welke winkelartikelen heb je onlangs bekeken?",
        },
    },
    "posts_seen": {
        "extraction_function": ef.extract_posts_seen,
        "patterns": ["posts_viewed"],
        "title": {
            "en": "How often did you view posts? [per day]",
            "de": "Wie oft haben Sie Posts angesehen? [pro Tag]",
            "nl": "Hoe vaak heb je berichten bekeken? [per dag]",
        },
    },
    "videos_seen": {
        "extraction_function": ef.extract_videos_seen,
        "patterns": ["videos_watched"],
        "title": {
            "en": "How often did you watch Reels and Story videos? [per day]",
            "de": "Wie oft haben Sie Reels und Story-Videos gesehen? [pro Tag]",
            "nl": "Hoe vaak heb je Reels en Story-video's bekeken? [per dag]",
        },
    },
    "paid_subscription": {
        "extraction_function": ef.extract_paid_subscription,
        "patterns": ["subscription_for_no_ads"],
        "title": {
            "en": "Do you use Instagram's paid subscription option that doesn't show you ads?",
            "de": "Nutzen Sie Instagrams kostenpflichtige Abo-Option, mit der Ihnen keine Werbeinhalte angezeigt werden?",
            "nl": "Gebruik je Instagram's betaalde abonnementsoptie die geen advertenties weergeeft?",
        },
    },
    "blocked_profiles": {
        "extraction_function": ef.extract_blocked_profiles,
        "patterns": ["blocked_profiles"],
        "title": {
            "en": "How often did you block or restrict other Instagram profiles? [per day]",
            "de": "Wie oft haben Sie andere Instagramkonten blockiert oder eingeschränkt? [pro Tag]",
            "nl": "Hoe vaak heb je andere Instagram-accounts geblokkeerd of beperkt? [per dag]",
        },
    },
    "restricted_profiles": {
        "extraction_function": ef.extract_restricted_profiles,
        "patterns": ["restricted_profiles"],
        "title": {
            "en": "How often did you restrict profiles? [per day]",
            "de": "Wie oft haben Sie Konten eingeschränkt? [pro Tag]",
            "nl": "Hoe vaak heb je accounts beperkt? [per dag]",
        },
    },
    "post_comments": {
        "extraction_function": ef.extract_post_comments,
        "patterns": ["post_comments_1"],
        "title": {
            "en": "How often did you comment on posts? [per day]",
            "de": "Wie oft haben Sie Beiträge kommentiert? [pro Tag]",
            "nl": "Hoe vaak heb je op berichten gereageerd? [per dag]",
        },
    },
    "reel_comments": {
        "extraction_function": ef.extract_reel_comments,
        "patterns": ["reels_comments"],
        "title": {
            "en": "How often did you comment on reels? [per day]",
            "de": "Wie oft haben Sie Reels kommentiert? [pro Tag]",
            "nl": "Hoe vaak heb je op reels gereageerd? [per dag]",
        },
    },
    "posts_liked": {
        "extraction_function": ef.extract_posts_liked,
        "patterns": ["liked_posts"],
        "title": {
            "en": "How often did you like posts? [per day]",
            "de": 'Wie oft haben Sie Beiträge "geliked"? [pro Tag]',
            "nl": "Hoe vaak heb je op berichten geliked? [per dag]",
        },
    },
    "stories_liked": {
        "extraction_function": ef.extract_stories_liked,
        "patterns": ["story_likes"],
        "title": {
            "en": "How often did you like a story? [per day]",
            "de": 'Wie oft haben Sie eine Story "geliked"? [pro Tag]',
            "nl": "Hoe vaak heb je een story geliked? [per dag]",
        },
    },
    "comments_liked": {
        "extraction_function": ef.extract_comments_liked,
        "patterns": ["liked_comments"],
        "title": {
            "en": "How often did you like comments? [per day]",
            "de": 'Wie oft haben Sie Kommentare "geliked"? [pro Tag]',
            "nl": "Hoe vaak heb je op reacties geliked? [per dag]",
        },
    },
    "story_interaction_countdowns": {
        "extraction_function": ef.extract_story_interaction_countdowns,
        "patterns": ["countdowns"],
        "title": {
            "en": "How often did you react to a countdown in a story? [per day]",
            "de": "Wie oft haben Sie auf einen Countdown in einer Story reagiert? [pro Tag]",
            "nl": "Hoe vaak heb je gereageerd op een aftelklok in een story? [per dag]",
        },
    },
    "story_interaction_emoji_sliders": {
        "extraction_function": ef.extract_story_interaction_emoji_sliders,
        "patterns": ["emoji_sliders"],
        "title": {
            "en": "How often did you react to an emoji slider in a story? [per day]",
            "de": "Wie oft haben Sie auf einen Emoji-Slider in einer Story reagiert? [pro Tag]",
            "nl": "Hoe vaak heb je gereageerd op een emoji-slider in een story? [per dag]",
        },
    },
    "story_interaction_polls": {
        "extraction_function": ef.extract_story_interaction_polls,
        "patterns": ["polls"],
        "title": {
            "en": "How often did you react to a poll in a story? [per day]",
            "de": "Wie oft haben Sie auf eine Umfrage in einer Story reagiert? [pro Tag]",
            "nl": "Hoe vaak heb je gereageerd op een poll in een story? [per dag]",
        },
    },
    "story_interaction_questions": {
        "extraction_function": ef.extract_story_interaction_questions,
        "patterns": ["questions"],
        "title": {
            "en": "How often did you answer a question in a story? [per day]",
            "de": "Wie oft haben Sie eine Frage in einer Story beantwortet? [pro Tag]",
            "nl": "Hoe vaak heb je een vraag in een story beantwoord? [per dag]",
        },
    },
    "story_interaction_quizzes": {
        "extraction_function": ef.extract_story_interaction_quizzes,
        "patterns": ["quizzes"],
        "title": {
            "en": "How often did you answer a quiz in a story? [per day]",
            "de": "Wie oft haben Sie ein Quiz in einer Story beantwortet? [pro Tag]",
            "nl": "Hoe vaak heb je dag een quiz in een story beantwoord? [per dag]",
        },
    },
    "posts_created": {
        "extraction_function": ef.extract_posts_created,
        "patterns": ["posts_1"],
        "title": {
            "en": "How often did you post and did you include location information?  [per day]",
            "de": "Wie oft haben Sie Posts veröffentlicht und haben Sie Standortinformationen hinzugefügt? [pro Tag]",
            "nl": "Hoe vaak heb je gepost en heb je locatie-informatie toegevoegd? [per dag]",
        },
    },
    "stories_created": {
        "extraction_function": ef.extract_stories_created,
        "patterns": ["stories"],
        "title": {
            "en": "How often did you post stories and did you include location information? [per day]",
            "de": "Wie oft haben Sie Stories gepostet und haben Sie Standortinformationen hinzugefügt? [pro Tag]",
            "nl": "Hoe vaak heb je stories gepost en heb je locatie-informatie toegevoegd? [per dag]",
        },
    },
    "reels_created": {
        "extraction_function": ef.extract_reels_created,
        "patterns": ["content/reels"],
        "title": {
            "en": "How often did you post reels? [per day]",
            "de": "Wie oft haben Sie Reels gepostet? [pro Tag]",
            "nl": "Hoe vaak heb je reels gepost? [per dag]",
        },
    },
    "followers_new": {
        "extraction_function": ef.extract_followers_accepted,
        "patterns": ["followers_1"],
        "title": {
            "en": "How often did you gain new followers? [per day]",
            "de": "Wie oft haben Sie neue Follower? [pro Tag]",
            "nl": "Hoe vaak heb je nieuwe volgers gekregen? [per dag]",
        },
    },
    "??? MESSAGES ???": {
        "extraction_function": ef.extract_contact_syncing,
        "patterns": ["XXX"],
        "title": {
            "en": "",
            "de": "Wie oft haben Sie mit anderen Menschen auf Instagram geschrieben? [pro Tag]",
            "nl": "",
        },
    },
    "??? SEARCH HISTORY ???": {
        "extraction_function": ef.extract_contact_syncing,
        "patterns": ["XXX"],
        "title": {
            "en": "",
            "de": "Wie oft haben Sie nach etwas gesucht? [pro Tag]",
            "nl": "",
        },
    },
    "contact_syncing": {
        "extraction_function": ef.extract_contact_syncing,
        "patterns": ["instagram_profile_information"],
        "title": {
            "en": "Have you enabled contact syncing?",
            "de": "Haben Sie die Kontaktsynchronisierung aktiviert?",
            "nl": "Heb je contact synchronisatie ingeschakeld?",
        },
    },
    "personal_information": {
        "extraction_function": ef.extract_personal_information,
        "patterns": ["personal_information/personal_information.json"],
        "title": {
            "en": "Do you have a profile image, email, phone, a private account, and do you use your real name?",
            "de": "Haben Sie ein Profilbild, E-Mail, Telefon, und ein privates Konto? Verwenden Sie einen echten Namen?",
            "nl": "Heb je een profielfoto, e-mail, telefoon, een privéaccount en gebruik je je echte naam?",
        },
    },
    "topic_interests": {
        "extraction_function": ef.extract_topic_interests,
        "patterns": ["your_topics"],
        "title": {
            "en": "What are your Topics inferred by Instagram?",
            "de": "Was sind Ihre, von Instagram abgeleiteten, Themen?",
            "nl": "Je onderwerpen afgeleid door Instagram?",
        },
    },
    "login_activity": {
        "extraction_function": ef.extract_login_activity,
        "patterns": ["login_activity"],
        "title": {
            "en": "When and with which user agent did you log in to Instagram?",
            "de": "Wann und mit welchem Gerät haben Sie sich bei Instagram angemeldet?",
            "nl": "Wanneer en met welke user-agent heb je ingelogd op Instagram?",
        },
    },
    "logout_activity": {
        "extraction_function": ef.extract_logout_activity,
        "patterns": ["logout_activity"],
        "title": {
            "en": "When and with which user agent did you log out of Instagram?",
            "de": "Wann und mit welchem Gerät haben Sie sich Instagram abgemeldet?",
            "nl": "Wanneer en met welke user agent heb je uitgelogd op Instagram?",
        },
    },
}
