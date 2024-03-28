FROM ubuntu:mantic-20240216

RUN apt-get update; \
    apt-get install python3 python3-venv libaugeas0 -y; \
    python3 -m venv /opt/next-century-pay-hoa/;

WORKDIR /opt/next-century-pay-hoa/

COPY . .
RUN bin/pip3 install -r requirements.txt

ENTRYPOINT ["bin/python3", "main.py"]