from typing import Any

import aws_cdk
import constructs

from iam import SharkordIam
from ec2 import SharkordServer


class SharkordStack(aws_cdk.Stack):
    def __init__(self, scope: constructs.Construct, id: str, **kwargs: Any):
        super().__init__(scope=scope, id=id, **kwargs)
        # TODO: add stack resources here
        sharkord_iam: SharkordIam = SharkordIam(scope=scope, id=id)
        _: SharkordServer = SharkordServer(scope=scope, id=id, role=sharkord_iam.server_role)
