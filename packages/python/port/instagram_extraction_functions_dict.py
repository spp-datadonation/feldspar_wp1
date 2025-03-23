import port.instagram_extraction_functions as ef

# defines which extraction functions are used and what titles are displayed
# dict-keys are names of files or paths to that file if filename in path (like in personal_information/personal_information)

extraction_dict = {
    "ads_clicked": {
        "extraction_function": ef.extract_ads_clicked,
        "title": {
            "en": "On how many ads did you click? [per day]",
            "de": "Wie oft haben Sie Werbung angeklickt? [pro Tag]",
            "nl": "Hoeveel productnamen (advertenties) heb je aangeklikt? [per dag]",
        },
    },
    "ads_viewed": {
        "extraction_function": ef.extract_ads_viewed,
        "title": {
            "en": "How often did you see ads? [per day]",
            "de": "Wie oft haben Sie Werbung angesehen? [pro Tag]",
            "nl": "Hoe vaak heb je advertenties gezien? [per dag]",
        },
    },
    "posts_viewed": {
        "extraction_function": ef.get_postViewsPerDay,
        "title": {
            "en": "How often did you view posts? [per day]",
            "de": "Wie oft haben Sie Posts angesehen? [pro Tag]",
            "nl": "Hoe vaak heb je berichten bekeken? [per dag]",
        },
    },
    "videos_watched": {
        "extraction_function": ef.get_videoViewsPerDay,
        "title": {
            "en": "How often did you watch Reels and Story videos? [per day]",
            "de": "Wie oft haben Sie Reels und Story-Videos gesehen? [pro Tag]",
            "nl": "Hoe vaak heb je Reels en Story-video's bekeken? [per dag]",
        },
    },
    "subscription_for_no_ads": {
        "extraction_function": ef.extract_subscription_for_no_ads,
        "title": {
            "en": "Do you use Instagram's paid subscription option that doesn't show you ads?",
            "de": "Nutzen Sie Instagrams kostenpflichtige Abo-Option, mit der Ihnen keine Werbeinhalte angezeigt werden?",
            "nl": "Gebruik je Instagram's betaalde abonnementsoptie die geen advertenties weergeeft?",
        },
    },
    "blocked_accounts": {
        "extraction_function": ef.extract_blocked_accounts,
        "title": {
            "en": "How often did you block or restrict other Instagram accounts? [per day]",
            "de": "Wie oft haben Sie andere Instagramkonten blockiert oder eingeschränkt? [pro Tag]",
            "nl": "Hoe vaak heb je andere Instagram-accounts geblokkeerd of beperkt? [per dag]",
        },
    },
    "close_friends": {
        "extraction_function": ef.extract_close_friends,
        "title": {
            "en": 'How often did you add followers as "close friends"? [per day]',
            "de": 'Wie oft haben Sie Follower als "enge Freunde" hinzugefügt? [pro Tag]',
            "nl": 'Hoe vaak heb je volgers toegevoegd als "goede vrienden"? [per dag]',
        },
    },
    "followers_1": {
        "extraction_function": ef.extract_followers_1,
        "title": {
            "en": "How often did you gain new followers? [per day]",
            "de": "Wie oft haben Sie neue Follower? [pro Tag]",
            "nl": "Hoe vaak heb je nieuwe volgers gekregen? [per dag]",
        },
    },
    "followers_and_following/following": {
        "extraction_function": ef.extract_following,
        "title": {
            "en": "How many accounts do you follow?",
            "de": "Wie vielen Konten folgen Sie?",
            "nl": "Hoeveel accounts volg je?",
        },
    },
    "follow_requests_you've_received": {
        "extraction_function": ef.extract_follow_requests_youve_received,
        "title": {
            "en": "How often did you receive follower requests? [per day]",
            "de": "Wie oft erhalten Sie Followeranfragen? [pro Tag]",
            "nl": "Hoe vaak heb je volgverzoeken ontvangen? [per dag]",
        },
    },
    "hide_story_from": {
        "extraction_function": ef.extract_hide_story_from,
        "title": {
            "en": "How many accounts did you hide your story from? [per day]",
            "de": "Für wie viele Konten verstecken Sie Ihre Story? [pro Tag]",
            "nl": "Hoe vaak heb je je verhaal verborgen voor accounts? [per dag]",
        },
    },
    "pending_follow_requests": {
        "extraction_function": ef.extract_pending_follow_requests,
        "title": {
            "en": "How often did you ignore follower requests? [per day]",
            "de": "Wie oft ignorieren Sie Followeranfragen? [pro Tag]",
            "nl": "Hoe vaak heb je volgverzoeken genegeerd? [per dag]",
        },
    },
    "recently_unfollowed_accounts": {
        "extraction_function": ef.extract_recently_unfollowed_accounts,
        "title": {
            "en": "How many accounts did you recently stop following? [per day]",
            "de": "Wie vielen Konten folgen Sie seit Kurzem nicht mehr? [pro Tag]",
            "nl": "Hoe vaak ben je recent accounts gestopt te volgen? [per dag]",
        },
    },
    "removed_suggestions": {
        "extraction_function": ef.extract_removed_suggestions,
        "title": {
            "en": "How often did you remove accounts from your suggestions? [per day]",
            "de": "Wie oft haben Sie Konten aus Ihren Vorschlägen entfernt? [pro Tag]",
            "nl": "Hoe vaak heb je accounts uit je suggesties verwijderd? [per dag]",
        },
    },
    "restricted_accounts": {
        "extraction_function": ef.extract_restricted_accounts,
        "title": {
            "en": "How often did you restrict accounts? [per day]",
            "de": "Wie oft haben Sie Konten eingeschränkt? [pro Tag]",
            "nl": "Hoe vaak heb je accounts beperkt? [per dag]",
        },
    },
    "notification_of_privacy_policy_updates": {
        "extraction_function": ef.extract_notification_of_privacy_policy_updates,
        "title": {
            "en": "When did you view updates to the Meta Privacy Policy?",
            "de": "Wann haben Sie die Updates der Meta-Datenschutzrichtlinie angesehen?",
            "nl": "Wanneer heb je updates van het Meta-privacybeleid bekeken?",
        },
    },
    "personal_information/account_information": {
        "extraction_function": ef.extract_account_information,
        "title": {
            "en": "Have you enabled contact syncing?",
            "de": "Haben Sie die Kontaktsynchronisierung aktiviert?",
            "nl": "Heb je contact synchronisatie ingeschakeld?",
        },
    },
    "linked_meta_accounts": {
        "extraction_function": ef.extract_linked_meta_accounts,
        "title": {
            "en": "Which accounts are connected at Meta?",
            "de": "Welche Ihrer Konten sind bei Meta verbunden?",
            "nl": "Welke accounts zijn verbonden bij Meta?",
        },
    },
    "personal_information/personal_information.json": {
        "extraction_function": ef.extract_personal_information,
        "title": {
            "en": "Do you have a profile image, email, phone, a private account, and do you use your real name?",
            "de": "Haben Sie ein Profilbild, E-Mail, Telefon, und ein privates Konto? Verwenden Sie einen echten Namen?",
            "nl": "Heb je een profielfoto, e-mail, telefoon, een privéaccount en gebruik je je echte naam?",
        },
    },
    "profile_changes": {
        "extraction_function": ef.extract_profile_changes,
        "title": {
            "en": "When did you change your personal information?",
            "de": "Wann haben Sie Ihre persönlichen Informationen geändert?",
            "nl": "Wanneer heb je je persoonlijke informatie gewijzigd?",
        },
    },
    "comments_allowed_from": {
        "extraction_function": ef.extract_comments_allowed_from,
        "title": {
            "en": "Which accounts do you allow comments from?",
            "de": "Von welchen Konten erlauben Sie Kommentare unter ihren Beiträgen?",
            "nl": "Van welke accounts sta je reacties toe?",
        },
    },
    "comments_blocked_from": {
        "extraction_function": ef.extract_comments_blocked_from,
        "title": {
            "en": "How many accounts did you block from commenting?",
            "de": "Wie viele Konten haben Sie blockiert, keine Kommentare mehr schreiben zu können?",
            "nl": "Hoe vaak heb je accounts geblokkeerd voor reacties?",
        },
    },
    "consents": {
        "extraction_function": ef.extract_consents,
        "title": {
            "en": "What did you agree to when?",
            "de": "Wozu haben Sie wann zugestimmt?",
            "nl": "Waarmee heb je wanneer ingestemd?",
        },
    },
    "use_cross-app_messaging": {
        "extraction_function": ef.extract_use_crossapp_messaging,
        "title": {
            "en": "Do you use the messenger for Facebook and Instagram?",
            "de": "Verwenden Sie einen gemeinsamen Messenger für Facebook und Instagram?",
            "nl": "Gebruik je de messenger voor Facebook en Instagram?",
        },
    },
    "your_topics": {
        "extraction_function": ef.extract_topics_df,
        "title": {
            "en": "What are your Topics inferred by Instagram?",
            "de": "Was sind Ihre, von Instagram abgeleiteten, Themen?",
            "nl": "Je onderwerpen afgeleid door Instagram?",
        },
    },
    "account_privacy_changes": {
        "extraction_function": ef.extract_account_privacy_changes,
        "title": {
            "en": "When did you switch your account to being public/private?",
            "de": "Wann haben Sie Ihr Konto auf öffentlich oder privat umgestellt?",
            "nl": "Wanneer heb je je account openbaar/privé gezet?",
        },
    },
    "login_activity": {
        "extraction_function": ef.extract_login_activity,
        "title": {
            "en": "When and with which user agent did you log in to Instagram?",
            "de": "Wann und mit welchem Gerät haben Sie sich bei Instagram angemeldet?",
            "nl": "Wanneer en met welke user-agent heb je ingelogd op Instagram?",
        },
    },
    "logout_activity": {
        "extraction_function": ef.extract_logout_activity,
        "title": {
            "en": "When and with which user agent did you log out of Instagram?",
            "de": "Wann und mit welchem Gerät haben Sie sich Instagram abgemeldet?",
            "nl": "Wanneer en met welke user agent heb je uitgelogd op Instagram?",
        },
    },
    "signup_information": {
        "extraction_function": ef.extract_signup_information,
        "title": {
            "en": "Did you use a real name to signup on Instagram?",
            "de": "Haben Sie einen echten Namen verwendet, um sich bei Instagram anzumelden?",
            "nl": "Heb je een echte naam gebruikt om je aan te melden bij Instagram?",
        },
    },
    "recently_viewed_items": {
        "extraction_function": ef.extract_recently_viewed_items,
        "title": {
            "en": "Which shopping items have you recently viewed?",
            "de": "Welche Einkaufsartikel haben Sie sich kürzlich angesehen?",
            "nl": "Welke winkelartikelen heb je onlangs bekeken?",
        },
    },
    "post_comments_1": {
        "extraction_function": ef.extract_post_comments_1,
        "title": {
            "en": "How often did you comment on posts? [per day]",
            "de": "Wie oft haben Sie Beiträge kommentiert? [pro Tag]",
            "nl": "Hoe vaak heb je op berichten gereageerd? [per dag]",
        },
    },
    "reels_comments": {
        "extraction_function": ef.extract_reels_comments,
        "title": {
            "en": "How often did you comment on reels? [per day]",
            "de": "Wie oft haben Sie Reels kommentiert? [pro Tag]",
            "nl": "Hoe vaak heb je op reels gereageerd? [per dag]",
        },
    },
    "archived_posts": {
        "extraction_function": ef.extract_archived_posts,
        "picture_info": None,
        "title": {
            "en": "How often did you archive posts and what information was included? [per day]",
            "de": "Wie oft haben Sie Beiträge archiviert und welche Informationen waren enthalten? [pro Tag]",
            "nl": "Hoe vaak heb je berichten gearchiveerd en welke informatie was inbegrepen? [per dag]",
        },
    },
    "posts_1": {
        "extraction_function": ef.extract_posts_1,
        "picture_info": None,
        "title": {
            "en": "How often did you post and what information was included? [per day]",
            "de": "Wie oft haben Sie Posts veröffentlicht und welche Informationen waren enthalten? [pro Tag]",
            "nl": "Hoe vaak heb je gepost en welke informatie was inbegrepen? [per dag]",
        },
    },
    "profile_photos": {
        "extraction_function": ef.extract_profile_photos,
        "picture_info": None,
        "title": {
            "en": "Do you use a face in your profile photo?",
            "de": "Verwenden Sie ein Gesicht in ihrem Profilfoto?",
            "nl": "Gebruik je een gezicht in je profielfoto?",
        },
    },
    "recently_deleted_content": {
        "extraction_function": ef.extract_recently_deleted_content,
        "picture_info": None,
        "title": {
            "en": "How often did you delete posts and what information was included? [per day]",
            "de": "Wie oft haben Sie Beiträge gelöscht und welche Informationen waren enthalten? [pro Tag]",
            "nl": "Hoe vaak heb je berichten verwijderd en welke informatie was inbegrepen? [per dag]",
        },
    },
    "content/reels": {
        "extraction_function": ef.extract_reels,
        "title": {
            "en": "How often did you post reels? [per day]",
            "de": "Wie oft haben Sie Reels gepostet? [pro Tag]",
            "nl": "Hoe vaak heb je reels gepost? [per dag]",
        },
    },
    "stories": {
        "extraction_function": ef.extract_stories,
        "picture_info": None,
        "title": {
            "en": "How often did you post stories and did you include location information? [per day]",
            "de": "Wie oft haben Sie Stories gepostet und haben Sie Standortinformationen hinzugefügt? [pro Tag]",
            "nl": "Hoe vaak heb je stories gepost en heb je locatie-informatie toegevoegd? [per dag]",
        },
    },
    "liked_comments": {
        "extraction_function": ef.extract_liked_comments,
        "title": {
            "en": "How often did you like comments? [per day]",
            "de": 'Wie oft haben Sie Kommentare "geliked"? [pro Tag]',
            "nl": "Hoe vaak heb je op reacties geliked? [per dag]",
        },
    },
    "liked_posts": {
        "extraction_function": ef.extract_liked_posts,
        "title": {
            "en": "How often did you like posts? [per day]",
            "de": 'Wie oft haben Sie Beiträge "geliked"? [pro Tag]',
            "nl": "Hoe vaak heb je op berichten geliked? [per dag]",
        },
    },
    "saved_collections": {
        "extraction_function": ef.extract_saved_collections,
        "title": {
            "en": "How often did you save posts or reels and shared it with someone? [per day]",
            "de": "Wie oft haben Sie Beiträge oder Reels gespeichert und mit jemandem geteilt? [pro Tag]",
            "nl": "Hoe vaak heb je berichten of reels opgeslagen en met iemand gedeeld? [per dag]",
        },
    },
    "saved_posts": {
        "extraction_function": ef.extract_saved_posts,
        "title": {
            "en": "How often did you save posts or reels? [per day]",
            "de": "Wie oft haben Sie Beiträge oder Reels gespeichert? [pro Tag]",
            "nl": "Hoe vaak heb je berichten of reels opgeslagen? [per dag]",
        },
    },
    "countdowns": {
        "extraction_function": ef.extract_countdowns,
        "title": {
            "en": "How often did you react to a countdown in a story? [per day]",
            "de": "Wie oft haben Sie auf einen Countdown in einer Story reagiert? [pro Tag]",
            "nl": "Hoe vaak heb je gereageerd op een aftelklok in een story? [per dag]",
        },
    },
    "emoji_sliders": {
        "extraction_function": ef.extract_emoji_sliders,
        "title": {
            "en": "How often did you react to an emoji slider in a story? [per day]",
            "de": "Wie oft haben Sie auf einen Emoji-Slider in einer Story reagiert? [pro Tag]",
            "nl": "Hoe vaak heb je gereageerd op een emoji-slider in een story? [per dag]",
        },
    },
    "polls": {
        "extraction_function": ef.extract_polls,
        "title": {
            "en": "How often did you react to a poll in a story? [per day]",
            "de": "Wie oft haben Sie auf eine Umfrage in einer Story reagiert? [pro Tag]",
            "nl": "Hoe vaak heb je gereageerd op een poll in een story? [per dag]",
        },
    },
    "questions": {
        "extraction_function": ef.extract_questions,
        "title": {
            "en": "How often did you answer a question in a story? [per day]",
            "de": "Wie oft haben Sie eine Frage in einer Story beantwortet? [pro Tag]",
            "nl": "Hoe vaak heb je een vraag in een story beantwoord? [per dag]",
        },
    },
    "quizzes": {
        "extraction_function": ef.extract_quizzes,
        "title": {
            "en": "How often did you answer a quiz in a story? [per day]",
            "de": "Wie oft haben Sie ein Quiz in einer Story beantwortet? [pro Tag]",
            "nl": "Hoe vaak heb je dag een quiz in een story beantwoord? [per dag]",
        },
    },
    "story_likes": {
        "extraction_function": ef.extract_story_likes,
        "title": {
            "en": "How often did you like a story? [per day]",
            "de": 'Wie oft haben Sie eine Story "geliked"? [pro Tag]',
            "nl": "Hoe vaak heb je een story geliked? [per dag]",
        },
    },
}
