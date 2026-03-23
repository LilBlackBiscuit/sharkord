from aws_cdk import aws_iam
from constructs import Construct


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
