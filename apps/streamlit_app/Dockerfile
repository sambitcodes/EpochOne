FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && rm -rf /var/lib/apt/lists/*

COPY apps/streamlit_app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY apps/streamlit_app /app

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]