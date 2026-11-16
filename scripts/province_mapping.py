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

UNCHANGED_REGIONS = [
    "Đồng Bằng Sông Hồng",
    "Trung Du Và Miền Núi Phía Bắc",
    "Đồng Bằng Sông Cửu Long",
    "Đông Nam Bộ",
    "Bắc Trung Bộ"
]
# In the Resolution 306/NQ-CP/2025, two regions 'Duyên Hải Nam Trung Bộ' and 'Tây Nguyên' are being merged into a new socio-economic one.
MERGED_REGIONS = { "Duyên Hải Nam Trung Bộ Và Tây Nguyên": ["Duyên Hải Nam Trung Bộ", "Tây Nguyên"] }

# A dictionary of provinces mapped with appropriate socio-economic region based on the Resolution 81/2023/QH15.
# Provinces from 'Bắc Trung Bộ và duyên hải miền Trung' region will have a clearer mapped value ("Bắc Trung Bộ" or "Duyên Hải Nam Trung Bộ") 
# due to the region splitting and merging based on the Resolution 306/NQ-CP/2025
MAPPED_REGIONS_WITH_PROVINCES = {
    "Hà Nội": "Đồng Bằng Sông Hồng",
    "Quảng Ninh": "Đồng Bằng Sông Hồng",
    "Bắc Giang": "Đồng Bằng Sông Hồng",
    "Bắc Ninh": "Đồng Bằng Sông Hồng",
    "Hưng Yên": "Đồng Bằng Sông Hồng",
    "Thái Bình": "Đồng Bằng Sông Hồng",
    "Hải Dương": "Đồng Bằng Sông Hồng",
    "Hải Phòng": "Đồng Bằng Sông Hồng",
    "Hà Nam": "Đồng Bằng Sông Hồng",
    "Nam Định": "Đồng Bằng Sông Hồng",
    "Ninh Bình": "Đồng Bằng Sông Hồng",
    "Vĩnh Phúc": "Trung Du Và Miền Núi Phía Bắc",
    "Tuyên Quang": "Trung Du Và Miền Núi Phía Bắc",
    "Hà Giang": "Trung Du Và Miền Núi Phía Bắc",
    "Lào Cai": "Trung Du Và Miền Núi Phía Bắc",
    "Yên Bái": "Trung Du Và Miền Núi Phía Bắc",
    "Thái Nguyên": "Trung Du Và Miền Núi Phía Bắc",
    "Bắc Kạn": "Trung Du Và Miền Núi Phía Bắc",
    "Phú Thọ": "Trung Du Và Miền Núi Phía Bắc",
    "Hòa Bình": "Trung Du Và Miền Núi Phía Bắc",
    "Lai Châu": "Trung Du Và Miền Núi Phía Bắc",
    "Điện Biên": "Trung Du Và Miền Núi Phía Bắc",
    "Sơn La": "Trung Du Và Miền Núi Phía Bắc",
    "Lạng Sơn": "Trung Du Và Miền Núi Phía Bắc",
    "Cao Bằng": "Trung Du Và Miền Núi Phía Bắc",
    "Kon Tum": "Tây Nguyên",
    "Đắk Nông": "Tây Nguyên",
    "Lâm Đồng": "Tây Nguyên",
    "Đắk Lắk": "Tây Nguyên",    
    "Gia Lai": "Tây Nguyên",
    "Đà Nẵng": "Duyên Hải Nam Trung Bộ",
    "Quảng Nam": "Duyên Hải Nam Trung Bộ",
    "Quảng Ngãi": "Duyên Hải Nam Trung Bộ",
    "Bình Định": "Duyên Hải Nam Trung Bộ",
    "Khánh Hòa": "Duyên Hải Nam Trung Bộ",
    "Ninh Thuận": "Duyên Hải Nam Trung Bộ",
    "Bình Thuận": "Duyên Hải Nam Trung Bộ",
    "Phú Yên": "Duyên Hải Nam Trung Bộ",
    "Huế": "Bắc Trung Bộ",
    "Thanh Hóa": "Bắc Trung Bộ",
    "Nghệ An": "Bắc Trung Bộ",
    "Hà Tĩnh": "Bắc Trung Bộ",
    "Quảng Bình": "Bắc Trung Bộ",
    "Quảng Trị": "Bắc Trung Bộ",
    "Cần Thơ": "Đồng Bằng Sông Cửu Long",
    "Hậu Giang": "Đồng Bằng Sông Cửu Long",
    "Sóc Trăng": "Đồng Bằng Sông Cửu Long",
    "Bến Tre": "Đồng Bằng Sông Cửu Long",
    "Trà Vinh": "Đồng Bằng Sông Cửu Long",
    "Vĩnh Long": "Đồng Bằng Sông Cửu Long",
    "Đồng Tháp": "Đồng Bằng Sông Cửu Long",
    "Tiền Giang": "Đồng Bằng Sông Cửu Long",
    "Bạc Liêu": "Đồng Bằng Sông Cửu Long",
    "Cà Mau": "Đồng Bằng Sông Cửu Long",
    "An Giang": "Đồng Bằng Sông Cửu Long",
    "Kiên Giang": "Đồng Bằng Sông Cửu Long",
    "Long An": "Đồng Bằng Sông Cửu Long",
    "Tây Ninh": "Đông Nam Bộ",
    "Bà Rịa - Vũng Tàu": "Đông Nam Bộ",
    "Bình Dương": "Đông Nam Bộ",
    "TP. Hồ Chí Minh": "Đông Nam Bộ",
    "Bình Phước": "Đông Nam Bộ",
    "Đồng Nai": "Đông Nam Bộ",
}

# Based on Resolution 306/NQ-CP/2025, because of merging into Tây Ninh, Long An had also switched to the new socio-economic region.
REGION_SWITCH = { "Long An": ["Đồng Bằng Sông Cửu Long", "Đông Nam Bộ"] }

# Thừa Thiên Huế became the centrally governed Huế city on 1 January 2025, without merging.
RENAMED = {"Thừa Thiên Huế": "Huế"}

OLD_TO_NEW = {old: new for new, olds in MERGERS.items() for old in olds}
OLD_TO_NEW.update({name: name for name in UNCHANGED if name != "Huế"})
OLD_TO_NEW.update(RENAMED)

NEW_PROVINCES = sorted(set(OLD_TO_NEW.values()))

NEW_REGIONS_MAPPED = dict(MAPPED_REGIONS_WITH_PROVINCES)
NEW_REGIONS_MAPPED.update({province: merged_region for province, region in NEW_REGIONS_MAPPED.items() for merged_region, sub_regions in MERGED_REGIONS.items() if region in sub_regions })
NEW_REGIONS_MAPPED.update({name: switch_region[1] for name, switch_region in REGION_SWITCH.items()})
NEW_REGIONS_MAPPED = {name: region for name, region in NEW_REGIONS_MAPPED.items() if name in NEW_PROVINCES}