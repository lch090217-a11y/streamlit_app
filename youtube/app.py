import streamlit as st
from googleapiclient.discovery import build
from openai import OpenAI
from urllib.parse import urlparse, parse_qs


# ----------------------------
# 설정
# ----------------------------

st.set_page_config(
    page_title="YouTube 댓글 분석기",
    page_icon="🎬",
    layout="wide"
)


YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

client = OpenAI(
    api_key=OPENAI_API_KEY
)


# ----------------------------
# 함수
# ----------------------------

def extract_video_id(url):
    """
    유튜브 URL에서 Video ID 추출
    """
    try:
        query = urlparse(url).query
        return parse_qs(query)["v"][0]

    except:
        return None



def get_comments(video_id, max_comments=100):
    """
    YouTube 댓글 가져오기
    """

    youtube = build(
        "youtube",
        "v3",
        developerKey=YOUTUBE_API_KEY
    )

    comments = []

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    )

    response = request.execute()


    for item in response["items"]:
        comment = (
            item["snippet"]
            ["topLevelComment"]
            ["snippet"]
            ["textDisplay"]
        )

        comments.append(comment)


        if len(comments) >= max_comments:
            break


    return comments



def analyze_comments(comments):
    """
    GPT 댓글 분석
    """

    joined_comments = "\n".join(
        comments
    )


    prompt = f"""
아래는 유튜브 댓글 목록입니다.

댓글을 분석해주세요.

분석 항목:

1. 전체 반응 요약
2. 긍정적인 의견
3. 부정적인 의견
4. 개선하면 좋은 점
5. 가장 많이 언급된 키워드
6. 시청자 감정 비율 예상

댓글:
{joined_comments}
"""


    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content":
                "너는 유튜브 데이터 분석 전문가다."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )


    return response.choices[0].message.content



# ----------------------------
# UI
# ----------------------------

st.title("🎬 YouTube 댓글 분석기")

st.write(
    "유튜브 영상 링크를 입력하면 댓글을 AI로 분석합니다."
)


video_url = st.text_input(
    "유튜브 영상 URL"
)



if st.button("🔍 분석 시작"):


    if not video_url:
        st.warning(
            "영상 URL을 입력해주세요."
        )
        st.stop()



    video_id = extract_video_id(video_url)


    if not video_id:
        st.error(
            "올바른 유튜브 URL이 아닙니다."
        )
        st.stop()



    with st.spinner(
        "댓글을 가져오는 중..."
    ):

        comments = get_comments(
            video_id
        )


    if len(comments) == 0:

        st.warning(
            "댓글을 찾을 수 없습니다."
        )
        st.stop()



    st.success(
        f"{len(comments)}개의 댓글 수집 완료"
    )


    with st.expander(
        "수집된 댓글 보기"
    ):
        for i, c in enumerate(comments):
            st.write(
                f"{i+1}. {c}"
            )



    with st.spinner(
        "AI 분석 중..."
    ):

        result = analyze_comments(
            comments
        )


    st.divider()

    st.subheader(
        "📊 AI 분석 결과"
    )

    st.markdown(
        result
    )
