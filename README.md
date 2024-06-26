# copy-gcs-to-s3
Copy files from GCS to S3 based on GCS events

## usage
gcloud --project [productdelivery_project_name] \
functions deploy copy_to_s3 \
--runtime python39 \
--trigger-resource [productdelivery_bucket_name] \
--trigger-event google.storage.object.finalize \
--entry-point copy_to_s3 \
--region us-west1 \
--set-secrets AWS_ACCESS_KEY_ID=s3-copy-cf-aws-access-key-id:latest, \
              AWS_SECRET_ACCESS_KEY=s3-copy-cf-aws-secret-access-key:latest, \
              S3_BUCKET_NAME=s3-copy-cf-s3-bucket-name:latest \
--set-env-vars AWS_REGION=us-west-2
