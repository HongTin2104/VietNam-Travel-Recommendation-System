import re

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from underthesea import word_tokenize
from unidecode import unidecode

# Common Vietnamese syllables without diacritics — used to detect unaccented Vietnamese
# queries so they are not mistakenly treated as English.
_VI_SYLLABLES = {
    "ba",
    "bac",
    "bai",
    "ban",
    "bay",
    "be",
    "bien",
    "bo",
    "bong",
    "bui",
    "cai",
    "cao",
    "cat",
    "cau",
    "cay",
    "cha",
    "chau",
    "cho",
    "chua",
    "co",
    "cung",
    "da",
    "dai",
    "dau",
    "dao",
    "dep",
    "dia",
    "dinh",
    "dong",
    "duc",
    "duong",
    "ga",
    "gia",
    "giai",
    "go",
    "hai",
    "hang",
    "hien",
    "hoa",
    "hoang",
    "hoi",
    "hong",
    "hue",
    "hung",
    "huong",
    "khe",
    "khu",
    "ky",
    "la",
    "lac",
    "lang",
    "lao",
    "len",
    "linh",
    "lua",
    "lung",
    "luong",
    "ly",
    "ma",
    "moc",
    "moi",
    "mua",
    "muong",
    "ngan",
    "ngam",
    "ngo",
    "ngon",
    "nha",
    "nhat",
    "nhieu",
    "nho",
    "ninh",
    "nui",
    "nung",
    "pho",
    "phong",
    "phu",
    "que",
    "quoc",
    "rang",
    "rung",
    "san",
    "sao",
    "sau",
    "so",
    "song",
    "suon",
    "tam",
    "tan",
    "tay",
    "thanh",
    "thap",
    "thieng",
    "thu",
    "thung",
    "thuy",
    "tien",
    "toan",
    "trang",
    "tre",
    "tri",
    "tu",
    "tung",
    "tuong",
    "vach",
    "van",
    "viet",
    "vinh",
    "vo",
    "vu",
    "xa",
    "xanh",
    "xom",
    "xuong",
}


def is_unaccented_vietnamese(text: str) -> bool:
    """Return True when text looks like Vietnamese typed without diacritics.

    Requires at least two tokens that match known Vietnamese syllables so that
    short, ambiguous inputs default to the existing translation path.
    """
    if not text.isascii():
        return False
    tokens = text.lower().split()
    vi_count = sum(1 for t in tokens if t in _VI_SYLLABLES)
    return vi_count >= 2


def remove_diacritics(text: str) -> str:
    """Strip Vietnamese diacritics using unidecode (đ→d, ơ→o, â→a, etc.)."""
    return unidecode(text)


def build_features_unaccented(text: str) -> str:
    """Like build_features but for unaccented queries: strip diacritics first."""
    return build_features(remove_diacritics(text))


# Tạo danh sách stopwords (từ không mang nghĩa)
vietnamese_stopwords = [
    "của",
    "và",
    "là",
    "theo",
    "như",
    "để",
    "trong",
    "có",
    "một",
    "này",
    "với",
    "nhưng",
    "lại",
    "thì",
    "ra",
    "nên",
    "đã",
    "được",
    "rằng",
    "nhất",
    "ở",
    "khi",
]


# Hàm tiền xử lý văn bản
def preprocess_text(text):
    if not isinstance(text, str) or not text.strip():
        return ""
    # Chuyển về chữ thường và loại bỏ ký tự không cần thiết
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)  # Loại bỏ dấu câu
    text = re.sub(r"\d+", "", text)  # Loại bỏ số
    # Tách từ và loại bỏ stopwords
    tokens = word_tokenize(text, format="text").split()
    tokens = [word for word in tokens if word not in vietnamese_stopwords]
    return " ".join(tokens) if tokens else ""


def build_features(text):
    """Segmented words plus the syllables of each compound word.

    A query for "biển" should still match "bãi_biển"; see reports/evaluation.md for the comparison.
    """
    words = preprocess_text(text)
    syllables = [s for word in words.split() if "_" in word for s in word.split("_")]
    return " ".join([words, *syllables]).strip()


def build_vectorizer():
    return TfidfVectorizer(ngram_range=(1, 2))


# Đọc dữ liệu đã làm sạch (scripts/build_dataset.py) và tiền xử lý
def load_and_process_data(file_path):
    df = pd.read_csv(file_path, keep_default_na=False)
    df["description_tokens"] = df["description"].apply(build_features)
    df["description_tokens_unaccented"] = df["description"].apply(lambda d: build_features(remove_diacritics(d)))
    df = df[df["description_tokens"].str.strip() != ""].reset_index(drop=True)
    return df
