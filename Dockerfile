FROM python:3.6-alpine

COPY requirements.txt /
RUN pip install -r /requirements.txt
RUN apk add --no-cache git dumb-init

ADD ./sonarcheck_analyzer.py /bin/sonarcheck_analyzer.py

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["python3" "/bin/sonarcheck_analyzer.py"]
