from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import openai
import re

client = openai.OpenAI(api_key="YOUR_API_KEY_HERE")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Article(BaseModel):
    text: str

# 크롤링 함수
def extract_naver_article(url: str) -> str:
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    article_body = soup.select_one('#dic_area') or soup.select_one('article')
    if not article_body:
        raise ValueError("네이버 뉴스 본문을 찾을 수 없습니다.")
    return article_body.get_text(strip=True)

def extract_general_article(url: str) -> str:
    article = Article(url, language='ko')
    article.download()
    article.parse()
    return article.text

# 요약 프롬프트
def summarize_article_nunick_style(text: str) -> str:
    prompt = f"""
이 내용과 관련된 뉴스들의 요약내용들을 알려줘.
관련된 뉴스들을 1순위 2순위 3순위 이런식으로 관련도에 따라 등수를 나눠서 알려주고 그에대한 기사의 url도 알려줘.
그리고 요약할때 사용한 기사 url도 알려줘.
- 너무 딱딱하지 않게, 친근한 문체로 설명해줘.
- 중요한 정보는 빠뜨리지 말고, 간결하게 정리해줘.

[기사 내용]
{text}
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7,
    )
    return response.choices[0].message.content

# ✅ 기존 summarize API 그대로 유지
@app.post("/summarize")
def summarize(article: Article) -> str:
    try:
        user_input = article.text.strip()
        if user_input.startswith("http"):
            if "n.news.naver.com" in user_input:
                article_text = extract_naver_article(user_input)
            else:
                article_text = extract_general_article(user_input)
            cleaned_text = article_text
        else:
            cleaned_text = " ".join(user_input.splitlines()).replace('\\"', " ")
        return summarize_article_nunick_style(cleaned_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ 팀원용 API: /api/summaries
@app.post("/api/summaries")
def summarize_for_ui(article: Article):
    try:
        user_input = article.text.strip()
        if user_input.startswith("http"):
            if "n.news.naver.com" in user_input:
                article_text = extract_naver_article(user_input)
            else:
                article_text = extract_general_article(user_input)
            cleaned_text = article_text
        else:
            cleaned_text = " ".join(user_input.splitlines()).replace('\\"', " ")
        summary = summarize_article_nunick_style(cleaned_text)
        return {
            "original": user_input,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ 로컬 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

