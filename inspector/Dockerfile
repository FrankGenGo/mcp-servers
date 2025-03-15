FROM node:20-alpine

WORKDIR /app

# Install curl for healthchecks and Python
RUN apk add --no-cache curl python3 py3-pip

# Create Python virtual environment outside of /app to avoid volume mount issues
RUN python3 -m venv /venv

# Set environment path to use the virtual environment by default
ENV PATH="/venv/bin:$PATH"
ENV VIRTUAL_ENV="/venv"

# Copy all project files first to avoid prepare script issues
COPY . .

# Install dependencies in the main package and client
RUN npm install --ignore-scripts && \
    cd client && npm install

# Install Python dependencies in the virtual environment
# We specifically use the venv's pip to ensure requirements are installed in the venv
RUN /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r /app/requirements.txt

# Verify Python environment
RUN /venv/bin/python -c "import sys; print(f'Using Python: {sys.executable}')" && \
    /venv/bin/pip list

# Build the application manually
RUN npm run build-server && \
    npm run build-client

# Expose ports
EXPOSE 5173 3000

# Set the default command
CMD ["npm", "run", "dev"]