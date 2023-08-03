FROM python:3.9

ADD bot_attempt_4.py .

RUN pip install alpaca-py

CMD ["python", "./bot_attempt_4.py"]