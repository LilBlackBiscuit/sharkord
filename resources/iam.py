import os

from aws_cdk import aws_iam
from constructs import Construct


CERTIFICATE_ARN: str = os.getenv(key="CLOUDFLARE_ORIGIN_CERTIFICATE_SECRET_ARN")


class SharkordIam(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope=scope, id=id)
        self.__create_server_role()

    def __create_server_role(self):
        self.server_role: aws_iam.Role = aws_iam.Role(
            scope=self,
            id="SharkordServerRole",
            assumed_by=aws_iam.ServicePrincipal(service="ec2.amazonaws.com"),
            description="Role for Sharkord server permissions"
        )
        self.server_role.attach_inline_policy(
            policy=aws_iam.Policy(
                scope=self,
                id="SharkordServerSecretsManagerPolicy",
                document=aws_iam.PolicyDocument(
                    statements=[
                        aws_iam.PolicyStatement(
                            sid="SharkordServerSecretsManager",
                            effect=aws_iam.Effect.ALLOW,
                            actions=["secretsmanager:GetSecretValue"],
                            resources=[CERTIFICATE_ARN]
                        )
                    ]
                )
            )
        )
