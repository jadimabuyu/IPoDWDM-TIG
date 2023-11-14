FROM python:3.7.17-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apk add --update --no-cache gcc libffi-dev musl-dev  && pip3 install --no-cache-dir -r requirements.txt

COPY juniperCORAmonitor.py .

CMD [ "python3", "./juniperCORAmonitor.py" ]