FROM nginx:1.25.3-alpine3.18
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
COPY ./services/nginx/conf.d/* /etc/nginx/conf.d/
