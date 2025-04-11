from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import openai
import requests
from bs4 import BeautifulSoup
import re

# GPT API 키 입력
openai.api_key = "api키"

app = FastAPI()


# 뉴스 본문 추출 함수 (네이버 뉴스 기준)
def get_article_text_from_url(url: str) -> str:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    body = soup.find('div', {'id': 'dic_area'})  # 네이버 뉴스 본문 영역
    if body:
        return body.get_text(strip=True)
    else:
        return "본문을 찾을 수 없습니다."


# GPT API를 이용한 친근한 뉴스 요약 함수
def summarize_article_nunick_style(text: str) -> str:
    prompt = f"""
다음은 뉴스 기사입니다. 이 내용을 마치 친구에게 말하듯이, 이해하기 쉬운 말투로 요약해줘.
- 너무 딱딱하지 않게, 친근한 문체로 설명해줘.
- 중요한 정보는 빠뜨리지 말고, 간결하게 정리해줘.

[기사 내용]
{text}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # 또는 gpt-3.5-turbo
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.7,
    )
    return response['choices'][0]['message']['content']


# 간단한 개체명 추출 (정규표현식 기반, NER 대체)
def extract_named_entities(text):
    words = set(re.findall(r'\b[가-힣]{2,}\b', text))
    stopwords = {'기자', '뉴스', '보도', '사진', '연합뉴스'}
    return list(words - stopwords)


# 추천 키워드 생성
def recommend_related_keywords(entities):
    return [f"'{e}' 관련 뉴스 보기" for e in entities[:5]]  # 상위 5개만 추천


# FastAPI 엔드포인트: URL 입력 → 요약 + 개체명 추출 + 추천 키워드
@app.get("/summarize-url")
def summarize_news_url(url: str = Query(...)):
    try:
        article_text = get_article_text_from_url(url)
        if "본문을 찾을 수 없습니다" in article_text:
            return JSONResponse(status_code=404, content={"message": "뉴스 본문을 찾을 수 없습니다."})

        summary = summarize_article_nunick_style(article_text)
        named_entities = extract_named_entities(article_text)
        related = recommend_related_keywords(named_entities)

        return {
            "url": url,
            "summary": summary,
            "entities": named_entities,
            "relatedSuggestions": related
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})