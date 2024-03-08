## New Additions

- Data Engineering Now Generates the Index Store
- App now loads the index store
- Chatbot Queries now operate with RAG

## New Project Local Setup
- cd into project_rag directory
- Create new virtualenv and activate it
- pip install -r requirements.txt
- PYTHONPATH=../ python data_engineering/rag_index_generator.py  # note this uses the parent directory for PYTHONPATH

If you get:
```shell
Traceback (most recent call last):
  File "/PATH/TO/REPO/ai-engineering-course/project_rag/data_engineering/rag_index_generator.py", line 12, in <module>
    from shared.settings import DATA_DIR, BASE_DIR
ModuleNotFoundError: No module named 'shared'
```
It is because you have not appended the repo root directory to your PYTHONPATH environment variable

## Code New Additions
- RAG index generation (offline)
- New endpoint with chat inference (online)
- New chatbot template (online)
- RAG capabilities for this endpoint (online + deps.py)
- Split out config and New evar


## Project Local Setup (Same as previous project)

1. cd into project directory & create virtualenv & activate it
2. `pip install -r requirements.txt`
3. Run the DB migrations `PYTHONPATH=. python prestart.py` (only required once)
4. Run the FastAPI server Python command: `PYTHONPATH=. python app/main.py`
6. Open http://localhost:8001/


## Troubleshooting
`ModuleNotFoundError: No module named 'project_rag'` - means that you need to add the
`project_rag` directory to your PYTHONPATH. 