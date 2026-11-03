import streamlit as st

from data_processing import (
    build_features,
    build_features_unaccented,
    build_vectorizer,
    is_unaccented_vietnamese,
    load_and_process_data,
)
from recommendation import recommend_places
from translation import translate_to_vietnamese
from weather import get_api_key, get_weather

DATA_PATH = "data/processed/places.csv"
ALL_PROVINCES = "Tất cả 34 tỉnh, thành"


@st.cache_resource
def load_model():
    df = load_and_process_data(DATA_PATH)
    tfidf = build_vectorizer().fit(df["description_tokens"])
    tfidf_unaccented = build_vectorizer().fit(df["description_tokens_unaccented"])
    return df, tfidf, tfidf_unaccented


df, tfidf, tfidf_unaccented = load_model()

st.title("Vietnam Travel Recommendation System")
st.caption("Dữ liệu đã cập nhật theo 34 tỉnh, thành sau sáp nhập (từ 1/7/2025).")

user_input = st.text_area("Nhập mô tả mong muốn của bạn:")
province = st.selectbox("Tỉnh, thành", [ALL_PROVINCES, *sorted(df["province"].unique())])

if st.button("Tìm kiếm"):
    if not user_input.strip():
        st.error("Vui lòng nhập mô tả mong muốn.")
    else:
        vi_unaccented = is_unaccented_vietnamese(user_input)
        if vi_unaccented:
            preprocess_fn = build_features_unaccented
        elif user_input.isascii():
            st.info("Phát hiện ngôn ngữ là tiếng Anh. Đang dịch sang tiếng Việt...")
            translated = translate_to_vietnamese(user_input)
            if translated:
                user_input = translated
                st.write(f"Mô tả: {user_input}")
            else:
                st.warning("Không dịch được, sẽ tìm kiếm với nội dung gốc.")
            preprocess_fn = build_features
        else:
            preprocess_fn = build_features

        recommendations = recommend_places(
            user_input,
            df,
            tfidf,
            preprocess_fn,
            province=None if province == ALL_PROVINCES else province,
            tfidf_unaccented=tfidf_unaccented,
            unaccented_query=vi_unaccented,
        )

        if recommendations.empty:
            st.write("Không tìm thấy địa điểm phù hợp với yêu cầu của bạn.")
        else:
            show_weather = bool(get_api_key())
            for _, row in recommendations.iterrows():
                st.subheader(row["name"])
                st.write(f"**Mô tả:** {row['description']}")

                with st.expander("Chi tiết"):
                    col1, col2 = st.columns([3, 2])

                    with col1:
                        location = row["province"]
                        if row["old_province"] != row["province"]:
                            location += f" (trước 7/2025: {row['old_province']})"
                        st.write(f"**Tỉnh, thành:** {location}")
                        st.write(f"**Độ tương đồng:** {row['similarity']}%")

                        # The pre-2025 province is closer to the place than the merged one.
                        weather_info = get_weather(row["old_province"]) if show_weather else None
                        if weather_info:
                            st.write(f"**Nhiệt độ:** {weather_info['temperature']}°C")
                            st.write(f"**Thời tiết:** {weather_info['description']}")
                            st.write(f"**Độ ẩm:** {weather_info['humidity']}%")
                            if weather_info["icon"]:
                                st.image(weather_info["icon"], width=80)
                        elif show_weather:
                            st.write("Không thể lấy thông tin thời tiết cho địa điểm này.")

                    with col2:
                        if row["image_url"]:
                            st.image(row["image_url"], caption=f"Hình ảnh {row['name']}", width="stretch")
                        else:
                            st.write("Không có hình ảnh cho địa điểm này.")
