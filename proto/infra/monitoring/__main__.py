import pulumi
from pulumi import export, Output, ResourceOptions
from prometheus import PrometheusArgs, Prometheus



config = pulumi.Config()
service_name = config.get('service_name') or 'example'
networkingStack = pulumi.StackReference(config.require('NetworkingStack'))


# for this to work, two docker images have to be built:
# 1) ecs_sd for automatic service discovery and writing of the /etc/config/ecs_auto_sd.yaml
# 2) prometheus for the custom prom image with the prometheus.yaml config file bind mounted to a VOLUME 
#    that will end up in the ecs-task-def
prom = Prometheus(
    f'{service_name}-prometheus-ecs',
    PrometheusArgs(
        vpc_id=networkingStack.get_output("vpc_id"),
        subnet_ids=[networkingStack.get_output("private_subnet1"),
                    networkingStack.get_output("private_subnet2")
        ],
        sg_groups=[networkingStack.get_output("prom_server_sg"), # allows prom server to send metrics to timescaledb for long-term storage
                   networkingStack.get_output("grafana_sg") # allows grafana dashboard access
        ],
        ecs_cluster_arn=networkingStack.get_output("ecs_cluster_arn"),
    )
)