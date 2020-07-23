FROM python:3

RUN pip install --upgrade pip

RUN useradd -ms /bin/bash worker
USER worker
WORKDIR /home/worker

COPY --chown=worker:worker requirements.txt .
RUN pip install --user -r requirements.txt


COPY --chown=worker:worker src/ app/

CMD ["python", "app/main.py"]