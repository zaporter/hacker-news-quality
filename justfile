download-hf-data:
    mkdir -p data/raw_comments
    uv tool run --from huggingface_hub hf download open-index/hacker-news --repo-type dataset --include "data/*" --local-dir data/raw_comments

# Rate a random sample of comments per month with Jev, e.g. `just jev 100` or `just jev 200 --dry-run --first 2024-01`
jev per_month="200" *args:
    uv run python -m hn_quality.rate jev --per-month {{per_month}} {{args}}

# Same sample, rated with OpenAI's Decisions API
openai per_month="200" *args:
    uv run python -m hn_quality.rate openai --per-month {{per_month}} {{args}}

# Aggregate each model's data/raw_analysis parquet into web/public/data-<model>.json for the viewer
export:
    uv run python -m hn_quality.export jev-monthly-v4 jev
    uv run python -m hn_quality.export openai-monthly-v4 openai

web: export
    cd web && npm install && npm run dev

# Build the Docker image (serves the static site on port 8000)
build-docker:
    docker build -t hnquality.zackporter.com web

# Run the Docker container on port 8000
run-docker:
    docker rm -f hnquality.zackporter.com
    docker run -d -p 8000:8000 --name hnquality.zackporter.com hnquality.zackporter.com

# Push the Docker image to ECR
push-ecr:
    aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 330298988091.dkr.ecr.us-east-2.amazonaws.com
    docker tag hnquality.zackporter.com:latest 330298988091.dkr.ecr.us-east-2.amazonaws.com/hnquality.zackporter.com:latest
    docker push 330298988091.dkr.ecr.us-east-2.amazonaws.com/hnquality.zackporter.com:latest
