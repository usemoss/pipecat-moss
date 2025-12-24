# 1. Get Python 3.11 from official image
FROM python:3.11-slim-bookworm AS python-source

# 2. Start from Pipecat base
FROM dailyco/pipecat-base:latest

WORKDIR /app

# 3. Copy Python 3.11 over
COPY --from=python-source /usr/local /usr/local
RUN ldconfig

# --- KEY FIX ---
# 4. Remove the old venv folder
RUN rm -rf /app/.venv

# 5. Reset the PATH to point to system folders only (ignoring the deleted venv)
#    and clear the VIRTUAL_ENV variable so Python doesn't get confused.
ENV PATH="/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin"
ENV VIRTUAL_ENV=""
# ---------------

# 6. Now 'pip' will install globally to /usr/local/lib/python3.11/site-packages
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./src ./src
COPY ./examples ./examples

ENV PYTHONPATH=/app