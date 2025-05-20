from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import openai
import re

client = openai.OpenAI(api_key="")

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
이 뉴스 내용과 관련된 기사들을 정리해줘. 관련도를 기준으로 1순위, 2순위, 3순위 식으로 순서를 나누고, 각 뉴스에 대해 다음 형식으로 마크다운으로 출력해줘:

### 1순위 뉴스: [제목]

- 요약: [친근하고 간결하게 정리된 핵심 내용]
- URL: [관련 기사 링크]

### 2순위 뉴스: ...
...

조건:
- 각 뉴스 항목은 위의 마크다운 형식과 정확히 일치하게 출력해줘.
- 제목과 순위는 반드시 `### 1순위 뉴스: 제목` 형식으로 한 줄에 작성해.
- 문체는 너무 딱딱하지 않게, 부드럽고 이해하기 쉽게 써줘.
- 관련 기사 URL은 실제 URL이 아니어도 괜찮아. 형식만 맞춰줘.

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

# ✅ 기본 요약 API
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
        return summarize_article_nunick_style(cleaned_text).replace("\n", "<br>")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ UI용 요약 API
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
        summary = summarize_article_nunick_style(cleaned_text).replace("\n", "<br>")
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
