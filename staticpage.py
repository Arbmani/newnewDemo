import json
import pulumi
from pulumi import ResourceOptions
from pulumi_aws import s3
from typing import Optional, TypedDict, Union, cast

class StaticPageArgs(TypedDict):
    index_content: pulumi.Input[str]

class StaticPage(pulumi.ComponentResource):
    endpoint: pulumi.Output[str]

    # NOTE: 'args' with a type annotation is present to satisfy component_provider_host.
    # We also accept index_content=... directly for convenience.
    def __init__(
        self,
        name: str,
        args: Optional[StaticPageArgs] = None,
        opts: Optional[ResourceOptions] = None,
        *,
        index_content: Optional[pulumi.Input[str]] = None,
    ):
        super().__init__("static-page-component:index:StaticPage", name, None, opts)

        if args is None:
            if index_content is None:
                raise TypeError("index_content is required")
            args = cast(StaticPageArgs, {"index_content": index_content})

        bucket = s3.Bucket(name)

        website = s3.BucketWebsiteConfiguration(
            f"{name}-website",
            bucket=bucket.bucket,
            index_document={"suffix": "index.html"},
        )

        s3.BucketObject(
            f"{name}-index",
            bucket=bucket.bucket,
            key="index.html",
            content=args["index_content"],
            content_type="text/html",
        )

        # Allow a public *policy* to take effect (common defaults block this)
        s3.BucketPublicAccessBlock(
            f"{name}-pab",
            bucket=bucket.id,
            block_public_policy=False,
            restrict_public_buckets=False,
        )

        s3.BucketPolicy(
            f"{name}-policy",
            bucket=bucket.bucket,
            policy=bucket.bucket.apply(
                lambda b: json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": "*",
                                "Action": "s3:GetObject",
                                "Resource": f"arn:aws:s3:::{b}/*",
                            }
                        ],
                    }
                )
            ),
        )

        self.endpoint = website.website_endpoint
        self.register_outputs({"endpoint": self.endpoint})
