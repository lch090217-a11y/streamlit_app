import streamlit as st
import requests
import random

st.set_page_config(
    page_title="오늘의 음식 추천",
    page_icon="🍽️",
    layout="wide"
)

# -------------------------
# 음식 데이터
# -------------------------

foods = {
    "cold": [
        {
            "name": "김치찌개",
            "image": "https://images.unsplash.com/photo-1604908177522-4728f3fa2d97",
            "calorie": 430,
            "carb": "32g",
            "protein": "25g",
            "fat": "18g",
            "reason": "추운 날에는 따뜻한 국물이 최고입니다."
        },
        {
            "name": "설렁탕",
            "image": "https://images.unsplash.com/photo-1547592180-85f173990554",
            "calorie": 520,
            "carb": "28g",
            "protein": "33g",
            "fat": "24g",
            "reason": "몸을 따뜻하게 해주는 국물 음식입니다."
        }
    ],
    "hot": [
        {
            "name": "냉면",
            "image": "https://images.unsplash.com/photo-1625943553852-781c6dd46c6b",
            "calorie": 480,
            "carb": "72g",
            "protein": "16g",
            "fat": "8g",
            "reason": "더운 날 시원하게 먹기 좋습니다."
        },
        {
            "name": "초밥",
            "image": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c",
            "calorie": 410,
            "carb": "52g",
            "protein": "22g",
            "fat": "9g",
            "reason": "가볍고 신선한 음식입니다."
        }
    ],
    "rain": [
        {
            "name": "파전",
            "image": "https://images.unsplash.com/photo-1600891964599-f61ba0e24092",
            "calorie": 550,
            "carb": "49g",
            "protein": "18g",
            "fat": "29g",
            "reason": "비 오는 날 생각나는 대표 음식입니다."
        },
        {
            "name": "칼국수",
            "image": "https://images.unsplash.com/photo-1612929633738-8fe44f7ec841",
            "calorie": 610,
            "carb": "80g",
            "protein": "22g",
            "fat": "17g",
            "reason": "따뜻한 국물이 비 오는 날과 잘 어울립니다."
        }
    ],
    "normal": [
        {
            "name": "비빔밥",
            "image": "https://images.unsplash.com/photo-1516684732162-798a0062be99",
            "calorie": 560,
            "carb": "68g",
            "protein": "21g",
            "fat": "18g",
            "reason": "균형 잡힌 영양소를 제공합니다."
        },
        {
            "name": "불고기",
            "image": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1",
            "calorie": 620,
            "carb": "26g",
            "protein": "36g",
            "fat": "30g",
            "reason": "언제 먹어도 맛있는 대표 한식입니다."
        }
    ]
}


# -------------------------
# 날씨 조회
# -------------------------

def get_weather(city, api_key):

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

    return None


def recommend_food(weather, temp):

    if "Rain" in weather:
        return random.choice(foods["rain"])

    elif temp >= 28:
        return random.choice(foods["hot"])

    elif temp <= 10:
        return random.choice(foods["cold"])

    else:
        return random.choice(foods["normal"])


# -------------------------
# 화면
# -------------------------

st.title("🍽️ 오늘의 날씨 음식 추천")

st.write("현재 날씨에 맞는 음식을 추천해드립니다.")

city = st.text_input("도시 입력", "Seoul")

if st.button("추천받기"):

    api_key = st.secrets["OPENWEATHER_API_KEY"]

    weather_data = get_weather(city, api_key)

    if weather_data:

        temp = weather_data["main"]["temp"]
        weather = weather_data["weather"][0]["main"]
        desc = weather_data["weather"][0]["description"]

        food = recommend_food(weather, temp)

        st.success(f"현재 기온 : {temp:.1f}℃")
        st.info(f"날씨 : {desc}")

        col1, col2 = st.columns([1,1])

        with col1:

            st.image(food["image"], use_container_width=True)

        with col2:

            st.header(food["name"])

            st.write(food["reason"])

            st.metric("칼로리", f"{food['calorie']} kcal")

            st.subheader("영양성분")

            st.write(f"탄수화물 : {food['carb']}")
            st.write(f"단백질 : {food['protein']}")
            st.write(f"지방 : {food['fat']}")

    else:
        st.error("도시를 찾을 수 없습니다.")
