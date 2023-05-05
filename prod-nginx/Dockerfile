#FROM nginx:1.19.0-alpine
FROM nginx:1.19.8

RUN rm /etc/nginx/conf.d/default.conf
#RUN mkdir /etc/nginx/conf.d
#RUN touch /etc/nginx/conf.d/timeout.conf


COPY nginx.conf /etc/nginx/nginx.conf
#COPY timeout.conf /etc/nginx/conf.d
#COPY index.html /data/www/


COPY dica.conf /etc/nginx/conf.d/dica.conf