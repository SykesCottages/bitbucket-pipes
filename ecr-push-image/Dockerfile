FROM amazon/aws-cli

RUN yum install jq -y

COPY pipe.sh /

ENTRYPOINT ["/pipe.sh" ]
