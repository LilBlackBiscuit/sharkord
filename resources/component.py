from typing import Any

import aws_cdk
import constructs

from resources.iam import SharkordIam
from resources.ec2 import SharkordServer


class SharkordStack(aws_cdk.Stack):
    def __init__(self, scope: constructs.Construct, id: str, **kwargs: Any):
        super().__init__(scope=scope, id=id, **kwargs)
        # TODO: add stack resources here
        sharkord_iam: SharkordIam = SharkordIam(scope=scope, id="SharkordIam")
        _: SharkordServer = SharkordServer(scope=scope, id="SharkordServer", role=sharkord_iam.server_role)
