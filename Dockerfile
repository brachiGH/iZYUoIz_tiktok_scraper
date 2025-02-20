FROM selenium/standalone-chrome:97.0-20250202

WORKDIR /app

# Switch to root to install packages
USER root
RUN chown -R 1200:1200 /app

# Install Python 3.11 and other dependencies
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y python3.11 python3.11-venv && rm -rf /var/lib/apt/lists/*

# Switch back to a non-root user for security
USER 1200

# Create a virtual environment and install dependencies
RUN python3.11 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY ./IzYOuIz_tiktok_scraper .

# Expose necessary ports
  # Selenium Grid
  # VNC Server (to view browser)
  # Application server
EXPOSE 4444
EXPOSE 5900  
EXPOSE 8000

# Run your application when the container launches
CMD ["uvicorn", "server:app", "--reload"]