import os

from aws_cdk import (
    aws_ec2,
    aws_iam,
)
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
        self.__create_user_data()
        self.__create_instance(role=role)
        self.__create_elastic_ip()

    def __create_security_group(self):
        self.security_group: aws_ec2.SecurityGroup = aws_ec2.SecurityGroup(
            scope=self,
            id="SharkordSecurityGroup",
            vpc=self.vpc,
            allow_all_outbound=True,
            description="Rules for Sharkord server access",
            security_group_name=configs.Ec2.SECURITY_GROUP_NAME.value
        )
        self.security_group.add_ingress_rule(peer=aws_ec2.Peer.any_ipv4(), connection=aws_ec2.Port.tcp(443))
        self.security_group.add_ingress_rule(peer=aws_ec2.Peer.ipv4(os.getenv("SSH_INGRESS_CIDR")), connection=aws_ec2.Port.tcp(22))

    def __create_user_data(self):
        self.user_data = aws_ec2.UserData.for_linux()

        self.user_data.add_commands(
            # update system and install apache
            "sudo yum update -y",
            "sudo yum install -y httpd mod_ssl",

            # fetch cloudflare origin certificate and key
            "aws secretsmanager get-secret-value --secret-id cloudflare/origin_certificate --query SecretString --output text | jq -r .certificate | openssl base64 -A -d > localhost.crt",
            "aws secretsmanager get-secret-value --secret-id cloudflare/origin_certificate --query SecretString --output text | jq -r .key | openssl base64 -A -d > localhost.key",
            "sudo chown root:root localhost.crt localhost.key",
            "sudo chmod 600 localhost.crt localhost.key",
            "sudo mv localhost.crt /etc/pki/tls/certs/",
            "sudo mv localhost.key /etc/pki/tls/private/",

            # create apache reverse proxy config
            "sudo tee /etc/httpd/conf.d/sharkord-proxy.conf > /dev/null << 'EOF'\n"
            "<IfModule mod_ssl.c>\n"
            "<VirtualHost *:443>\n"
            "    ProxyPreserveHost On\n"
            "    ProxyPass / http://localhost:4991/\n"
            "    ProxyPassReverse / http://localhost:4991/\n"
            "</VirtualHost>\n"
            "</IfModule>\n"
            "EOF",

            # start Apache
            "sudo systemctl enable httpd",
            "sudo systemctl start httpd",

            # install sharkord into /opt/sharkord
            "sudo mkdir -p /opt/sharkord",
            "sudo chown ec2-user:ec2-user /opt/sharkord",
            "curl -L 'https://github.com/sharkord/sharkord/releases/latest/download/sharkord-linux-x64' -o /opt/sharkord/sharkord",
            "sudo chmod +x /opt/sharkord/sharkord",

            # create sharkord systemd service
            "sudo tee /etc/systemd/system/sharkord.service > /dev/null << 'EOF'\n"
            "[Unit]\n"
            "Description=Sharkord Server\n"
            "After=network.target\n\n"
            "[Service]\n"
            "Type=simple\n"
            "WorkingDirectory=/opt/sharkord\n"
            "ExecStart=/opt/sharkord/sharkord\n"
            "Restart=always\n"
            "RestartSec=5\n"
            "Environment=\"SHARKORD_AUTOUPDATE=true\"\n"
            "NoNewPrivileges=true\n"
            "PrivateTmp=true\n"
            "ProtectSystem=full\n"
            "ProtectHome=true\n\n"
            "[Install]\n"
            "WantedBy=multi-user.target\n"
            "EOF",

            # enable and start Sharkord service
            "sudo systemctl daemon-reload",
            "sudo systemctl enable sharkord",
            "sudo systemctl start sharkord"
        )

    def __create_instance(self, role: aws_iam.Role):
        self.instance = aws_ec2.Instance(
            scope=self,
            id="SharkordInstance",
            instance_type=aws_ec2.InstanceType.of(
                aws_ec2.InstanceClass.T3,
                aws_ec2.InstanceSize.NANO
            ),
            machine_image=aws_ec2.MachineImage.latest_amazon_linux2023(),
            vpc=self.vpc,
            allow_all_outbound=True,
            allow_all_ipv6_outbound=False,
            associate_public_ip_address=False,
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
            user_data=self.user_data,
            user_data_causes_replacement=True,
            vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PUBLIC)
        )

    def __create_elastic_ip(self):
        self.elastic_ip = aws_ec2.CfnEIP(
            scope=self,
            id="SharkordServerEip",
            domain="vpc"
        )
        _: aws_ec2.CfnEipAssociation = aws_ec2.CfnEIPAssociation(
            scope=self,
            id="SharkordServerEipAssociation",
            eip=self.elastic_ip.ref,
            instance_id=self.instance.instance_id
        )
