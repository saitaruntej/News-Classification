FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose ports for FastAPI and Streamlit
EXPOSE 8000
EXPOSE 8501

# Create a startup script to run both services
RUN echo '#!/bin/bash\nuvicorn api:app --host 0.0.0.0 --port 8000 &\nstreamlit run app.py --server.port 8501 --server.address 0.0.0.0\n' > start.sh
RUN chmod +x start.sh

CMD ["./start.sh"]
