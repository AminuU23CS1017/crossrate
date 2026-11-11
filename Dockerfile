FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home tracker
COPY --chown=tracker:tracker . .
RUN mkdir /data && chown tracker:tracker /data
USER tracker
ENV DATABASE_URL=sqlite:////data/rates.db
EXPOSE 8000
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
