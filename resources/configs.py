import enum

class Ec2(enum.Enum):
    INSTANCE_NAME = "SharkordServer"
    INSTANCE_KEY_PAIR_NAME = "SharkordServerKeyPair"
    SECURITY_GROUP_NAME = "SharkordSecurityGroup"
    VPC_ID = "vpc-0544dc4cd65532674"

class Ssm(enum.Enum):
    SERVER_HOSTNAME_PARAM = "/sharkord/server_hostname"
