FROM node:19-alpine

WORKDIR /app

# Install python dependencies
COPY ./package.json ./package-lock.json ./

RUN apk add \
        build-base \
        pkgconfig \
        autoconf \
        automake \
        libtool \
        nasm \
        libffi-dev \
        libxml2-dev \
        libxslt-dev \
        jpeg-dev \
        zlib-dev \
        libpng-dev \
        freetype-dev \
    && npm install