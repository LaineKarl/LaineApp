FROM python:3.8-slim
RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/app/raamatud
WORKDIR /usr/src/app
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
COPY hs9-flask-api-raamatute-otsing.py app.py
EXPOSE 5000
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
