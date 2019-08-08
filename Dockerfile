FROM python:3.7-alpine
MAINTAINER Jonas Als Christensen "jonas.christensen@sesam.io"
COPY . .
WORKDIR /
RUN pip install -r requirements.txt
EXPOSE 5000/tcp
ENTRYPOINT ["python"]
CMD ["main.py"]