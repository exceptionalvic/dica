FROM python:3.8-alpine

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add --update --virtual .tmp gcc py3-grpcio g++ libc-dev linux-headers \
    && apk add cmake libstdc++ libgcc g++ make jpeg jpeg-dev libpng libpng-dev giflib giflib-dev \
    && apk add openblas sdl2-dev freetype freetype-dev py3-opencv sdl_mixer \
	&& apk add tcl-dev tiff-dev musl-dev python3-dev postgresql-dev libpq nano libffi-dev py-cffi \
	&& apk add openssl-dev coreutils cargo dos2unix postgresql-client openssh-client rustup certbot certbot-nginx gfortran openblas-dev lapack-dev

RUN pip install --upgrade pip
RUN pip install --upgrade pip setuptools wheel
# RUN pip install opencv-python==4.5.5.64 --verbose


COPY ./requirements.txt /usr/src/app/requirements.txt

RUN pip install -r requirements.txt

# Update numpy
# RUN pip install -U numpy
# # to cache opencv errors
# RUN pip install imgaug

#RUN apk del .tmp

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

COPY . /usr/src/app/

RUN chmod +x entrypoint.sh

RUN mkdir -p media
RUN mkdir -p staticfiles

RUN chmod -R 755 media
RUN chmod -R 755 staticfiles

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]