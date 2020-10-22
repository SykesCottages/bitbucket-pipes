FROM rust:1.47.0

RUN wget https://github.com/aws-cloudformation/cloudformation-guard/releases/download/1.0.0/cfn-guard-linux-1.0.0.tar.gz

RUN tar -xvf cfn-guard-linux-1.0.0.tar.gz

WORKDIR ./cfn-guard-linux

COPY pipe.sh /

ENTRYPOINT [ "/pipe.sh" ]

