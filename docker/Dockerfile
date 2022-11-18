FROM rockylinux:9.0

RUN dnf -y install epel-release dnf-plugins-core
RUN dnf install -y mock
#RUN dnf config-manager --set-enabled powertools

VOLUME /build
VOLUME /result

COPY build.sh /
WORKDIR /build

CMD ["/build.sh"]
