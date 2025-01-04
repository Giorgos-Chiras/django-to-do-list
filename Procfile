web: uvicorn List.wsgi
worker: celery -A List worker --loglevel=info
beat: celery -A List beat --loglevel=info