locals {
  s3_origin_id = "s3_origin"
}

resource "aws_s3_bucket" "s3_origin_bucket" {
  acl = "public-read"
  tags = {
    Use         = "frontend"
    Type        = "static website"
    Environment = "dev"
    Name        = "lambda_edge_cloudfront_terraform"
  }
  versioning {
    enabled = true
  }
  website {
    index_document = "index.html"
  }
  force_destroy = true
}

resource "aws_cloudfront_distribution" "s3_distribution" {
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = local.s3_origin_id

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"

    lambda_function_association {
      event_type   = "origin-response"
      lambda_arn   = aws_lambda_function.origin_response_lambda.qualified_arn
      include_body = false
    }
    lambda_function_association {
      event_type   = "viewer-request"
      lambda_arn   = aws_lambda_function.viewer_request_lambda.qualified_arn
      include_body = false
    }
  }

  enabled = true

  origin {
    # S3 origin
    domain_name = aws_s3_bucket.s3_origin_bucket.website_endpoint
    origin_id   = local.s3_origin_id
    custom_origin_config {
      origin_protocol_policy = "http-only"
      http_port              = 80
      https_port             = 443
      origin_ssl_protocols   = ["TLSv1.2", "TLSv1.1", "TLSv1"]
    }
  }

  tags = {
    Environment = "dev"
    Name        = "lambda_edge_cloudfront_terraform"
  }

  price_class = "PriceClass_All"

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["US"]
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

output "s3_bucket" {
  value = aws_s3_bucket.s3_origin_bucket.bucket
}

output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.s3_distribution.id
}
