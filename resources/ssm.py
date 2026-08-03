from aws_cdk import aws_ssm
from constructs import Construct

from resources import configs


class SharkordSsm(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope=scope, id=id)
        self.parameter: aws_ssm.StringParameter = aws_ssm.StringParameter(
            scope=self,
            id="SharkordServerHostnameParameter",
            parameter_name=configs.Ssm.SERVER_HOSTNAME_PARAM.value,
            string_value="chat.zolabs.io",
            description="Public hostname Sharkord's Apache vhost is served on"
        )
