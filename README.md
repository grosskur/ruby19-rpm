# Ruby 1.9.3 RPM from Amazon Linux

These [RPM][rpm] sources are for the `ruby19` package on [Amazon Linux
AMI][amazon-linux-ami] 2013.09:
    
    ruby19-1.9.3.448-31.53.amzn1.src.rpm

It was obtained by the command:

    get_reference_source -p ruby19

This `ruby19` package installs alongside the normal `ruby` package and
the default Ruby can be managed with the `alternatives` program:

    alternatives --config ruby

[amazon-linux-ami]: http://aws.amazon.com/amazon-linux-ami/
[rpm]: http://www.rpm.org/
