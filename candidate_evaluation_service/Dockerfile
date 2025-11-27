FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Install into system python
ENV UV_SYSTEM_PYTHON=1

# Copy project definition
COPY pyproject.toml .

# Install dependencies
# We use `uv pip install .` to install the project and its dependencies defined in pyproject.toml
# We need to copy the source code first if we want to install the project itself, 
# but for caching purposes, we might want to just install dependencies first.
# However, uv pip install . requires the source. 
# Let's just copy everything for now to keep it simple and working.
COPY . .

# Install the project and dependencies
RUN uv pip install .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
