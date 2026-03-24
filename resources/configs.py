import enum

class Ec2(enum.Enum):
    INSTANCE_NAME = "SharkordServer"
    INSTANCE_KEY_PAIR_NAME = "SharkordServerKeyPair"
    SECURITY_GROUP_NAME = "SharkordSecurityGroup"
    VPC_ID = "vpc-0544dc4cd65532674"

class Iam(enum.Enum):
    CLOUDFLARE_ORIGIN_CERTIFICATE_ARN: r"arn:aws:secretsmanager:us-east-1:473207619138:secret:cloudflare/origin_certificate-y0Qtr5"
