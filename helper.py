def get_native_language_name(english_text):
    language_map = {
        'Tamil': 'தமிழ்',
        'Hindi': 'हिन्दी',
        'Telugu': 'తెలుగు',
        'Malayalam': 'മലയാളം',
        'Kannada': 'ಕನ್ನಡ',
        'Bengali': 'বাংলা',
        'Marathi': 'मराठी',
        'Punjabi': 'ਪੰਜਾਬੀ',
        'Gujarati': 'ગુજરાતી',
        'Urdu': 'اردو',
        'English': 'English',  # English stays the same
        # Add more as needed
    }

    return language_map.get(english_text.strip().capitalize(), english_text)


