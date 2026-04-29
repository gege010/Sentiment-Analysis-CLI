# Indonesian Slang & Emoticon Sentiment Lexicon
# Extends the HuggingFace model with local knowledge

POSITIVE_WORDS = {
    # Indonesian
    "bagus", "baik", "mantap", "keren", "sukses", "lancar", "sukses",
    "bangga", "suka", "senang", "gembira", "高兴", "hebat", "luar biasa",
    "terbaik", "awesome", "great", "good", "nice", "best", "amazing",
    "fantastic", "wonderful", "excellent", "love", "happy", "joy",
    "indahnya", "menyenangkan", "membanggakan", "alhamdulillah",
    "bestie", "sipp", "sip", "oke", "ok", "recommended", "worth it",
    "worth", "helped", "berhasil", "juara", "winner", "champion",
    "mantul", "jos", "gass", "gasskan", "cahya", "cemerlang",

    # Slang
    "ngotak", "joss", "mantep", "keren", "asik", "asyik",
    "gile", "gila", "banging", "pol", "mantab", "m强的",

    # Emoticons
    ":)", ":-)", ":D", ":-D", "=)", "^_^", ":))", ":P", ";-)", "<3",
    "❤", "💕", "👍", "👏", "🎉", "🔥", "✨", "💯", "🙌",
}

NEGATIVE_WORDS = {
    # Indonesian
    "buruk", "jelek", "gagal", "salah", " buruk", "busuk", "kecewa",
    "sedih", "marah", "kesal", "benci", "takut", "cemas", "khawatir",
    "bad", "worse", "worst", "terrible", "awful", "horrible", "hate",
    "sad", "angry", "disappointed", "fail", "failed", "failure", "wrong",
    "sucks", "damn", "shit", "fuck", "stupid", "dumb", "idiot",
    "mengecewakan", "memalukan", "membosankan", "boring", "lame",

    # Slang
    "parah", "kacau", "amburadul", "kocar-kacil", "receh", "anjir",
    "babi", "bangsat", "kampret", "tolol", "bodoh", "goblok",
    "ya allah", "astaga", "masya allah", "disabled", "gagal",

    # Emoticons
    ":(", ":-(", ":'(", ":'-(", "T_T", "T.T", "T.T", ":((", "/:",
    "💔", "😢", "😭", "😡", "👎", "💀", "🤮", "😤",
}

NEUTRAL_WORDS = {
    "biasa", "bukan", "cuma", "hanya", "mungkin", "barangkali",
    "biasa saja", "bukan apa-apa", "gitu", "begitu", "netral",
    "normal", "standard", "okay", "nothing special",
}
