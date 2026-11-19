"""Map the 63 provinces used before 1 July 2025 to the 34 provincial units after the 2025 merger.

Source: Resolution 202/2025/QH15 of the National Assembly (12 June 2025), effective 1 July 2025.
"""

MERGERS = {
    "Tuyên Quang": ["Tuyên Quang", "Hà Giang"],
    "Lào Cai": ["Lào Cai", "Yên Bái"],
    "Thái Nguyên": ["Thái Nguyên", "Bắc Kạn"],
    "Phú Thọ": ["Phú Thọ", "Vĩnh Phúc", "Hòa Bình"],
    "Bắc Ninh": ["Bắc Ninh", "Bắc Giang"],
    "Hưng Yên": ["Hưng Yên", "Thái Bình"],
    "Hải Phòng": ["Hải Phòng", "Hải Dương"],
    "Ninh Bình": ["Ninh Bình", "Hà Nam", "Nam Định"],
    "Quảng Trị": ["Quảng Trị", "Quảng Bình"],
    "Đà Nẵng": ["Đà Nẵng", "Quảng Nam"],
    "Quảng Ngãi": ["Quảng Ngãi", "Kon Tum"],
    "Gia Lai": ["Gia Lai", "Bình Định"],
    "Khánh Hòa": ["Khánh Hòa", "Ninh Thuận"],
    "Lâm Đồng": ["Lâm Đồng", "Đắk Nông", "Bình Thuận"],
    "Đắk Lắk": ["Đắk Lắk", "Phú Yên"],
    "TP. Hồ Chí Minh": ["TP. Hồ Chí Minh", "Bình Dương", "Bà Rịa - Vũng Tàu"],
    "Đồng Nai": ["Đồng Nai", "Bình Phước"],
    "Tây Ninh": ["Tây Ninh", "Long An"],
    "Cần Thơ": ["Cần Thơ", "Sóc Trăng", "Hậu Giang"],
    "Vĩnh Long": ["Vĩnh Long", "Bến Tre", "Trà Vinh"],
    "Đồng Tháp": ["Đồng Tháp", "Tiền Giang"],
    "Cà Mau": ["Cà Mau", "Bạc Liêu"],
    "An Giang": ["An Giang", "Kiên Giang"],
}

UNCHANGED = [
    "Hà Nội",
    "Huế",
    "Lai Châu",
    "Điện Biên",
    "Sơn La",
    "Lạng Sơn",
    "Quảng Ninh",
    "Thanh Hóa",
    "Nghệ An",
    "Hà Tĩnh",
    "Cao Bằng",
]

# The 6 socio-economic regions for the 34 provinces, from the Resolution 306/NQ-CP 2025.
REGIONS = {
    "Trung du và miền núi phía Bắc": [
        "Cao Bằng",
        "Điện Biên",
        "Lai Châu",
        "Lạng Sơn",
        "Lào Cai",
        "Phú Thọ",
        "Sơn La",
        "Thái Nguyên",
        "Tuyên Quang",
    ],
    "Đồng bằng sông Hồng": ["Hà Nội", "Hải Phòng", "Ninh Bình", "Hưng Yên", "Bắc Ninh", "Quảng Ninh"],
    "Bắc Trung Bộ": ["Thanh Hóa", "Nghệ An", "Hà Tĩnh", "Quảng Trị", "Huế"],
    "Duyên hải Nam Trung Bộ và Tây Nguyên": ["Đà Nẵng", "Quảng Ngãi", "Gia Lai", "Đắk Lắk", "Khánh Hòa", "Lâm Đồng"],
    "Đông Nam Bộ": ["TP. Hồ Chí Minh", "Đồng Nai", "Tây Ninh"],
    "Đồng bằng sông Cửu Long": ["Cần Thơ", "Vĩnh Long", "Đồng Tháp", "An Giang", "Cà Mau"],
}

# Thừa Thiên Huế became the centrally governed Huế city on 1 January 2025, without merging.
RENAMED = {"Thừa Thiên Huế": "Huế"}

OLD_TO_NEW = {old: new for new, olds in MERGERS.items() for old in olds}
OLD_TO_NEW.update({name: name for name in UNCHANGED if name != "Huế"})
OLD_TO_NEW.update(RENAMED)

NEW_PROVINCES = sorted(set(OLD_TO_NEW.values()))

PROVINCE_TO_REGION = {province: region for region, provinces in REGIONS.items() for province in provinces}
