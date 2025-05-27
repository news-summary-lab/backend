from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import openai
import os
from dotenv import load_dotenv

load_dotenv()

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ArticleRequest(BaseModel):
    text: str

def is_url(text: str) -> bool:
    return text.startswith("http")

# ✅ 네이버 뉴스 본문 크롤링
def extract_naver_article(url: str) -> str:
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/113.0.0.0 Safari/537.36'
        )
    }
    res = requests.get(url, headers=headers, timeout=5)
    if res.status_code == 403:
        raise ValueError("❌ 네이버에서 접근이 차단되었습니다.")
    soup = BeautifulSoup(res.text, 'html.parser')
    selectors = ['#dic_area', '#newsct_article', '#newsEndContents', 'div.article_body', 'div#articeBody', 'article']
    for selector in selectors:
        article_body = soup.select_one(selector)
        if article_body:
            for tag in article_body.find_all(['table', 'img', 'figure']):
                tag.decompose()
            text = article_body.get_text(separator="\n", strip=True)
            if len(text) >= 30:
                return text
    raise ValueError("본문을 자동으로 추출할 수 없습니다.")

# ✅ 일반 뉴스 본문 추출
def extract_general_article(url: str) -> str:
    article = Article(url, language='ko')
    article.download()
    article.parse()
    return article.text

# ✅ 검색용 키워드 추출
def extract_search_query(text: str) -> str:
    return " ".join(text.strip().split()[:6])

# ✅ 관련 뉴스 검색
def search_naver_news(query: str):
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": query,
        "display": 3,
        "sort": "date"
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json().get("items", [])

# ✅ GPT 요약 (문맥에 따라 프롬프트 구분)
def summarize_article(text: str, is_direct_prompt: bool = False) -> str:
    if is_direct_prompt:
        prompt = f"""
사용자의 요청에 따라 최근 뉴스나 이슈에 대해 응답해 주세요.

요청 내용: "{text}"

- 자연스러운 대화체
- 짧고 간결하게 핵심만
- 마크다운 없이 HTML <p>만 사용
"""
    else:
        prompt = f"""
다음은 뉴스 기사 본문입니다. 이 내용을 한 단락으로 자연스럽게 요약해 주세요.

[뉴스 본문]
{text}

조건:
- 딱딱하지 않은 문체
- 마크다운 대신 HTML 형식으로 줄바꿈 없이 요약만 출력
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

# ✅ 관련 뉴스 HTML 생성
def format_related_news_html(related_news: list) -> str:
    if not related_news:
        return "<h3>관련 뉴스</h3><p>관련된 뉴스를 찾을 수 없습니다.</p>"
    result = "<h3>관련 뉴스</h3><ol>"
    for item in related_news:
        title = item['title'].replace('<b>', '').replace('</b>', '')
        desc = item['description'].replace('<b>', '').replace('</b>', '')
        link = item.get('originallink') or item.get('link')
        result += f"<li><strong>{title}</strong><br>- 요약: {desc}<br>- <a href='{link}' target='_blank'>기사 링크</a></li><br>"
    result += "</ol>"
    return result

# ✅ 전체 HTML 구성
def summarize_with_related_news(text: str, related_news: list) -> str:
    summary = summarize_article(text, is_direct_prompt=False)
    related_html = format_related_news_html(related_news)
    return f"<h2>본문 요약</h2><p>{summary}</p><br>{related_html}"

# ✅ FastAPI 엔드포인트
@app.post("/summarize")
def summarize(article: ArticleRequest):
    try:
        user_input = article.text.strip()
        if not user_input:
            raise HTTPException(status_code=400, detail="입력된 텍스트가 비어 있습니다.")

        if is_url(user_input):
            # ✅ 뉴스 링크인 경우
            article_text = extract_naver_article(user_input) if "n.news.naver.com" in user_input else extract_general_article(user_input)
            if len(article_text) < 30:
                raise HTTPException(status_code=400, detail="본문 길이가 너무 짧습니다. 30자 이상 필요합니다.")
            search_query = extract_search_query(article_text)
            related_news = search_naver_news(search_query)
            return summarize_with_related_news(article_text, related_news)
        else:
            # ✅ 자유 질문인 경우
            return summarize_article(user_input, is_direct_prompt=True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ 로컬 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
