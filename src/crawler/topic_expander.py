"""
Topic Expander - Expands a core topic into related search terms
to maximize relevant data collection.
"""

from typing import List, Dict, Set


# Topic mapping for common Indonesian terms
TOPIC_MAPPINGS: Dict[str, List[str]] = {
    # MBG related (Makan Bergizi Gratis / Prabowo's program)
    "mbg": [
        "MBG", "Makan Bergizi Gratis", "Program MBG",
        "Makan Siang Gratis", "Prabowo MBG", "Prabowo Subianto",
        "#MakanBergiziGratis", "#MBG", "#Prabowo", "#MakanGratis",
        "susu MBG", "gizi siswa", "dapur MBG", "stunting",
    ],
    "prabowo": [
        "Prabowo", "Prabowo Subianto", "Gibran", "Gemoy",
        "#Prabowo", "#PrabowoGibran", "#IndonesiaMaju",
        "presiden prabowo", "kabinet merah putih",
    ],
    "politik": [
        "politik", "Partai", "GOLKAR", "PDIP", "Gerindra", "NasDem",
        "#Politik", "#PartaiGelora", " DPR", "Legislasi",
        "pemilu", "pilkada", "suara rakyat",
    ],
    "ekonomi": [
        "ekonomi", "UMKM", "startup", "investor",
        "BUMN", "bank", "rupiah", "inflasi", "dolar",
        "#Ekonomi", "#UMKM", "#Investasi",
    ],
    "teknologi": [
        "teknologi", "tech", "AI", "sains", "startup", "digital",
        "#Teknologi", "#AI", "#Startup", "inovasi",
        "kecerdasan buatan", "programming",
    ],
    "ai": [
        "AI", "Artificial Intelligence", "ChatGPT", "GPT", "Gemini",
        "Machine Learning", "Deep Learning", "OpenAI", "Neural",
        "#AI", "#MachineLearning", "#ChatGPT", "robot", "automation",
    ],
    "pendidikan": [
        "pendidikan", "sekolah", "kampus", "guru", "siswa", "mahasiswa",
        "PTN", "PTS", "beasiswa", "kredit", "PJJ", "sekolah daring",
        "#Pendidikan", "#Sekolah", "#Guru",
    ],
    "kesehatan": [
        "kesehatan", "rumah sakit", "dokter", "BPJS", "obat", "vaksin",
        "pandemi", "covid", "stunting", "gizi", "malnutrisi",
        "#Kesehatan", "#BPJS", "#Vaksin",
    ],
    "bola": [
        "bola", "sepak bola", "football", "Premier League", "EPL",
        "liga", "Goal", "Barcelona", "Real Madrid", "Liverpool",
        "Persib", "Persija", "Arema", "Bali United",
        "#Bola", "#Football", "#SepakBola",
    ],
    "hiburan": [
        "hiburan", "film", "musik", "konser", "sinema", "bioskop",
        "artis", "selebriti", "drama", "Kpop", "musik",
        "#Film", "#Musik", "#Konser", "#Bioskop",
    ],
}


def expand_topic(core_topic: str) -> List[str]:
    """
    Expand a core topic into multiple related search terms.

    Args:
        core_topic: The main topic to search for

    Returns:
        List of related search terms (deduplicated)
    """
    topic_lower = core_topic.lower().strip()

    # Check for known topics
    for key, expansions in TOPIC_MAPPINGS.items():
        if key in topic_lower or topic_lower in key:
            return list(set(expansions))

    # For unknown topics, just return the original
    # and generate some variations
    variations = [core_topic]

    # Add common variations
    if " " not in core_topic:
        # Single word - might be abbreviation
        variations.append(f"#{core_topic}")
        variations.append(f'"{core_topic}"')

    return list(set(variations))


def expand_topics(topics: List[str]) -> List[str]:
    """
    Expand multiple topics and deduplicate.

    Args:
        topics: List of core topics

    Returns:
        List of all expanded search terms
    """
    expanded: Set[str] = set()

    for topic in topics:
        expanded.update(expand_topic(topic))

    return list(expanded)


# Example usage
if __name__ == "__main__":
    print("=== Topic Expansion Examples ===\n")

    test_topics = ["MBG", "AI", "pendidikan", "teknologi"]

    for topic in test_topics:
        expanded = expand_topic(topic)
        print(f"Topic: {topic}")
        print(f"Expanded: {expanded}")
        print()
