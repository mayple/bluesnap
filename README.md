# bluesnap

[![PyPI version](https://badge.fury.io/py/bluesnap.svg)](https://badge.fury.io/py/bluesnap)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/bluesnap.svg)](https://pypi.python.org/pypi/bluesnap/)
[![Build Status](https://travis-ci.com/mayple/bluesnap.svg?branch=master)](https://travis-ci.com/mayple/bluesnap)

> A Python 3 module to interact with the Bluesnap API.

Developed in [Mayple](https://www.mayple.com).

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
    TransactionMetadata, VaultedShopperInfo, ShippingContactInfo, TransactionFraudInfo, BillingContactInfo, Level3Data, \
    Level3DataItem

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

# Create a token
# --------------

tokenId = paymentFieldsTokenResource.create()
print(tokenId)

# Use it in your frontend: https://developers.bluesnap.com/docs/build-a-form
input('Press enter to continue...')

# Create vaulted shopper
# ----------------------

billingContactInfo = BillingContactInfo(
    firstName="Credit Card",
    lastName="Owner",
    personalIdentificationNumber="1234123123",
    address1="5 Somewhere",
    city="Tel Aviv",
    country="il",
    zip_="123456"
)

shippingContactInfo = ShippingContactInfo(
    firstName="Package",
    lastName="Receiver",
    address1="18 Otherplace",
    city="Ramat Gan",
    country="il",
    zip_="123123"
)

transactionFraudInfo = TransactionFraudInfo(
    # Have a look here: https://developers.bluesnap.com/docs/fraud-prevention#section-device-data-checks
    fraudSessionId="12345678123456781234567812345678",
    shippingContactInfo=shippingContactInfo,
)

vaultedShopperInfo = VaultedShopperInfo(
    firstName="Customer Name",
    lastName="for Invoicing",
    companyName="Company LTD",
    personalIdentificationNumber="123123123",
    shopperCurrency="USD",
    softDescriptor="AppearInCreditCard",
    descriptorPhoneNumber="+972-1231-123123",
    merchantShopperId="12345",
    address="More Place 4",
    city="Givatayim",
    country="IL",
    zip_="123123",
    email="customer@email.com",
    phone="+972-123123123",
    shippingContactInfo=shippingContactInfo,
    transactionFraudInfo=transactionFraudInfo,
)

vaultedShopper = vaultedShopperResource.createFromPaymentFieldsToken(
    vaultedShopperInfo=vaultedShopperInfo,
    paymentFieldsTokenId=tokenId,
    billingContactInfo=billingContactInfo
)
print(vaultedShopper)
vaultedShopperId = vaultedShopper['vaultedShopperId']

# Retrieve again, if you want
existingVaultedShopper = vaultedShopperResource.retrieve('22823473')
print(existingVaultedShopper)

# Validate credit card set to shopper
# -----------------------------------

# Validate the vaulted shopper
validatingTransaction = transactionResource.auth(
    vaultedShopperId=vaultedShopperId,
    amount='0',
    currency='USD',
)
print(validatingTransaction)
vaultedShopperIsValid = validatingTransaction['processingInfo']['processingStatus'] == 'success'
print("vaultedShopperIsValid:", vaultedShopperIsValid)

# Create a transaction
# --------------------

amount = random.randint(100, 10000)
shippingRate = 0.08
stateTaxRate = 0.17
shippingAmount = math.ceil(float(amount) * shippingRate)
stateTaxAmount = math.ceil(float(amount) * stateTaxRate)
total = amount + shippingAmount + stateTaxAmount

amount = float(amount) / 100.0
shippingAmount = float(shippingAmount) / 100.0
stateTaxAmount = float(stateTaxAmount) / 100.0
total = float(total) / 100.0

level3Data = Level3Data(
    customerReferenceNumber="12345234234",
    salesTaxAmount=str(stateTaxRate),
    freightAmount=str(shippingAmount),
    dutyAmount="0",
    level3DataItems=[
        Level3DataItem(
            description="Item description",
            lineItemTotal=str(amount),
            commodityCode="96345345",
            grossNetIndicator="N",
            productCode="123123123123",
            itemQuantity="1",
            unitCost="1",
            unitOfMeasure="USD"
        )
    ]
)

newTransaction = transactionResource.authCapture(
    vaultedShopperId=22823473,
    amount=total,
    currency='USD',
    level3Data=level3Data,
    transactionMetadataObjectList=[
        TransactionMetadata(value=f'{amount}', key='amount', description='Amount'),
        TransactionMetadata(value=f'{shippingAmount}', key='shippingAmount', description='Shipping Amount'),
        TransactionMetadata(value=f'{stateTaxAmount}', key='stateTaxAmount', description='State Tax Amount')
    ]
)
print(newTransaction)

# Retrieve a transaction
newlyCreatedTransaction = transactionResource.retrieve(newTransaction['transactionId'])
print(newlyCreatedTransaction)

# Is it valid?
newlyCreatedTransactionIsValid = (newlyCreatedTransactionTransaction['processing-info']['processing-status'] == 'SUCCESS')
print(newlyCreatedTransactionIsValid)
```

## Related projects

You might also be interested in these projects:

* [python-bluesnap](https://github.com/justyoyo/bluesnap-python): This project was forked from it, but adds Python 3 support and includes new support for Standard JSON API resources.

## Contributing

Pull requests and stars are always welcome. For bugs and feature requests, [please create an issue](https://github.com/mayple/bluesnap/issues/new).

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


