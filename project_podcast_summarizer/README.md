## Project Local Setup

1. cd into project directory & create virtualenv & activate it
2. `pip install -r requirements.txt`
3. Run the DB migrations `PYTHONPATH=. python prestart.py` (only required once)
4. Run the FastAPI server Python command: `PYTHONPATH=. python app/main.py`
6. Open http://localhost:8001/

n.b. the alembic migrations are already generated for you. If you wanted to
create a new migration you would run: `PYTHONPATH=. alembic revision --autogenerate -m "DESCRIPTION"`

## Generating the Podcast Summaries
1. cd into the `project_podcast_summarizer` directory
2. activate your virtual env
3. Summarize first episode: `PYTHONPATH=. python data_engineering/summarize_transcript.py -t developer_tea_episode_1191.txt`
4. Summarize second episode: `PYTHONPATH=. python data_engineering/summarize_transcript.py -t 9_years_persistence.txt`
5. `PYTHONPATH=. python app/update_data.py`
6. Run the FastAPI server Python command: `PYTHONPATH=. python app/main.py`
7. When you open http://localhost:8001/ you should see the summaries


## Troubleshooting
`ModuleNotFoundError: No module named 'project_podcast_summarizer'` - means that you need to add the
`project_podcast_summarizer` directory to your PYTHONPATH. 