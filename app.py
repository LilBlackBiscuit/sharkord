import os

import aws_cdk

from resources.component import SharkordStack


REGION: str = os.getenv(key="AWS_REGION", default="us-east-1")


app: aws_cdk.App = aws_cdk.App()
sharkord_stack: SharkordStack = SharkordStack(scope=app, id="SharkordApp")
aws_cdk.Tags.of(scope=sharkord_stack).add(key="application", value="sharkord")
app.synth(force=True, validate_on_synthesis=True)
