FROM amazon/aws-cli

RUN yum install jq -y

RUN yum install gettext -y

COPY ecs-deploy /

ENTRYPOINT ["/ecs-deploy" ]
