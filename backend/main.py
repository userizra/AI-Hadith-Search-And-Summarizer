from fastapi import FastAPI, HTTPException
from transformers import pipeline
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

async def connect_db():
    return await asyncpg.create_pool(DATABASE_URL)

summarizer = pipeline("summarization",)

@app.on_event("startup")
async def startup():
    global pool
    pool = await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await pool.close()

@app.get("/search")
async def search_hadith(query: str):
    try:
        async with pool.acquire() as conn:
            sql_query = """
                SELECT id, hadith_id, source, chapter_no, hadith_no, chapter, chain_indx, text_en
                FROM all_hadith 
                WHERE text_en ILIKE $1
                LIMIT 10;
            """
            # Use % for a partial match on the query
            rows = await conn.fetch(sql_query, f"%{query}%")

            results = [{
                "id": row["id"],
                "hadith_id": row["hadith_id"],
                "source": row["source"],
                "chapter_no": row["chapter_no"],
                "hadith_no": row["hadith_no"],
                "chapter": row["chapter"],
                "chain_indx": row["chain_indx"],
                "text_en": row["text_en"]
            } for row in rows]

            return {"query": query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

@app.get("/summarize")
async def summarize_text(hadith_id: int):
    try:
        # Fetch the Hadith text using the hadith_id from the database
        async with pool.acquire() as conn:
            hadith = await conn.fetchrow("SELECT text_en FROM all_hadith WHERE hadith_id = $1", hadith_id)
            if not hadith:
                raise HTTPException(status_code=404, detail="Hadith not found")
            
            # Get the Hadith text
            text = hadith["text_en"]

            # Summarize the text using Hugging Face model
            summary = summarizer(text, max_length=200, min_length=50, do_sample=False)
            
            return {"hadith_id": hadith_id, "summary": summary[0]["summary_text"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error summarizing text: {str(e)}")