import os

import aws_cdk

from resources.component import SharkordStack


ACCOUNT: str = os.getenv(key="AWS_ACCOUNT_ID")
REGION: str = os.getenv(key="AWS_REGION")


app: aws_cdk.App = aws_cdk.App()
sharkord_stack: SharkordStack = SharkordStack(
    scope=app,
    id="SharkordStack",
    env=aws_cdk.Environment(account=ACCOUNT, region=REGION)
)
aws_cdk.Tags.of(scope=sharkord_stack).add(key="application", value="sharkord")
app.synth(force=True, validate_on_synthesis=True)
