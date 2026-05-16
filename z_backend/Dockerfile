# Use a lightweight Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies into the container's environment
# We use --frozen to ensure version consistency
RUN uv sync --frozen --no-install-project

# Copy the rest of the application
COPY . .

# Expose the API port
EXPOSE 8000

# Use 'uv run' to ensure we use the managed environment
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
