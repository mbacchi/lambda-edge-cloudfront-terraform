# Lambda@Edge On CloudFront

This project demonstrates how to use Lambda@Edge and a CloudFront distribution
to manipulate a request at the edge. We pass a querystring from one HTML page to
a second HTML page using a redirect initiated via the Lambda@Edge viewer request
function.

## Pre-requisites

* Terraform 0.12.x
* An AWS account

## Deploying

**NOTE**: You must use the AWS Northern Virginia region (`us-east-1`) because in
order to replicate Lambda@Edge functions to all regions, AWS requires that you
are deploying your functions into this region only. This requirement may be
relaxed in the future but this is the reality at the moment.

### Prepare to run terraform

These steps include:

* Install Terraform 0.12.x
* Clone this repository
* Change into the `terraform/` directory
* Run `terraform init`
* Exporting environment variable for your AWS_PROFILE and AWS_REGION. This looks
  something like:

    `export AWS_PROFILE=blah && export AWS_REGION=us-east-1`

  Another option is to use [aws-vault](https://github.com/99designs/aws-vault)
  to manage AWS credentials. I personally use aws-vault, as you will see in the
  commands used below.

### Deploy

1. Run the following commands to deploy:

```
aws-vault exec profile_name -- terraform plan -out=devplan.$(date +%F.%H.%M.%S).out
```

This will create a Terraform plan file, which you can then apply with the command:

```
aws-vault exec profile_name -- terraform apply devplan.2020-01-19.08.44.07.out
```

**NOTE**: Terraform apply` it can take up to 20 or 30 minutes to replicate the
Lambda@Edge function across all the (supported) AWS regions. You may not want to
replicate and that would be fine, but doesn't fit the model of using all AWS
regions to run Lambda at their edge locations. If you don't create the Lambda
function in the `us-east-1` (N. Virginia) region, as far as I understand (at
this time) it will not be replicated to all AWS regions.

The distribution name will be shown in the output at the end, something such as:

```
Outputs:

cloudfront_distribution_id = E2U0H2YCG3AYFU
s3_bucket = terraform-20200118165546224400000003
```

Then you will need to determine the distribution domain name. This can be shown
with the command, using the ID shown in the above output:

```
aws-vault exec --no-session experiments_user1 -- aws cloudfront get-distribution --id E2U0H2YCG3AYFU
```

Look in the JSON output for the Distribution.DomainName, it appears like:

```
"DomainName": "d11e7fgi9rskgz.cloudfront.net",
```

2. After the cloudfront distribution is deployed successfully, you need to place
   the HTML and script resources in the S3 bucket. You need to know the S3
   bucket previous step to do this. Run the command:

```
aws-vault exec profile_name -- aws s3 cp index.html s3://terraform-20200118165546224400000003/ --acl public-read
aws-vault exec profile_name -- aws s3 cp other.html s3://terraform-20200118165546224400000003/ --acl public-read
aws-vault exec profile_name -- aws s3 cp script.js s3://terraform-20200118165546224400000003/ --acl public-read
```

### Re-deploying

Remember from the above NOTE, when running `terraform apply` it can take up to
20 or 30 minutes to replicate the Lambda@Edge function across all the
(supported) AWS regions. You may not want to replicate and that would be fine,
but doesn't fit the model of using all AWS regions to run Lambda at their edge
locations. If you don't create the Lambda function in the `us-east-1` (N.
Virginia) region, as far as I understand (at this time) it will not be
replicated to all AWS regions.

## Viewing the site

Browse to your index page using the CloudFront DomainName you obtained above. In
our example that URL is(this URL is no longer valid!!! I have since removed the
CloudFront distribution.):

https://d11e7fgi9rskgz.cloudfront.net/index.html

Type a GitHub user name in the input box, and hit the Submit button. You will be
redirected to the other.html page, and the querystring will be used to query the
GitHub API, returning that user's information in the response section of the web
page.

### Troubleshooting

If you don't see the output you expect, i.e. the GitHub user information, there
are a couple ways to find problems.

1. Open the Developer Console in Chrome (or whatever browser you are using)
2. Go to AWS CloudWatch Logs, open the Log Group `/aws/lambda/us-east-1.viewer_request_lambda` or `/aws/lambda/us-east-1.origin_response_lambda`, and view the recent logs, to see if there are server side errors.

## Tearing down the infrastructure

Deleting the replicated Lambda functions takes time, just like deploying the
Lambda to all replicated regions does. In order to perform this deletion in a
timely fashion, you first need to remove the function association in the
CloudFront distribution via the AWS console. Browse to CloudFront in the AWS
console. Then click on your distribution ID from above. Go to the "Behaviors"
tab and select the "Origin or Origin Group" `s3_origin`, then choose "Edit".
Finally at the bottom of the "Edit Behavior" page, click on the X for both the
"Viewer Request" and "Origin Response" CloudFront Events. Once these are removed
select "Yes, Edit", which is apparently the "Save" button in CloudFront.

Now, wait 20-30 minutes before running `terraform destroy` to remove the
infrastucture via Terraform.

This wait time is required because Terraform will attempt to remove the Lambda
function before the CloudFront distribution, and this won't work because the
function association is still defined between the CloudFront distribution and
the Lambda function. We must remove this association first before attempting to
tear down all the infrastructure via Terraform.

If you don't do this step, you would likely see the following error message:

```
Error: Error deleting Lambda Function: InvalidParameterValueException: Lambda was unable to delete arn:aws:lambda:us-east-1:592431548397:function:origin_response_lambda:5 because it is a replicated function. Please see our documentation for Deleting Lambda@Edge Functions and Replicas.
	status code: 400, request id: e47befaa-79f8-42c3-84f8-774df27f31d4
```

Either wait 20-30 minutes to re-run `terraform destroy` or remove the
association with the CloudFront distribution as described above.

Enjoy!