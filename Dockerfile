FROM postgres
ENV POSTGRES_PASSWORD postgres
ENV POSTGRES_DB helpme
COPY data.sql /docker-entrypoint-initdb.d/