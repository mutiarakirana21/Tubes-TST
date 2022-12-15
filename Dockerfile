FROM python:3.8.0

WORKDIR /user/src/app

COPY './requirements.txt' .

RUN pip install -r requirements.txt

COPY . .

# ENTRYPOINT [ "flask", "-debug", "run" ]

CMD [ "python", "main.py" ]