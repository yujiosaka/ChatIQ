################
## Base stage ##
################
FROM python:3.10-slim AS base

# Set the working directory for the application
WORKDIR /app

# Set PYTHONUNBUFFERED to ensure immediate output
# for print statements and avoid output buffering.
ENV PYTHONUNBUFFERED 1

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml package.json package-lock.json ./

# Install dependencies
RUN uv sync --frozen

#######################
## Development stage ##
#######################
FROM base AS development

# Install Node.js, Git, and other dependencies
RUN apt-get update && apt-get install -y curl git && \
    curl -sL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    # Clean up APT when done
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY . .

# Install Node.js dependencies
RUN npm install

# Initialize an empty Git repository
# for allowing pre-commit install to run without errors.
RUN git init \
    && uv sync --dev \
    && uv run pre-commit install

# indicate what port the server is running on
EXPOSE 3000

CMD ["flask", "--app", "chatiq.main:app", "--debug", "run", "--host", "0.0.0.0", "--port", "3000"]

#######################
## Production stage ##
#######################
FROM base AS production

# Copy application code
COPY . .

# Set PATH to include UV tool bin directory
ENV PATH="/usr/local/bin:${PATH}"

# indicate what port the server is running on
EXPOSE 3000

CMD ["gunicorn", "chatiq.main:app", "--bind", "0.0.0.0:3000"]
