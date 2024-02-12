FROM nginx:1.25.3-alpine3.18
RUN ln -snf /usr/share/zoneinfo/Europe/Moscow /etc/localtime && echo 'Europe/Moscow' > /etc/timezone
COPY ./services/nginx/conf.d/* /etc/nginx/conf.d/
