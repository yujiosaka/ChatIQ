################
## Base stage ##
################
FROM python:3.10-slim AS base

# Set the working directory for the application
WORKDIR /app

# Set PYTHONUNBUFFERED to ensure immediate output
# for print statements and avoid output buffering.
ENV PYTHONUNBUFFERED 1

COPY pyproject.toml package.json package-lock.json ./

RUN pip install --no-cache-dir uv \
    && uv pip install --system -e .

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
    && uv pip install --system -e .[dev] \
    && uv run pre-commit install

# indicate what port the server is running on
EXPOSE 3000

CMD ["flask", "--app", "chatiq.main:app", "--debug", "run", "--host", "0.0.0.0", "--port", "3000"]

#######################
## Production stage ##
#######################
FROM base AS production

COPY . .

# indicate what port the server is running on
EXPOSE 3000

CMD ["gunicorn", "chatiq.main:app", "--bind", "0.0.0.0:3000"]
