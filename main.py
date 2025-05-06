from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import openai

# 🔑 OpenAI API 키 입력
client = openai.OpenAI(api_key="")  # ← 여기에 키 입력

app = FastAPI()

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 요청 데이터 형식
class ArticleRequest(BaseModel):
    url: str

# ✅ 네이버 뉴스 본문 추출 함수
def extract_naver_article(url: str) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    article_body = soup.select_one('#dic_area') or soup.select_one('article')

    if not article_body:
        raise ValueError("네이버 뉴스 본문을 찾을 수 없습니다.")

    return article_body.get_text(strip=True)

# ✅ 일반 뉴스 본문 추출 함수 (newspaper3k)
def extract_general_article(url: str) -> str:
    article = Article(url, language='ko')
    article.download()
    article.parse()
    return article.text

# ✅ URL에 따라 분기 처리
def extract_text_from_url(url: str) -> str:
    if "n.news.naver.com" in url:
        print("🌐 네이버 뉴스 감지됨 → BeautifulSoup 사용")
        return extract_naver_article(url)
    else:
        print("🌐 일반 뉴스 → newspaper3k 사용")
        return extract_general_article(url)

# ✅ GPT 요약 함수
def summarize_article(text: str) -> str:
    prompt = f"""
다음 뉴스 내용을 요약해줘.
- 너무 딱딱하지 않게, 친근한 문체로 설명해줘.
- 중요한 정보는 빠뜨리지 말고, 간결하게 정리해줘.

[뉴스 본문]
{text}
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7,
    )
    return response.choices[0].message.content

# ✅ API 엔드포인트
@app.post("/summarize")
def summarize(request: ArticleRequest) -> str:
    try:
        article_text = extract_text_from_url(request.url)
        print("📄 추출된 기사 본문 앞부분:", article_text[:500])  # 로그로 본문 확인
        summary = summarize_article(article_text)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

