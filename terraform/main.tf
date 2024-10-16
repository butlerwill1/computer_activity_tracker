provider "aws" {
    region = "eu-west-2"
}

resource "aws_kinesis_stream" "t_computer_activity_stream" {
    name            = "computer_activity_stream_new"
    shard_count     = 1
}

resource "aws_s3_bucket" "t_computer_activity_s3" {
    bucket = "computer-activity-new"
}

resource "aws_iam_role" "t_firehose_service_role" {
    name = "firehose_service_role"

    assume_role_policy = jsonencode({
        "Version" : "2012-10-17",
        "Statement" : [{
            "Effect" : "Allow",
            "Principal" : {
                "Service" : "firehose.amazonaws.com"
            },
            "Action" : "sts:AssumeRole"
        }]
    })
}

resource "aws_iam_policy" "t_firehose_policy" {
    name = "firehose_access_policy"

    policy = jsonencode({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "${aws_s3_bucket.t_computer_activity_s3.arn}",
                "${aws_s3_bucket.t_computer_activity_s3.arn}/*"
            ]
        }]
    })

}

resource "aws_iam_policy_attachment" "t_firehose_policy_attachment" {
    name = "firehose_policy_attachment"
    roles = [aws_iam_role.t_firehose_service_role.name]
    policy_arn = aws_iam_policy.t_firehose_policy.arn
}

resource "aws_kinesis_firehose_delivery_stream" "t_kinesis_to_firehose" {
    name          =  "kinesis_to_firehose_new"
    destination   =  "extended_s3"

    extended_s3_configuration {
        role_arn            =  aws_iam_role.t_firehose_service_role.arn
        bucket_arn          =  aws_s3_bucket.t_computer_activity_s3.arn
        buffering_size      =  64
        buffering_interval  =  300

        dynamic_partitioning_configuration {
            enabled = "true"
        }

        prefix              =  "activity_type=!{partitionKeyFromQuery:activity_type}/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/hour=!{timestamp:HH}/"
        error_output_prefix =  "error-output/!{firehose:error-output-type}/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/hour=!{timestamp:HH}/"

        processing_configuration {
            enabled = "true"

            processors {

                type = "MetadataExtraction"
                parameters {
                    parameter_name  = "JsonParsingEngine"
                    parameter_value = "JQ-1.6"
                }
                parameters {
                    parameter_name  = "MetadataExtractionQuery"
                    parameter_value = "{activity_type:.activity_type}"
                }
            
            }

        }

    }

}

