from urllib.parse import parse_qs, urlencode
from re import search

def handler(event, context):
    print(event)

    request = event['Records'][0]['cf']['request']

    if request.get('uri'):
        if '/index.html' in request.get('uri'):
            if request.get('querystring'):
                print("DEBUG: found querystring: {}".format(request.get('querystring')))

                print("DEBUG: distributionDomainName: {}".format(event['Records'][0]['cf']['config']['distributionDomainName']))
                redirectURL = 'https://' + event['Records'][0]['cf']['config']['distributionDomainName'] + '/other.html?' + request.get('querystring')
                print("DEBUG: redirectURL: {}".format(redirectURL))

                response = {
                    'status': '302',
                    'statusDescription': 'Found',
                    'headers': {
                        'location': [{
                            'key': 'Location',
                            'value': redirectURL
                        }],
                        'cache-control': [{
                            'key': 'Cache-Control',
                            'value': 'max-age=300'
                        }],
                        'content-security-policy': [{
                            'key': 'Content-Security-Policy',
                            'value': "unsafe-inline"
                        }]
                    }
                }

                print("DEBUG: Returning response: {}".format(response))
                return response
    return request
