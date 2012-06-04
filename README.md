# pdns-dynamodb

PowerDNS backend using DynamoDB

## Schema

* name - string - hash key
* type - string - range key
* ttl - number
* values - set of strings

**Note** that in order to simplify the DynamoDB schema MX and SRV
records must store the priority field at the beginning of the content,
separated by a TAB.

## Permissions

It is recommended you create a special IAM users that only has
permissions for querying DNS records to be used by this backend. You
can use the following IAM policy template (replacing REGION, ACCOUNTID
and TABLE with the correct values).

```
{
  "Statement": [
    {
      "Action": [
        "dynamodb:DescribeTable",
        "dynamodb:GetItem",
        "dynamodb:Query"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:dynamodb:REGION:ACCOUNTID:table/TABLE"
      ]
    }
  ]
}
```

## Usage

### Secret key storage

Place the secret key of the IAM account into a file that is only
readable by the `pdns` user.

### Executable script

Create an executable script that looks like

```
#!/bin/sh

pdns-dynamodb -t TABLE -r REGION -I ACCESS_KEY -K /path/to/secret.key
```

Replacing TABLE, REGION and ACCESS_KEY with the appropriate values and
the path to secret key from the previous step.

### PowerDNS backend configuration

Configure pdns.conf as follows:

```
launch=pipe
pipe-command=/path/to/executable/script
```

using the path to the executable script you created above.
