import json
import boto3
import logging
import asyncio
import argparse
from aiohttp import web
import sys
import signal
import yaml

logger = logging.getLogger(__name__)

class Discoverer:
    """_summary_
    """
    def __init__(self, file, cluster):
        self.file = file
        self.cluster = cluster
        self.tasks = {}      # ecs tasks cache

        try:
            self.ecs_client = boto3.client('ecs')
            self.ecs_client.list_clusters()  # check creds on start
        except Exception as e:
            sys.exit(e)

    async def loop(self, interval):
        """_summary_

        Args:
            interval (_type_): _description_
        """
        signal.signal(signal.SIGINT, self.signal_handler)
        loop = asyncio.get_event_loop()

        while True:
            try:
                await asyncio.wait_for(loop.run_in_executor(None, self.get_cluster_tasks), timeout=interval)
            except asyncio.exceptions.TimeoutError:
                logger.error('Timeout while reading ECS Tasks! Try to increase --interval')
            except Exception:
                logger.error('Read tasks error:', exc_info=True)

            await asyncio.sleep(interval)


    def get_cluster_tasks(self) -> dict:
        """_summary_

        Args:
            ecs_client (_type_): _description_

        Returns:
            dict: _description_
        """
        cluster_arns_paginator = self.ecs_client.get_paginator('list_clusters').paginate()
        cluster_arns = []
        for page in cluster_arns_paginator:
            cluster_arns.extend(page['clusterArns'])
        for cluster_arn in cluster_arns:
            logger.info("Cluster ARN %s", cluster_arn)
            cluster_task_arns_paginator = self.ecs_client.get_paginator('list_tasks').paginate(cluster=cluster_arn)
            cluster_task_definitions = []
            for page in cluster_task_arns_paginator:
                cluster_task_arns = page['taskArns']
                if len(cluster_task_arns) == 0:
                    cluster_page_task_definitions = {'tasks': []}
                else:
                    cluster_page_task_definitions = self.ecs_client.describe_tasks(
                        cluster=cluster_arn, tasks=cluster_task_arns
                    )
                cluster_task_definitions.extend(cluster_page_task_definitions['tasks'])
            self.tasks[cluster_arn] = cluster_task_definitions

        self.to_config_items()


    def to_config_items(self) -> list:
        """_summary_

        Args:
            cluster_tasks (_type_): _description_
            default_port (_type_): _description_

        Returns:
            list: _description_
        """
        items = []
        for cluster_arn in self.tasks.keys():
            cluster_task_definitions = self.tasks[cluster_arn]
            for task in cluster_task_definitions:
                port = 8080
                labels = dict(
                    (k, task.get(k, '')) for k in [
                        'clusterArn',
                        'taskArn',
                        'taskDefinitionArn',
                        'lastStatus',
                        'cpu',
                        'memory',
                        'startedBy',
                        'group',
                        'launchtype',
                    ]
                )
                ip_address = None
                for container in task.get('containers', []):
                    for network_interface in container.get('networkInterfaces', []):
                        ip_address = network_interface.get('privateIpv4Address')
                if ip_address is None:
                    logger.info("Skipping task: no IP address %s", str(labels))
                else:
                    items.append(
                        dict(
                            targets=[f"{ip_address}:{port}"],
                            labels=labels
                        )
                    )
        logger.info("scrape targets written: %s", print(json.dumps(items, indent=4)))
        with open(self.file, 'w') as f:
            yaml.dump(items, f)

        print(json.dumps(items, indent=4)) # save to /tmp/ecs_auto_sd.yaml
        return items




    @staticmethod
    def signal_handler(num, frame):
        """_summary_

        Args:
            num (_type_): _description_
            frame (_type_): _description_
        """
        sys.exit(0)




class Metrics:
    """_summary_
    """
    def __init__(self, cluster):
        self.cluster = cluster
        self.ecs_client = boto3.client('ecs')

    async def handler(self, request) -> dict:
        """_summary_

        Args:
            request (_type_): _description_

        Returns:
            dict: _description_
        """
        res=""
        for cluster in self.ecs_client.list_clusters().get('clusterArns', []):
            for page in self.ecs_client.get_paginator('list_services').paginate(cluster=cluster):
                for arn in page.get('serviceArns', []):
                    logger.info("Service ARN %s", arn)
                    service = self.ecs_client.describe_services(cluster=cluster, services=[arn])['services'][0]
                    res += f'ecs_service_running_tasks{{service="{service["serviceName"]}"}} {service["runningCount"]}\n'


        return web.Response(text=res)



async def start_background_tasks(app):
    """_summary_

    Args:
        app (_type_): _description_
    """
    app['discovery'] = asyncio.create_task(Discoverer(app['args'].file, 
                                                      app['args'].cluster).loop(app['args'].interval))

async def cleanup_background_tasks(app):
    """_summary_

    Args:
        app (_type_): _description_
    """
    app['discovery'].cancel()
    await app['discovery']


if __name__ == "__main__":

    # Also check out 
    # https://github.com/sepich/prometheus-ecs-sd/blob/master/prometheus-ecs-sd.py
    print("hello")

    parser = argparse.ArgumentParser(prog='prometheus-ecs-sd', description='Prometheus file discovery for AWS ECS')
    parser.add_argument('-f', '--file', type=str, default='/tmp/ecs_file_sd.yml', help='File to write tasks (default: /tmp/ecs_file_sd.yml)')
    parser.add_argument('-c', '--cluster', type=str, default='', help='Return metrics only for this Cluster name (default: all)')
    parser.add_argument('-i', '--interval', type=int, default=60, help='Interval to discover ECS tasks, seconds (default: 60)')
    parser.add_argument('-l', '--log', choices=['debug', 'info', 'warn'], default='info', help='Logging level (default: info)')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Port to serve /metrics (default: 8080)')
    args = parser.parse_args()
    logger.setLevel(getattr(logging, args.log.upper()))

    args = parser.parse_args()

    app = web.Application()
    app['args'] = args
    # This will be the endpoint exposed to get metrics related to services and containers/tasks
    #app.router.add_get("/metrics", Metrics(args.cluster).handler)
    logger.info("hello")
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    web.run_app(app, port=args.port, access_log=logger)
