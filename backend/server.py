from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from ir_system import IRSystem

app = FastAPI()

# Initialize IR system
corpus_dir = os.path.join(os.path.dirname(__file__), "Corpus")
index_dir = os.path.join(os.path.dirname(__file__), "index")
ir_system = IRSystem(corpus_dir=corpus_dir, index_dir=index_dir)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your Next.js frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get list of all corpus files
@app.get("/api/corpus")
async def get_corpus_files():
    corpus_dir = os.path.join(os.path.dirname(__file__), "Corpus")
    files = [f.replace(".txt", "") for f in os.listdir(corpus_dir) if f.endswith(".txt")]
    return {"files": files}

# Get content of a specific corpus file
@app.get("/api/corpus/{file_name}")
async def get_corpus_content(file_name: str):
    try:
        file_path = os.path.join(os.path.dirname(__file__), "Corpus", f"{file_name}.txt")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content}
    except FileNotFoundError:
        return {"error": "File not found"}

@app.post("/api/search")
async def search(
    query: str = Query(..., description="Search query"),
    use_soundex: bool = Query(False, description="Enable Soundex matching"),
    use_spellcorrection: bool = Query(False, description="Enable spell correction")
):
    try:
        results = ir_system.search(
            query=query,
            use_soundex=use_soundex,
            use_spellcorrection=use_spellcorrection
        )
        
        return {
            "results": [
                {
                    "document": doc.replace(".txt", ""),
                    "score": score,
                    "snippet": get_document_snippet(doc, query)
                }
                for doc, score in results
            ]
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Search failed: {str(e)}"}
        )

@app.post("/api/rebuild-index")
async def rebuild_index():
    """Rebuild the search index"""
    try:
        ir_system.build_index()
        return {"message": "Index rebuilt successfully"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to rebuild index: {str(e)}"}
        )

def get_document_snippet(doc_name: str, query: str, snippet_length: int = 200) -> str:
    """Get a relevant snippet from the document containing query terms"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), "Corpus", doc_name)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # For now, just return the first snippet_length characters
        # This could be improved to return a more relevant snippet
        return content[:snippet_length] + "..." if len(content) > snippet_length else content
    except Exception:
        return ""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)