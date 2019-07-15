FROM python:3.7
WORKDIR /app/
COPY . /app

RUN pip install -r requirements
RUN ls -la

ENTRYPOINT [ "python" ]
CMD [ "main.py" ]