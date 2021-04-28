import os
os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(os.getcwd(), 'cacert.pem')

import certifi

