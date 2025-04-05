from fastapi import FastAPI, HTTPException
import asyncpg
import os
from dotenv import load_dotenv
import random

load_dotenv()  # Load environment variables from .env file

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

async def connect_db():
    return await asyncpg.create_pool(DATABASE_URL)


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
                SELECT id, hadith_id, source, chapter_no, hadith_no, chapter, chain_indx, text_ar, text_en, 
                       ts_rank(text_searchable, to_tsquery($1)) AS rank
                FROM all_hadith 
                WHERE text_searchable @@ to_tsquery($1)
                ORDER BY rank DESC
                LIMIT 10;
            """
            query_ts = query.replace(" ", " & ")  # Convert query to tsquery format
            rows = await conn.fetch(sql_query, query_ts)

            results = [{
                "id": row["id"],
                "hadith_id": row["hadith_id"],
                "source": row["source"],
                "chapter_no": row["chapter_no"],
                "hadith_no": row["hadith_no"],
                "chapter": row["chapter"],
                "chain_indx": row["chain_indx"],
                "text_ar": row["text_ar"],
                "text_en": row["text_en"],
                "rank": row["rank"]  # Add rank to results
            } for row in rows]

            return {"query": query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

@app.get("/hadith/{id}")
async def get_hadith(id: str):  # id should be a string
    try:
        async with pool.acquire() as conn:
            hadith = await conn.fetchrow("SELECT * FROM all_hadith WHERE id = $1", id)
            if not hadith:
                raise HTTPException(status_code=404, detail="Hadith not found")
            
            return {
                "id": hadith["id"],
                "hadith_id": hadith["hadith_id"],
                "source": hadith["source"],
                "chapter_no": hadith["chapter_no"],
                "hadith_no": hadith["hadith_no"],
                "chapter": hadith["chapter"],
                "chain_indx": hadith["chain_indx"],
                "text_ar": hadith["text_ar"],
                "text_en": hadith["text_en"]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving Hadith: {str(e)}")

@app.get("/hadith/random")
async def get_random_hadith():
    try:
        async with pool.acquire() as conn:
            # Fetch one random row from the table
            row = await conn.fetchrow("SELECT * FROM all_hadith ORDER BY RANDOM() LIMIT 1")
            if not row:
                # Return a specific message if no rows are found
                raise HTTPException(status_code=404, detail="No Hadith found in the database")
            
            # Return the random Hadith data
            return {
                "id": row["id"],
                "hadith_id": row["hadith_id"],
                "source": row["source"],
                "chapter_no": row["chapter_no"],
                "hadith_no": row["hadith_no"],
                "chapter": row["chapter"],
                "chain_indx": row["chain_indx"],
                "text_ar": row["text_ar"],
                "text_en": row["text_en"]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving random Hadith: {str(e)}")

@app.get("/hadith/related/{id}")
async def get_related_hadith(id: str):  # id should be a string
    try:
        async with pool.acquire() as conn:
            # Fetch the chapter or any other identifier for related Hadiths
            row = await conn.fetchrow("SELECT chapter FROM all_hadith WHERE id = $1", id)
            if not row:
                raise HTTPException(status_code=404, detail="Hadith not found")
            
            chapter = row["chapter"]
            
            # Fetch related Hadiths based on the chapter
            related_hadiths = await conn.fetch("""
                SELECT id, hadith_id, source, chapter_no, hadith_no, chapter, chain_indx, text_ar, text_en
                FROM all_hadith
                WHERE chapter = $1
                LIMIT 5;
            """, chapter)
            
            results = [{
                "id": h["id"],
                "hadith_id": h["hadith_id"],
                "source": h["source"],
                "chapter_no": h["chapter_no"],
                "hadith_no": h["hadith_no"],
                "chapter": h["chapter"],
                "chain_indx": h["chain_indx"],
                "text_ar": h["text_ar"],
                "text_en": h["text_en"]
            } for h in related_hadiths]
            
            return {"id": id, "related_hadiths": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching related Hadiths: {str(e)}")
@app.get("/hadith/authenticity/{id}")
async def check_authenticity(id: str):  # id should be a string
    try:
        async with pool.acquire() as conn:
            hadith = await conn.fetchrow("SELECT source, chain_indx FROM all_hadith WHERE id = $1", id)
            if not hadith:
                raise HTTPException(status_code=404, detail="Hadith not found")
            
            source = hadith["source"]
            chain_indx = hadith["chain_indx"]

            # Here, you can implement your logic to check authenticity based on the source and chain.
            # For simplicity, this example assumes Sahih Bukhari is always authentic.
            authenticity = "Sahih" if source == "Sahih Bukhari" else "Da'if"

            return {
                "hadith_id": id,
                "authenticity": authenticity,
                "source": source,
                "chain_indx": chain_indx
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking authenticity: {str(e)}")
