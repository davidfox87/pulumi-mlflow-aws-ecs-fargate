from pulumi import ComponentResource, ResourceOptions
import pulumi_aws as aws



class RDSDbArgs:
    """_summary_"""

    def __init__(
        self,
        db_name=None,
        db_user=None,
        db_password=None,
        subnets=None,
        security_group_ids=None,
        allocated_storage=20,
        engine="mysql",
        engine_version="5.7",
        instance_class='db.t2.micro',
        storage_type="gp2",
        skip_final_snapshot=True,
        publicly_accessible=False,
    ):

        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.subnets = subnets
        self.security_group_ids = security_group_ids
        self.allocated_storage = allocated_storage
        self.engine = engine
        self.engine_version = engine_version
        self.instance_class = instance_class
        self.storage_type = storage_type
        self.skip_final_snapshot = skip_final_snapshot
        self.publicly_accessible = publicly_accessible

class RDSDb(ComponentResource):
    """_summary_
    Args:
        ComponentResource (_type_): _description_
    """

    def __init__(self, name: str, args: RDSDbArgs, opts: ResourceOptions = None):

        super().__init__("mlflow:backend_store", name, {}, opts)

        # Create RDS subnet group to put RDS instance on.
        subnet_group_name = f"{name}-sng"
        rds_subnet_group = aws.rds.SubnetGroup(
            subnet_group_name,
            subnet_ids=args.subnets,
            tags={"Name": subnet_group_name},
            opts=ResourceOptions(parent=self),
        )

        rds_name = f"{name}-rds"
        self.db = aws.rds.Instance(
            rds_name,
            db_name=args.db_name,
            allocated_storage=args.allocated_storage,
            engine=args.engine,
            engine_version=args.engine_version,
            instance_class=args.instance_class,
            storage_type=args.storage_type,
            db_subnet_group_name=rds_subnet_group.id,
            username=args.db_user,
            password=args.db_password,
            vpc_security_group_ids=args.security_group_ids,
            skip_final_snapshot=args.skip_final_snapshot,
            publicly_accessible=args.publicly_accessible,
            opts=ResourceOptions(parent=self),
        )

        self.register_outputs({})