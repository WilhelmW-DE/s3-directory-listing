# s3-directory-listing
Amazon S3 directory listing with Lambda@Edge

## Prerequisites

* S3 Bucket Website Hosting
* CloudFront Distribution for the S3-Bucket

## Installing

Create a Python Lambda function in North Virginia, choose to *Create a new role from AWS policy templates* with the name "origin-response-role" and add the policy template *Basic Lambda@Edge permissions (for CloudFront trigger)*.

Paste the code from **origin-response.py** and change the bucket variable in the beginning to the S3 bucket of your choice (it doesn't even need to be the bucket you are hosting).

Save and *Deploy to Lambda@Edge* in the *Actions* menu as a *origin response* CloudFront event.

Create a new IAM policy "origin-response-s3-policy" and insert the content of the origin-response-s3-policy.json file.
Add the policy to your "origin-response-role".

## Usage

Make sure you are using the trailing slash in your directory url.
