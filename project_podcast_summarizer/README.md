## Project Local Setup

1. cd into project directory & create virtualenv & activate it
2. `pip install -r requirements.txt`
3. Run the DB migrations `PYTHONPATH=. python prestart.py` (only required once)
4. Run the FastAPI server via poetry with the Python command: `poetry run python app/main.py`
6. Open http://localhost:8001/

## Troubleshooting
`ModuleNotFoundError: No module named 'project_podcast_summarizer'` - means that you need to add the
`project_podcast_summarizer` directory to your PYTHONPATH. 