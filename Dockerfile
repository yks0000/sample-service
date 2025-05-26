# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install Poetry
# We use a specific version to ensure reproducible builds.
# You might want to pin this to a version you prefer.
RUN pip install poetry==2.1.2

# Copy only the Poetry configuration files first to leverage Docker's build cache.
# If these files don't change, Docker won't re-run the 'poetry install' step.
COPY pyproject.toml poetry.lock ./

# Install project dependencies
# The --no-root flag prevents installing the project itself as a package,
# which is useful when you're just copying the source code directly.
# The --no-dev flag ensures dev dependencies are not installed.
RUN poetry install --no-root

# Copy the rest of your application code
# This copies the 'sample_app' directory and any other necessary files
COPY . .

# Expose the port your Flask app runs on
EXPOSE 8000

# Command to run the application
# We use 'poetry run' to ensure the app runs within the Poetry virtual environment
# The app.py is located inside the sample_app directory
CMD ["poetry", "run", "python", "sample_app/app.py"]