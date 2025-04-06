FROM debian:bullseye

# Install Python, Java, procps and other dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    openjdk-11-jdk \
    procps \ 
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# ... (rest of Dockerfile: update-alternatives, ENV, WORKDIR) ...

# Copy consumer requirements (ensure this file exists!)
COPY ./requirements.txt /app/requirements.txt 
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Set CMD to run your desired consumer script
CMD ["python", "consumer.py"] # Or consumer_simple.py