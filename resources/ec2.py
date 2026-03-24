import os

from aws_cdk import aws_ec2, aws_iam
from constructs import Construct

from resources import configs


class SharkordServer(Construct):
    def __init__(self, scope: Construct, id: str, role: aws_iam.Role):
        super().__init__(scope=scope, id=id)
        self.vpc: aws_ec2.Vpc = aws_ec2.Vpc.from_lookup(
            scope=self,
            id=id,
            vpc_id=configs.Ec2.VPC_ID.value
        )
        self.__create_security_group()
        # self.__create_user_data()
        self.__create_instance(role=role)
        
    def __create_security_group(self):
        self.security_group: aws_ec2.SecurityGroup = aws_ec2.SecurityGroup(
            scope=self,
            id="SharkordSecurityGroup",
            vpc=self.vpc,
            allow_all_outbound=True,
            description="Rules for Sharkord server access",
            security_group_name=configs.Ec2.SECURITY_GROUP_NAME.value
        )
        self.security_group.add_ingress_rule(peer=aws_ec2.Peer.any_ipv4(), connection=aws_ec2.Port.tcp(port=443))
        self.security_group.add_ingress_rule(peer=aws_ec2.Peer.ipv4(cidr_ip=os.getenv(key="SSH_INGRESS_CIDR")), connection=aws_ec2.Port.tcp(port=22))

    def __create_user_data(self):
        self.user_data: aws_ec2.UserData = aws_ec2.UserData.for_linux()
        self.user_data.add_commands(
            "cd",
            "sudo yum update -y",
            "export SHARKORD_AUTOUPDATE=true",
            "sudo curl -L 'https://github.com/sharkord/sharkord/releases/latest/download/sharkord-linux-x64' -o sharkord",
            "sudo chmod +x sharkord",
            "sudo yum install -y httpd mod_ssl",
            "sudo systemctl start httpd",
            "aws secretsmanager get-secret-value --secret-id cloudflare/origin_certificate --query SecretString --output text | jq -r .certificate | openssl base64 -A -d > localhost.crt",
            "sudo chown root:root localhost.crt",
            "sudo chmod 600 localhost.crt",
            "sudo mv localhost.crt /etc/pki/tls/certs/",
            "aws secretsmanager get-secret-value --secret-id cloudflare/origin_certificate --query SecretString --output text | jq -r .key | openssl base64 -A -d > localhost.key",
            "sudo chown root:root localhost.key",
            "sudo chmod 600 localhost.key",
            "sudo mv localhost.key /etc/pki/tls/private/",
            "printf 'ProxyPass \"/\" \"127.0.0.1:4991\"\n' | sudo tee -a /etc/httpd/conf.d/ssl.conf",
            "printf 'ProxyPassReverse \"/\" \"127.0.0.1:4991\"\n' | sudo tee -a /etc/httpd/conf.d/ssl.conf",
            "sudo systemctl restart httpd",
            "./sharkord"
        )

    def __create_instance(self, role: aws_iam.Role):
        self.instance: aws_ec2.Instance = aws_ec2.Instance(
            scope=self,
            id="SharkordInstance",
            instance_type=aws_ec2.InstanceType.of(
                instance_class=aws_ec2.InstanceClass.T3,
                instance_size=aws_ec2.InstanceSize.NANO
            ),
            machine_image=aws_ec2.MachineImage.latest_amazon_linux2023(),
            vpc=self.vpc,
            allow_all_ipv6_outbound=False,
            allow_all_outbound=True,
            associate_public_ip_address=True,
            credit_specification=aws_ec2.CpuCredits.STANDARD,
            disable_api_termination=False,
            ebs_optimized=False,
            enclave_enabled=False,
            hibernation_enabled=False,
            http_endpoint=True,
            http_protocol_ipv6=False,
            instance_initiated_shutdown_behavior=aws_ec2.InstanceInitiatedShutdownBehavior.STOP,
            instance_name=configs.Ec2.INSTANCE_NAME.value,
            key_pair=aws_ec2.KeyPair(
                scope=self,
                id="SharkordKeyPair",
                key_pair_name=configs.Ec2.INSTANCE_KEY_PAIR_NAME.value
            ),
            role=role,
            security_group=self.security_group,
            ssm_session_permissions=True,
            vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PUBLIC)
        )
