FROM registry.access.redhat.com/ubi8/ubi

WORKDIR /services/hotel-v1

COPY requirements.txt .
COPY .openapirc.js .
COPY run.py .
COPY app app
COPY data data

RUN yum clean all

RUN yum install -y python39
RUN python3 -m pip install -r requirements.txt

RUN yum module enable nodejs:12; yum install -y @nodejs:12/common
RUN npm install -g npx; npm install -g openapi-comment-parser

EXPOSE 9101

CMD ["python3", "run.py"]
