FROM phusion/baseimage

ADD nginx.sh /setup.sh
RUN /setup.sh

COPY entrypoint.py /entrypoint.py
RUN chmod +x /entrypoint.py

COPY etc.py /etc.py
RUN chmod +x /etc.py

COPY nginx /etc/nginx

ONBUILD COPY nginx /etc/nginx

ENTRYPOINT ["/entrypoint.py"]
