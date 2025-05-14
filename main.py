from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import openai

# ✅ OpenAI API Key
client = openai.OpenAI(api_key="YOUR_API_KEY_HERE")  # 여기에 실제 키 삽입

app = FastAPI()

# ✅ CORS 설정 (HTML에서 접근 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 입력 스키마
class ArticleRequest(BaseModel):
    text: str

# ✅ 네이버 뉴스 크롤링
def extract_naver_article(url: str) -> str:
    print("🌐 네이버 기사 크롤링:", url)
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    article_body = soup.select_one('#dic_area') or soup.select_one('article')
    if not article_body:
        raise ValueError("❌ 네이버 본문을 찾지 못했습니다.")
    return article_body.get_text(strip=True)

# ✅ 일반 뉴스 URL 크롤링
def extract_general_article(url: str) -> str:
    print("🌐 일반 뉴스 크롤링:", url)
    article = Article(url, language='ko')
    article.download()
    article.parse()
    return article.text

# ✅ GPT 요약 함수
def summarize_article(text: str) -> str:
    prompt = f"""
이 내용과 관련된 뉴스들의 요약내용들을 알려줘.
관련된 뉴스들을 1순위 2순위 3순위 이런식으로 관련도에 따라 등수를 나눠서 알려주고 그에대한 기사의 url도 알려줘.
그리고 요약할때 사용한 기사 url도 알려줘.
- 너무 딱딱하지 않게, 친근한 문체로 설명해줘.
- 중요한 정보는 빠뜨리지 말고, 간결하게 정리해줘.

[기사 내용]
{text}
"""
    try:
        print("🟡 GPT 요청 시작 (길이:", len(prompt), ")")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # ⚠️ gpt-4o 대신 테스트용
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7,
        )
        print("✅ GPT 응답 수신 완료")
        return response.choices[0].message.content
    except Exception as e:
        print("❌ GPT 요청 실패:", e)
        raise

# ✅ 통합 엔드포인트
@app.post("/api/summaries")
def summarize(article: ArticleRequest):
    try:
        user_input = article.text.strip()
        print("📥 요청 수신:", user_input)

        # URL 판별
        if user_input.startswith("http"):
            print("🌐 URL로 판단됨")
            if "n.news.naver.com" in user_input:
                article_text = extract_naver_article(user_input)
            else:
                article_text = extract_general_article(user_input)
            cleaned_text = article_text
        else:
            print("💬 일반 질문으로 판단됨")
            cleaned_text = user_input

        summary = summarize_article(cleaned_text)

        return {
            "original": user_input,
            "summary": summary
        }

    except Exception as e:
        print("❌ /api/summaries 처리 오류:", e)
        raise HTTPException(status_code=403, detail=str(e))

# ✅ 로컬 실행
if __name__ == "__main__":
    import uvicorn
    print("🚀 FastAPI 서버 실행 중 (http://localhost:8000)")
    uvicorn.run(app, host="0.0.0.0", port=8000)

