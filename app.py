from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
import openai

# OpenAI 최신 버전 클라이언트 사용
client = openai.OpenAI(api_key="")  # 실제 키로 대체해주세요

app = FastAPI()

# 요청 바디 스키마
class Article(BaseModel):
    text: str

# GPT 요약 함수 (친근한 말투 스타일)
def summarize_article_nunick_style(text: str) -> str:
    prompt = f"""
다음은 뉴스 기사입니다. 이 내용을 마치 친구에게 말하듯이, 이해하기 쉬운 말투로 요약해줘.
- 너무 딱딱하지 않게, 친근한 문체로 설명해줘.
- 중요한 정보는 빠뜨리지 말고, 간결하게 정리해줘.

[기사 내용]
{text}
"""
    response = client.chat.completions.create(
        model="gpt-4o",  # 또는 "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.7,
    )
    return response.choices[0].message.content

# POST /summarize 엔드포인트
@app.post("/summarize")
def summarize(article: Article) -> str:
    try:
        cleaned_text = " ".join(article.text.splitlines())
        cleaned_text = cleaned_text.replace('\\"', " ")
        summary = summarize_article_nunick_style(cleaned_text)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 로컬 서버 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)