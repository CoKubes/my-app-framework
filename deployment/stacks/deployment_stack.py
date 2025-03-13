from aws_cdk import Stack, aws_ecs as ecs, aws_ec2 as ec2, aws_elasticloadbalancingv2 as elbv2, aws_logs as logs
from constructs import Construct
from aws_cdk import Duration

class MyAppFrameworkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC
        vpc = ec2.Vpc(self, "MyVPC", max_azs=2)

        # ECS Cluster
        cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)

        # CloudWatch Log Group
        log_group = logs.LogGroup(self, "MyLogGroup", log_group_name="/ecs/my-fastapi-app")

        # Task Definition
        task_definition = ecs.FargateTaskDefinition(
            self, "MyTaskDef",
            cpu=256,
            memory_limit_mib=512
        )

        # Backend Container
        container = task_definition.add_container(
            "AppContainer",
            image=ecs.ContainerImage.from_registry("662244660081.dkr.ecr.us-east-1.amazonaws.com/my-fastapi-app:backend-setup"),
            port_mappings=[ecs.PortMapping(container_port=8000)],
            environment={"AWS_REGION": "us-east-1"},
            logging=ecs.LogDrivers.aws_logs(stream_prefix="app", log_group=log_group)  # Use log_group object
        )

        # X-Ray Daemon Container
        task_definition.add_container(
            "XRayDaemon",
            image=ecs.ContainerImage.from_registry("amazon/aws-xray-daemon:latest"),
            port_mappings=[ecs.PortMapping(container_port=2000, protocol=ecs.Protocol.UDP)]
        )

        # Fargate Service
        service = ecs.FargateService(
            self, "MyService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=1
        )

        # Application Load Balancer
        alb = elbv2.ApplicationLoadBalancer(self, "MyALB", vpc=vpc, internet_facing=True)
        listener = alb.add_listener("Listener", port=80)
        target_group = listener.add_targets(
            "Targets",
            port=8000,
            targets=[service],
            health_check=elbv2.HealthCheck(path="/", interval=Duration.seconds(30))
        )