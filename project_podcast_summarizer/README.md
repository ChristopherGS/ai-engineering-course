## Project Local Setup

1. cd into project directory & create virtualenv & activate it
2. `pip install -r requirements.txt`
3. Run the DB migrations `PYTHONPATH=. python prestart.py` (only required once)
4. Run the FastAPI server Python command: `PYTHONPATH=. python app/main.py`
6. Open http://localhost:8001/

## Generating the Podcast Summaries
1. cd into the `project_podcast_summarizer` directory
2. activate your virtual env
3. `PYTHONPATH=. python data_engineering/summarize_transcript.py -t developer_tea_episode_1191.txt`
4. `PYTHONPATH=. python app/update_data.py`
5. Run the FastAPI server Python command: `PYTHONPATH=. python app/main.py`
6. When you open http://localhost:8001/ you should see the summaries


## Troubleshooting
`ModuleNotFoundError: No module named 'project_podcast_summarizer'` - means that you need to add the
`project_podcast_summarizer` directory to your PYTHONPATH. 