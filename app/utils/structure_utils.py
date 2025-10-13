"""
Structure processing utilities
"""
import difflib

from app.utils.html_processor_utils import HtmlProcessor

# Structure mapping (chuẩn hóa về tiếng Anh)
STRUCTURE_MAPPING = {
    "木造": "wood",
    "ブロック": "cb",
    "鉄骨造": "steel_frame",
    "鉄筋コンクリート（RC）": "rc",
    "鉄骨鉄筋コンクリート（SRC）": "src",
    "プレキャストコンクリート（PC）": "pc",
    "鉄骨プレキャスト（HPC）": "other",
    "軽量鉄骨": "light_gauge_steel",
    "軽量気泡コンクリート（ALC）": "alc",
    "その他": "other",
}

# Từ khóa đặc trưng → chuẩn hóa về dạng standard key
STRUCTURE_KEYWORDS = {
    "RC": "鉄筋コンクリート（RC）",
    "SRC": "鉄骨鉄筋コンクリート（SRC）",
    "PC": "プレキャストコンクリート（PC）",
    "ALC": "軽量気泡コンクリート（ALC）",
    "HPC": "鉄骨プレキャスト（HPC）",
    "木造": "木造",
    "鉄骨造": "鉄骨造",
    "鉄骨": "鉄骨造",  # fallback: có chữ "鉄骨" thì coi như steel_frame
    "ブロック": "ブロック",
}


def normalize_structure_text(text: str) -> str:
    """Normalize different structure expressions to standard format."""
    if not text:
        return ""

    # Chuẩn hóa ngoặc
    text = text.replace("(", "（").replace(")", "）").strip()

    # Check theo keyword
    for key, standard in STRUCTURE_KEYWORDS.items():
        if key in text:
            return standard

    return text


def extract_structure_info(structure_text: str) -> str:
    """
    Extract and map building structure information.
    
    Args:
        structure_text: Raw structure text from HTML.
        
    Returns:
        Mapped structure type (English code).
    """
    html_processor = HtmlProcessor()

    def map_structure(original: str) -> str:
        if not original:
            return "other"

        normalized = normalize_structure_text(original)

        # Nếu chuẩn hóa xong nằm trong mapping
        if normalized in STRUCTURE_MAPPING:
            return STRUCTURE_MAPPING[normalized]

        # Fallback fuzzy matching
        keys = list(STRUCTURE_MAPPING.keys())
        matches = difflib.get_close_matches(normalized, keys, n=1, cutoff=0.3)
        if matches:
            return STRUCTURE_MAPPING[matches[0]]

        return "other"

    # Regex thử bắt cấu trúc chính (…造 hoặc …コンクリート…)
    pattern = html_processor.compile_regex(r'^(.*?造|.*?コンクリート.*?）?)')
    match = pattern.search(structure_text)

    target = match.group(1).strip() if match else structure_text.strip()
    return map_structure(target)