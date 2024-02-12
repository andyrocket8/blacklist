FROM redis:7.2.3-alpine3.18
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# use default configuration. Substitute with custom volume mapping on start
COPY ./services/redis/redis.conf /usr/local/etc/redis/redis.conf
RUN touch /usr/local/etc/redis/users.acl
# copy custom ACL file to /usr/local/etc/redis/
COPY ./services/redis/users.acl* /usr/local/etc/redis/
ENTRYPOINT [ "redis-server", "/usr/local/etc/redis/redis.conf" ]
