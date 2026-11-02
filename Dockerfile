FROM python:3.8-slim-buster

WORKDIR /app
COPY ./requirements.txt ./

RUN sed -i 's|deb.debian.org|archive.debian.org|g; s|security.debian.org|archive.debian.org|g; /buster-updates/d' /etc/apt/sources.list && \
    echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99archive && \
    apt-get update && \
    apt-get install -y --no-install-recommends g++ && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt --default-timeout=1000 --no-cache-dir

# Copy remaining files into working directory
COPY . .

CMD [ "python3", "-m", "uvicorn", "monitoring_service.monitoring_api:app", "--host=0.0.0.0", "--port=5000", "--reload"]
