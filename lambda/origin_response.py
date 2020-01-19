import json
from urllib.parse import parse_qs

def handler(event, context):
    print("DEBUG: Printing the entire event:")
    print(event)
    print("DEBUG: Adding security headers to CloudFront response")
    script_src = "https://" + event['Records'][0]['cf']['config']['distributionDomainName']
    connect_src = "https://api.github.com"

    csp = "default-src 'none'; img-src 'self'; script-src 'self' {}; style-src 'self'; object-src 'none'; connect-src {}".format(script_src, connect_src)

    response = event['Records'][0]['cf']['response']
    headers = response["headers"]
    headers['referrer-policy'] = [{'key': 'Referrer-Policy', 'value': 'same-origin'}]
    headers['strict-transport-security'] = [{'key': 'Strict-Transport-Security', 'value': 'max-age= 63072000; includeSubdomains; preload'}]
    headers['content-security-policy'] = [{'key': 'Content-Security-Policy', 'value': csp}]
    headers['x-content-type-options'] = [{'key': 'X-Content-Type-Options', 'value': 'nosniff'}]
    headers['x-frame-options'] = [{'key': 'X-Frame-Options', 'value': 'DENY'}]
    headers['x-xss-protection'] = [{'key': 'X-XSS-Protection', 'value': '1; mode=block'}]

    print("DEBUG: distributionDomainName: {}".format(event['Records'][0]['cf']['config']['distributionDomainName']))

    print("DEBUG: Returning response: {}".format(response))
    return response
