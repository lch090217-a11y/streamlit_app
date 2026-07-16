import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

st.set_page_config(
    page_title="주차장 정보 시스템",
    layout="wide"
)

st.title("🚗 주차장 정보 검색 시스템")

uploaded_file = st.file_uploader(
    "CSV 업로드(cp949 인코딩)",
    type=["csv"]
)

if uploaded_file:

    # cp949 한글 CSV 읽기
    df = pd.read_csv(uploaded_file, encoding="cp949")

    st.success("파일 업로드 완료!")

    st.subheader("데이터 미리보기")
    st.dataframe(df)

    ############################################
    # 사이드바
    ############################################

    st.sidebar.header("검색 조건")

    district = st.sidebar.selectbox(
        "자치구",
        ["전체"] + sorted(df["자치구"].unique().tolist())
    )

    parking_type = st.sidebar.selectbox(
        "주차장 종류",
        ["전체"] + sorted(df["주차장종류"].unique().tolist())
    )

    fee_type = st.sidebar.radio(
        "무료 / 유료",
        ["전체","무료","유료"]
    )

    parking_hour = st.sidebar.number_input(
        "예상 주차시간(시간)",
        1,
        24,
        2
    )

    ############################################
    # 필터
    ############################################

    filtered = df.copy()

    if district != "전체":
        filtered = filtered[
            filtered["자치구"] == district
        ]

    if parking_type != "전체":
        filtered = filtered[
            filtered["주차장종류"] == parking_type
        ]

    if fee_type != "전체":
        filtered = filtered[
            filtered["무료여부"] == fee_type
        ]

    ############################################
    # 예상요금 계산
    ############################################

    def calc_fee(row):

        if row["무료여부"] == "무료":
            return 0

        minute = parking_hour * 60

        base_time = row["기본시간"]
        base_fee = row["기본요금"]

        add_time = row["추가시간"]
        add_fee = row["추가요금"]

        if minute <= base_time:
            return base_fee

        extra = minute - base_time

        count = np.ceil(extra / add_time)

        return int(base_fee + count * add_fee)

    filtered["예상요금"] = filtered.apply(calc_fee, axis=1)

    ############################################
    # 가장 저렴한 주차장
    ############################################

    if len(filtered) > 0:

        cheapest = filtered.sort_values("예상요금").iloc[0]

        st.success(
            f"""
            💰 가장 저렴한 주차장

            **{cheapest['주차장명']}**

            예상요금 : **{cheapest['예상요금']:,}원**
            """
        )

    ############################################
    # 지도
    ############################################

    st.subheader("주차장 위치")

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered,
        get_position='[경도, 위도]',
        get_radius=70,
        get_fill_color='[255,0,0,180]',
        pickable=True
    )

    view_state = pdk.ViewState(
        latitude=filtered["위도"].mean(),
        longitude=filtered["경도"].mean(),
        zoom=11
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "text":"{주차장명}\n예상요금:{예상요금}원"
        }
    )

    st.pydeck_chart(deck)

    ############################################
    # 결과
    ############################################

    st.subheader("검색 결과")

    st.dataframe(
        filtered[
            [
                "주차장명",
                "자치구",
                "주차장종류",
                "무료여부",
                "예상요금"
            ]
        ].sort_values("예상요금")
    )
