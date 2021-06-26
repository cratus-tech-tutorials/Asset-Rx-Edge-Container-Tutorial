FROM nvcr.io/nvidia/l4t-pytorch:r32.5.0-pth1.7-py3

LABEL maintainer="Gibson Martin" \
    email="gibson@cratustech.com"

RUN apt-get update

COPY ./requirements.txt /requirements.txt

WORKDIR /

RUN pip3 install -r requirements.txt

COPY . /

EXPOSE 8080 8080

ENTRYPOINT [ "python3" ]

CMD [ "/app/app.py" ]
