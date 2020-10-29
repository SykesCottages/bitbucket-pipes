FROM amazon/aws-cli

RUN yum install jq -y

RUN yum install gettext -y

COPY pipe.sh /

ENTRYPOINT ["/pipe.sh" ]
