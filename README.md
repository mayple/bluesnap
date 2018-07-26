# bluesnap

[![PyPI version fury.io](https://badge.fury.io/py/bluesnap.svg)](https://pypi.python.org/pypi/bluesnap/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/bluesnap.svg)](https://pypi.python.org/pypi/bluesnap/)
[![Build Status](https://travis-ci.com/selectom/bluesnap.svg?branch=master)](https://travis-ci.com/selectom/bluesnap)

> A Python 3 module to interact with the Bluesnap API.

Developed in [Selectom](https://www.selectom.com).

## Install

```sh
pip install bluesnap
```

## Example

```python
import logging
import math
import random

import bluesnap
from bluesnap.resources import PaymentFieldsTokenResource, VaultedShopperResource, TransactionResource, \
    TransactionMetadata

logging.basicConfig()

client = \
    bluesnap.client.configure(
        # Or use "live"
        env="sandbox",
        # Get credentials from BlueSnap
        username="...",
        password="...",
        # Default store Id
        default_store_id="...",
        # Seller id
        seller_id='...',
        # Default currency
        default_currency="usd",
        # Locale
        locale='en',
        # Logger
        logger=logging.root
    )

print(client.endpoint_url)
print(bluesnap.client.default_user_agent())
print(client.currency)
print(client.store_id)

paymentFieldsTokenResource = PaymentFieldsTokenResource()
vaultedShopperResource = VaultedShopperResource()
transactionResource = TransactionResource()

# Get a Hosted Payment Fields token
tokenId = paymentFieldsTokenResource.create()
print(tokenId)

# Use it in your frontend: https://developers.bluesnap.com/docs/build-a-form

# Create a vaulted shopper
vaultedShopper = vaultedShopperResource.createFromPaymentFieldsToken(
    firstName="FirstName",
    lastName="LastName",
    paymentFieldsTokenId=tokenId
)
print(vaultedShopper)

# Retrieve again, if you want
existingVaultedShopper = vaultedShopperResource.retrieve('22823473')
print(existingVaultedShopper)

# Validate the vaulted shopper
validatingTransaction = transactionResource.auth(
    vaultedShopperId=22823473,
    amount=0,
    currency='USD',
    softDescriptor='Selectom'
)
print(validatingTransaction)
vaultedShopperIsValid = validatingTransaction['processingInfo']['processingStatus'] == 'success'
print("vaultedShopperIsValid:", vaultedShopperIsValid)

# Create a transaction
amount = random.randint(100, 10000)
shippingAmount = math.ceil(float(amount) * 0.175)
stateTaxAmount = math.ceil(float(amount) * 0.08)
total = amount + shippingAmount + stateTaxAmount
amount = float(amount) / 100.0
shippingAmount = float(shippingAmount) / 100.0
stateTaxAmount = float(stateTaxAmount) / 100.0
total = float(total) / 100.0
newTransaction = transactionResource.authCapture(
    vaultedShopperId=22823473,
    amount=total,
    currency='USD',
    softDescriptor='Selectom',
    transactionMetadataObjectList=[
        TransactionMetadata(value=f'{amount}', key='amount', description='Amount'),
        TransactionMetadata(value=f'{shippingAmount}', key='shippingAmount', description='Shipping Amount'),
        TransactionMetadata(value=f'{stateTaxAmount}', key='stateTaxAmount', description='State Tax Amount')
    ]
)
print(newTransaction)

# Retrieve a transaction
newlyCreatedTransaction = transactionResource.get(newTransaction['transactionId'])
print(newlyCreatedTransaction)

# Is it valid?
newlyCreatedTransactionIsValid = (newlyCreatedTransactionTransaction['processing-info']['processing-status'] == 'SUCCESS')
print(newlyCreatedTransactionIsValid)
```

## Related projects

You might also be interested in these projects:

* [python-bluesnap](https://github.com/justyoyo/bluesnap-python): This project was forked from it, but adds Python 3 support and includes new support for Standard JSON API resources.

## Contributing

Pull requests and stars are always welcome. For bugs and feature requests, [please create an issue](https://github.com/selectom/bluesnap/issues/new).

Install with:
```sh
$ virtualenv .venv -p python3
$ . .venv/bin/activate
(.venv) $ pip install -r requirements.txt
```
and run the tests with:
```sh
(.venv) $ pip install -r tests/requirements.txt
(.venv) $ nosetests tests/
```

## Author

**Alon Diamant (advance512)**

* [github/advance512](https://github.com/advance512)
* [Homepage](http://www.alondiamant.com)


