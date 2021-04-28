import re
from abc import abstractmethod
from typing import List, Optional
from urllib.parse import urlparse

import requests
from lxml import etree

from . import models
from .client import default as default_client


class Resource(object):
    def __init__(self, client=None):
        self.client = client or default_client()
        """:type : .client.Client"""

    def request(self, method, path, data=None):
        response, body = self.client.request(method, path, data)
        return response, body


# ------------------
# XML API
# ------------------

class ShopperResource(Resource):
    shoppers_path = '/services/2/shoppers'
    shopper_path = shoppers_path + '/{shopper_id}'
    shopper_id_path_pattern = re.compile(r'{}/(\d+)'.format(shoppers_path))  # /services/2/shoppers/(\d+)

    def find_by_shopper_id(self, shopper_id):
        """
        :param shopper_id: BlueSnap shopper id
        :return: shopper dictionary
        """
        response, body = self.request('GET', self.shopper_path.format(shopper_id=shopper_id))
        return body['shopper']

    def find_by_seller_shopper_id(self, seller_shopper_id):
        """
        :param seller_shopper_id: Seller-specific shopper id
        :return: shopper dictionary
        """
        return self.find_by_shopper_id('{seller_shopper_id},{seller_id}'.format(
            seller_shopper_id=seller_shopper_id,
            seller_id=self.client.seller_id))

    def _create_shopper_element(self, contact_info, credit_card=None,
                                seller_shopper_id=None, client_ip=None):
        # noinspection PyPep8Naming
        E = self.client.E

        credit_cards_info = []
        if credit_card is not None:
            credit_cards_info.append(getattr(E, 'credit-card-info')(
                contact_info.to_xml('billing'),
                credit_card.to_xml()
            ))

        shopper_info = []
        if seller_shopper_id is not None:
            shopper_info.append(getattr(E, 'seller-shopper-id')(seller_shopper_id))

        return E.shopper(
            getattr(E, 'shopper-info')(
                getattr(E, 'store-id')(self.client.store_id),
                getattr(E, 'shopper-currency')(self.client.currency),
                E.locale(self.client.locale),
                contact_info.to_xml('shopper'),
                getattr(E, 'payment-info')(
                    getattr(E, 'credit-cards-info')(*credit_cards_info)
                ),
                *shopper_info
            ),
            models.WebInfo(ip=client_ip).to_xml()
        )

    def create(self, contact_info, credit_card=None, seller_shopper_id=None,
               client_ip=None):
        """
        Creates a new shopper
        :type contact_info: models.ContactInfo
        :type credit_card: models.AbstractCreditCard
        :param seller_shopper_id: Seller-specific shopper id
        :param client_ip:
        :return: Returns the newly created BlueSnap shopper id
        """
        shopper_element = self._create_shopper_element(
            contact_info, credit_card, seller_shopper_id, client_ip=client_ip)
        data = etree.tostring(shopper_element)

        response, body = self.request('POST', self.shoppers_path, data=data)

        # Extract shopper id from location header
        new_shopper_url = urlparse(response.headers['location'])
        shopper_id = self.shopper_id_path_pattern.match(new_shopper_url.path).group(1)

        return shopper_id

    def update(self, shopper_id, contact_info, credit_card=None, client_ip=None):
        """
        Updates an existing shopper
        :param shopper_id: BlueSnap shopper id
        :type contact_info: models.ContactInfo
        :type credit_card: models.AbstractCreditCard
        :param client_ip:
        :rtype: bool
        """
        shopper_element = self._create_shopper_element(
            contact_info, credit_card, client_ip=client_ip)
        data = etree.tostring(shopper_element)

        response, _ = self.request('PUT', self.shopper_path.format(shopper_id=shopper_id), data=data)
        return response.status_code == requests.codes.no_content


class OrderResource(Resource):
    path = '/services/2/orders'

    def create(self, shopper_id, sku_id, amount_in_pence, credit_card=None,
               description=None, client_ip=None):
        """
        :type shopper_id: int or str
        :type sku_id: int or str
        :type amount_in_pence: int
        :type credit_card: models.CreditCardSelection
        :param description: Order description
        :param client_ip:
        :return:
        """
        # noinspection PyPep8Naming
        E = self.client.E

        amount = '{:.2f}'.format(amount_in_pence / 100.0)

        order = []
        if description is not None:
            order.append(getattr(E, 'soft-descriptor')(description))

        ordering_shopper = []
        if credit_card is not None:
            ordering_shopper.append(credit_card.to_xml())

        order_element = E.order(
            getattr(E, 'ordering-shopper')(
                getattr(E, 'shopper-id')(str(shopper_id)),
                models.WebInfo(ip=client_ip).to_xml(),
                *ordering_shopper
            ),
            E.cart(
                getattr(E, 'cart-item')(
                    E.sku(
                        getattr(E, 'sku-id')(str(sku_id)),
                        getattr(E, 'sku-charge-price')(
                            getattr(E, 'charge-type')('initial'),
                            E.amount(amount),
                            E.currency(self.client.currency)
                        )
                    ),
                    E.quantity('1'),
                ),
            ),
            getattr(E, 'expected-total-price')(
                E.amount(amount),
                E.currency(self.client.currency)
            ),
            *order
        )

        data = etree.tostring(order_element)
        response, body = self.request('POST', self.path, data=data)
        return body['order']


# ------------------
# JSON API
# ------------------

class PaymentFieldsTokenResource(Resource):
    """
    If you would like to build your custom checkout flow using the API, but keep your PCI compliance requirements
    limited to the minimal SAQ-A level, BlueSnap’s Hosted Payment Fields are the ideal solution.

    Hosted Payment Fields are iframes that replace sensitive credit card input fields in your checkout page.
    When the shopper submits the checkout form, BlueSnap binds this payment data to a token. You can then easily
    process payments or save shopper details by including the token in your BlueSnap API requests.

    https://developers.bluesnap.com/v8976-Tools/docs/hosted-payment-fields

    """
    path = '/services/2/payment-fields-tokens'

    def __init__(
            self,
    ):
        super(PaymentFieldsTokenResource, self).__init__()

    def create(
            self,
            shopperId: str = None
    ):
        """
        Create a Hosted Payment Fields token by sending a server-to-server POST request to BlueSnap
        :return:
        """

        if shopperId is not None:
            _url = '%s?shopperId=%s' % (self.path, shopperId)
        else:
            _url = self.path

        response, body = self.request('POST', _url)

        locationHeader = response.headers['Location']
        tokenId = locationHeader.split('/')[-1]
        return tokenId


class DictableObject:

    def __init__(self):
        pass

    @abstractmethod
    def toDict(self):
        raise NotImplementedError("Must implement this.")

    def _setToDictIfHasValue(self, resultDict: dict, key: str):
        """
        Set a value to a dict if it has a value
        :param resultDict:
        :param key:
        :return:
        """

        if hasattr(self, key) and getattr(self, key, None):
            resultDict[key] = getattr(self, key)

    def _setToDictIfHasValues(self, resultDict: dict, keys: list):
        for key in keys:
            self._setToDictIfHasValue(resultDict, key)


class ShippingContactInfo(DictableObject):

    def __init__(
            self,
            firstName: str,
            lastName: str,
            address1: str = None,
            address2: str = None,
            city: str = None,
            state: str = None,
            country: str = None,
            zip_: str = None,
    ):
        """
        Details of a Shipping Contact Info.

        More information here:
        https://developers.bluesnap.com/v8976-JSON/docs/shipping-contact-info

        :param firstName: Shopper's first name. Maximum 100 characters.
        :param lastName: Shopper's last name. Maximum 100 characters.
        :param address1: Shopper's address line 1. Maximum 100 characters.
        :param address2: Shopper's address line 2. Maximum 100 characters.
        :param city: Shopper's city. Between 2-42 characters.
        :param state: Based on https://developers.bluesnap.com/docs/state-and-province-codes
        :param country: Based on https://developers.bluesnap.com/docs/country-codes
        :param zip_: Shopper's ZIP code. Maximum 20 characters.
        """

        # Call base class init
        super(ShippingContactInfo, self).__init__()

        if not firstName or not lastName or not address1 or not city or not zip_ or not country:
            raise ValueError('firstName, lastName, address1, city, zip and country are required.')

        self.firstName = firstName
        self.lastName = lastName
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.country = country
        self.zip = zip_

    def toDict(self) -> dict:
        result = {
            "firstName": self.firstName,
            "lastName":  self.lastName,
            "address1":  self.address1,
            "city":      self.city,
            "zip":       self.zip,
            "country":   self.country,
        }

        self._setToDictIfHasValues(
            resultDict=result,
            keys=[
                "address2",
                "state",
            ]
        )

        return result


class CardHolderInfo(DictableObject):
    """
    A Vaulted Shopper Info object, containing some of the fields defined here:
    https://developers.bluesnap.com/v8976-JSON/docs/vaulted-shopper
    """

    def __init__(
            self,
            firstName: str,
            lastName: str,
            personalIdentificationNumber: str = None,
            merchantShopperId: str = None,
            address: str = None,
            address2: str = None,
            city: str = None,
            state: str = None,
            country: str = None,
            zip_: str = None,
            email: str = None,
            phone: str = None,
    ):
        """
        Details of a Card Holder.

        More information here:
        CardHolderInfo

        :param firstName: Shopper's first name. Maximum 100 characters.
        :param lastName: Shopper's last name. Maximum 100 characters.
        :param personalIdentificationNumber: The shopper's local personal identification number.
            These are the ID types per country:
            Argentina - DNI (length 7-11 chars)
            Brazil - CPF/CNPJ (length 11-14 chras)
            Chile - RUN (length 8-9 chars)
            Colombia - CC (length 6-10 chars)
            Mexico - CURP/RFC (length 10-18 chars)
        :param merchantShopperId: A merchant's ID for a specific shopper, up to 50 characters.
        :param address: Shopper's address line 1. Maximum 100 characters.
        :param address2: Shopper's address line 2. Maximum 100 characters.
        :param city: Shopper's city. Between 2-42 characters.
        :param state: Based on https://developers.bluesnap.com/docs/state-and-province-codes
        :param country: Based on https://developers.bluesnap.com/docs/country-codes
        :param zip_: Shopper's ZIP code. Maximum 20 characters.
        :param email: Shopper's email address. Between 3-100 characters.
        :param phone: Shopper's phone number. Between 2-36 characters.
        """

        # Call base class init
        super(CardHolderInfo, self).__init__()

        if not firstName or not lastName:
            raise ValueError('firstName and lastName are required.')

        self.firstName = firstName
        self.lastName = lastName
        self.personalIdentificationNumber = personalIdentificationNumber
        self.merchantShopperId = merchantShopperId
        self.address = address
        self.address2 = address2
        self.city = city
        self.state = state
        self.country = country
        self.zip = zip_
        self.email = email
        self.phone = phone

    def toDict(self) -> dict:
        result = {
            "firstName": self.firstName,
            "lastName":  self.lastName,
        }

        self._setToDictIfHasValues(
            resultDict=result,
            keys=[
                "personalIdentificationNumber",
                "merchantShopperId",
                "address",
                "address2",
                "city",
                "state",
                "country",
                "zip",
                "email",
                "phone",
            ]
        )

        return result


class BillingContactInfo(DictableObject):

    def __init__(
            self,
            firstName: str,
            lastName: str,
            personalIdentificationNumber: str = None,
            address1: str = None,
            address2: str = None,
            city: str = None,
            state: str = None,
            country: str = None,
            zip_: str = None,
    ):
        """
        Details of a Billing Contact Info.

        More information here:
        https://developers.bluesnap.com/v8976-JSON/docs/billing-contact-info

        :param firstName: Shopper's first name. Maximum 100 characters.
        :param lastName: Shopper's last name. Maximum 100 characters.
        :param personalIdentificationNumber: The shopper's local personal identification number.
            These are the ID types per country:
            Argentina - DNI (length 7-11 chars)
            Brazil - CPF/CNPJ (length 11-14 chras)
            Chile - RUN (length 8-9 chars)
            Colombia - CC (length 6-10 chars)
            Mexico - CURP/RFC (length 10-18 chars)
        :param address1: Shopper's address line 1. Maximum 100 characters.
        :param address2: Shopper's address line 2. Maximum 100 characters.
        :param city: Shopper's city. Between 2-42 characters.
        :param state: Based on https://developers.bluesnap.com/docs/state-and-province-codes
        :param country: Based on https://developers.bluesnap.com/docs/country-codes
        :param zip_: Shopper's ZIP code. Maximum 20 characters.
        """

        # Call base class init
        super(BillingContactInfo, self).__init__()

        if not firstName or not lastName or not address1 or not city or not zip_ or not country:
            raise ValueError('firstName, lastName, address1, city, zip and country '
                             'are required.')

        # In one of the countries that required a personal identification number?
        # https://developers.bluesnap.com/v8976-JSON/docs/billing-contact-info
        if country.lower() in {
            'ar',  # Argentina
            'br',  # Brazil
            'cl',  # Chile
            'co',  # Colombia
            'mx',  # Mexico
            'il',  # Israel
        }:
            if not personalIdentificationNumber:
                raise ValueError('personalIdentificationNumber is required for country %s.' % country)

        self.firstName = firstName
        self.lastName = lastName
        self.personalIdentificationNumber = personalIdentificationNumber
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.country = country
        self.zip = zip_

    def toDict(self) -> dict:
        result = {
            "firstName": self.firstName,
            "lastName":  self.lastName,
            "address1":  self.address1,
            "city":      self.city,
            "zip":       self.zip,
            "country":   self.country,
        }

        self._setToDictIfHasValues(
            resultDict=result,
            keys=[
                "address2",
                "state",
                "personalIdentificationNumber",
            ]
        )

        return result


class TransactionFraudInfo(DictableObject):

    def __init__(
            self,
            fraudSessionId: str,
            shopperIpAddress: str = None,
            company: str = None,
            shippingContactInfo: ShippingContactInfo = None,
            # TODO: enterpriseSiteId
            # TODO: enterpriseUdfs
    ):
        """
        Transaction Fraud Info class.

        More information here:
        https://developers.bluesnap.com/v8976-JSON/docs/transaction-fraud-info

        :param fraudSessionId: Unique ID of the shopper whose device fingerprint information was collected on
            the checkout page. The Fraud Session ID should contain up to 32 alpha-numeric characters only.
            https://developers.bluesnap.com/docs/fraud-prevention#section-device-data-checks
        :param shopperIpAddress: Shopper's IP address. Should be a valid IPv4 or IPv6 address.
        :param company: Shopper's company name. Maximum 100 characters.
        :param shippingContactInfo: ShippingContactInfo object
        """

        # Call base class init
        super(TransactionFraudInfo, self).__init__()

        if not fraudSessionId:
            raise ValueError('fraudSessionId is required.')

        self.fraudSessionId = fraudSessionId
        self.shopperIpAddress = shopperIpAddress
        self.company = company
        self.shippingContactInfo = shippingContactInfo

    def toDict(self) -> dict:
        result = {
            "fraudSessionId": self.fraudSessionId,
        }

        self._setToDictIfHasValues(
            resultDict=result,
            keys=[
                "shopperIpAddress",
                "company",
            ]
        )

        if self.shippingContactInfo:
            result["shippingContactInfo"] = self.shippingContactInfo.toDict()

        return result


class VaultedShopperInfo(DictableObject):
    """
    A Vaulted Shopper Info object, containing some of the fields defined here:
    https://developers.bluesnap.com/v8976-JSON/docs/vaulted-shopper
    """

    def __init__(
            self,
            firstName: str,
            lastName: str,
            companyName: str = None,
            personalIdentificationNumber: str = None,
            shopperCurrency: str = None,
            softDescriptor: str = None,
            descriptorPhoneNumber: str = None,
            merchantShopperId: str = None,
            address: str = None,
            address2: str = None,
            city: str = None,
            state: str = None,
            country: str = None,
            zip_: str = None,
            email: str = None,
            phone: str = None,
            shippingContactInfo: ShippingContactInfo = None,
            transactionFraudInfo: TransactionFraudInfo = None,
    ):
        """
        Details of a Vaulted Shopper.

        More information here:
        https://developers.bluesnap.com/v8976-JSON/docs/create-vaulted-shopper#section-request-content

        :param firstName: Shopper's first name. Maximum 100 characters.
        :param lastName: Shopper's last name. Maximum 100 characters.
        :param companyName: Shopper's company name. Maximum 100 characters.
        :param personalIdentificationNumber: The shopper's local personal identification number.
            These are the ID types per country:
            Argentina - DNI (length 7-11 chars)
            Brazil - CPF/CNPJ (length 11-14 chras)
            Chile - RUN (length 8-9 chars)
            Colombia - CC (length 6-10 chars)
            Mexico - CURP/RFC (length 10-18 chars)
        :param shopperCurrency: Shopper's currency. Based on https://developers.bluesnap.com/docs/currency-codes
        :param softDescriptor: Description that may appear on the shopper's bank statement when BlueSnap validates
            the card. Maximum 20 characters.
            More info here: https://developers.bluesnap.com/docs/statement-descriptor
        :param descriptorPhoneNumber: Merchant's support phone number that may appear on the shopper's bank statement
            when BlueSnap validates the card. Maximum 20 characters.
            More info here: https://developers.bluesnap.com/docs/statement-descriptor
        :param merchantShopperId: A merchant's ID for a specific shopper, up to 50 characters.
        :param address: Shopper's address line 1. Maximum 100 characters.
        :param address2: Shopper's address line 2. Maximum 100 characters.
        :param city: Shopper's city. Between 2-42 characters.
        :param state: Based on https://developers.bluesnap.com/docs/state-and-province-codes
        :param country: Based on https://developers.bluesnap.com/docs/country-codes
        :param zip_: Shopper's ZIP code. Maximum 20 characters.
        :param email: Shopper's email address. Between 3-100 characters.
        :param phone: Shopper's phone number. Between 2-36 characters.
        :param shippingContactInfo: ShippingContactInfo object
        :param transactionFraudInfo: TransactionFraudInfo
        # TODO: walletId
        """

        # Call base class init
        super(VaultedShopperInfo, self).__init__()

        if not firstName or not lastName:
            raise ValueError('firstName and lastName are required.')

        self.firstName = firstName
        self.lastName = lastName
        self.companyName = companyName
        self.personalIdentificationNumber = personalIdentificationNumber
        self.shopperCurrency = shopperCurrency
        self.softDescriptor = softDescriptor
        self.descriptorPhoneNumber = descriptorPhoneNumber
        self.merchantShopperId = merchantShopperId
        self.address = address
        self.address2 = address2
        self.city = city
        self.state = state
        self.country = country
        self.zip = zip_
        self.email = email
        self.phone = phone
        self.shippingContactInfo = shippingContactInfo
        self.transactionFraudInfo = transactionFraudInfo

    def toDict(self) -> dict:
        result = {
            "firstName": self.firstName,
            "lastName":  self.lastName,
        }

        self._setToDictIfHasValues(
            resultDict=result,
            keys=[
                "companyName",
                "personalIdentificationNumber",
                "shopperCurrency",
                "softDescriptor",
                "descriptorPhoneNumber",
                "merchantShopperId",
                "address",
                "address2",
                "city",
                "state",
                "country",
                "zip",
                "email",
                "phone",
                "fraudSessionId",
            ]
        )

        if self.shippingContactInfo:
            result["shippingContactInfo"] = self.shippingContactInfo.toDict()

        if self.transactionFraudInfo:
            result["transactionFraudInfo"] = self.transactionFraudInfo.toDict()

        return result


class Level3DataItem(DictableObject):
    """
    Contains Level 2/3 data properties for each item purchased
    https://developers.bluesnap.com/v8976-JSON/docs/level3dataitems

    While all level3DataItems properties are optional in the request, each data level (such as Level 2 and Level 3)
    has specific requirements. See the Level 2/3 Data guide for complete details.
    https://developers.bluesnap.com/docs/level-23-data
    """

    def __init__(
            self,
            lineItemTotal: str = None,
            commodityCode: str = None,
            description: str = None,
            discountAmount: str = None,
            discountIndicator: str = None,
            grossNetIndicator: str = None,
            productCode: str = None,
            itemQuantity: str = None,
            taxAmount: str = None,
            taxRate: str = None,
            taxType: str = None,
            unitCost: str = None,
            unitOfMeasure: str = None,
    ):
        """

        :param lineItemTotal: Total item amount.
        :param commodityCode: Commodity code used to classify item.
        :param description: Item description
        :param discountAmount: Discount amount applied to item
        :param discountIndicator: Indicates whether item amount is discounted. 'Y' or 'N'
        :param grossNetIndicator: Indicates whether tax is included in item amount. 'Y' or 'N'
        :param productCode: Product code for item
        :param itemQuantity: Item quantity purchased
        :param taxAmount: Tax amount for item
        :param taxRate: Tax rate applied to item
        :param taxType: Type of tax being applied
        :param unitCost: Unit cost
        :param unitOfMeasure: Unit of measure
        """

        # Call base class init
        super(Level3DataItem, self).__init__()

        self.lineItemTotal = lineItemTotal
        self.commodityCode = commodityCode
        self.description = description
        self.discountAmount = discountAmount
        self.discountIndicator = discountIndicator
        self.grossNetIndicator = grossNetIndicator
        self.productCode = productCode
        self.itemQuantity = itemQuantity
        self.taxAmount = taxAmount
        self.taxRate = taxRate
        self.taxType = taxType
        self.unitCost = unitCost
        self.unitOfMeasure = unitOfMeasure

    def toDict(self) -> dict:
        result = {
        }

        self._setToDictIfHasValues(
            resultDict=result,
            keys=[
                "lineItemTotal",
                "commodityCode",
                "description",
                "discountAmount",
                "discountIndicator",
                "grossNetIndicator",
                "productCode",
                "itemQuantity",
                "taxAmount",
                "taxRate",
                "taxType",
                "unitCost",
                "unitOfMeasure",
            ]
        )

        return result


class Level3Data(DictableObject):
    """
    Contains Level 2/3 data properties for the transaction

    While all level3Data properties are optional in the request, each data level (such as Level 2 and Level 3) has
    specific requirements. See the Level 2/3 Data guide for complete details.
    https://developers.bluesnap.com/docs/level-23-data
    """

    def __init__(
            self,
            customerReferenceNumber: str = None,
            salesTaxAmount: str = None,
            freightAmount: str = None,
            dutyAmount: str = None,
            destinationZipCode: str = None,
            destinationCountryCode: str = None,
            shipFromZipCode: str = None,
            discountAmount: str = None,
            taxAmount: str = None,
            taxRate: str = None,
            level3DataItems: list = (),
    ):

        # Call base class init
        super(Level3Data, self).__init__()

        self.customerReferenceNumber = customerReferenceNumber
        self.salesTaxAmount = salesTaxAmount
        self.freightAmount = freightAmount
        self.dutyAmount = dutyAmount
        self.destinationZipCode = destinationZipCode
        self.destinationCountryCode = destinationCountryCode
        self.shipFromZipCode = shipFromZipCode
        self.discountAmount = discountAmount
        self.taxAmount = taxAmount
        self.taxRate = taxRate
        self.level3DataItems = level3DataItems

    def toDict(self) -> dict:
        result = {
        }

        self._setToDictIfHasValues(
            resultDict=result,
            keys=[
                "customerReferenceNumber",
                "salesTaxAmount",
                "freightAmount",
                "dutyAmount",
                "destinationZipCode",
                "destinationCountryCode",
                "shipFromZipCode",
                "discountAmount",
                "taxAmount",
                "taxRate",
            ]
        )

        if self.level3DataItems:
            level3DataItems = []

            for dataItem in self.level3DataItems:
                level3DataItems.append(
                    dataItem.toDict()
                )
            result["level3DataItems"] = level3DataItems

        return result


class NetworkTransactionInfo(DictableObject):
    """
    Contains the network transaction information for this transaction
    https://developers.bluesnap.com/v8976-JSON/docs/network-transaction-info
    """

    def __init__(
            self,
            originalNetworkTransactionId: str = None,
    ):
        """

        :param originalNetworkTransactionId: If this transaction is linked to an a previous network transaction ID,
            that NTI is sent here.
        """

        # Call base class init
        super(NetworkTransactionInfo, self).__init__()

        self.originalNetworkTransactionId = originalNetworkTransactionId

    def toDict(self) -> dict:
        result = {
        }

        self._setToDictIfHasValues(
            resultDict=result,
            keys=[
                "originalNetworkTransactionId",
            ]
        )

        return result


class ThreeDSecure(DictableObject):
    """
    Contains 3D Secure details for this transaction
    https://developers.bluesnap.com/v8976-JSON/docs/threedsecure
    """

    def __init__(
            self,
            threeDSecureReferenceId: str = None,
    ):
        """

        :param threeDSecureReferenceId: 3-D Secure reference ID received from client
        """

        # Call base class init
        super(ThreeDSecure, self).__init__()

        self.threeDSecureReferenceId = threeDSecureReferenceId

    def toDict(self) -> dict:
        result = {
        }

        self._setToDictIfHasValues(
            resultDict=result,
            keys=[
                "threeDSecureReferenceId",
            ]
        )

        return result


class CreditCard(DictableObject):
    """
    Contains the details for a specific credit card, such as the card number and expiration date

    Required if sending card data or if vaulted shopper has multiple cards.
    https://developers.bluesnap.com/v8976-JSON/docs/credit-card
    """

    def __init__(
            self,
            cardLastFourDigits: str = None,
            cardType: str = None,
            expirationMonth: str = None,
            expirationYear: str = None,
    ):
        """

        :param cardLastFourDigits: use if sending a vaulted shopper ID and the shopper has multiple saved credit cards.
        """

        # Call base class init
        super(CreditCard, self).__init__()

        self.cardLastFourDigits = cardLastFourDigits
        self.cardType = cardType
        self.expirationMonth = expirationMonth
        self.expirationYear = expirationYear

    def toDict(self) -> dict:
        result = {
        }

        self._setToDictIfHasValues(
            resultDict=result,
            keys=[
                "cardLastFourDigits",
                "cardType",
                "expirationMonth",
                "expirationYear",
            ]
        )

        return result


class CreditCardInfo(DictableObject):
    """
    Contains credit card information for vaulted shoppers

    More info:
    https://developers.bluesnap.com/v8976-JSON/docs/payment-sources
    """

    def __init__(
            self,
            billingContactInfo: BillingContactInfo = None,
            creditCard: CreditCard = None,
            pfToken: str = None,
            status: str = None,
    ):
        """
        Used as part of the paymentSources array in calls related to Vaulted Shoppers.

        Note: If status is included in the request, specify the card to be deleted by including cardType and
        cardLastFourDigits within creditCard.

        :param billingContactInfo: Contains billing contact information
        :param creditCard: Contains the details for a specific credit card, such as the card number and expiration date
        :param pfToken: Required if using Hosted Payment Fields. Do not include creditCard parameter if
            using this token. Relevant only for Create Vaulted Shopper and Update Vaulted Shopper.
        :param status: Enter "D" to delete the card from the shopper
        """

        # Call base class init
        super(CreditCardInfo, self).__init__()

        if creditCard and pfToken:
            raise Exception("Do not include creditCard parameter if using the pfToken parameter.")

        if status == "D" and (not creditCard or not getattr(creditCard, 'cardLastFourDigits')):
            raise Exception("If the status parameter is set as D, specify the card to be deleted by including "
                            "cardType and cardLastFourDigits within creditCard.")

        self.billingContactInfo = billingContactInfo
        self.creditCard = creditCard
        self.pfToken = pfToken
        self.status = status

    def toDict(self) -> dict:
        result = {
        }

        self._setToDictIfHasValues(
            resultDict=result,
            keys=[
                "status",
                "pfToken"
            ]
        )

        if self.billingContactInfo:
            result["billingContactInfo"] = self.billingContactInfo.toDict()

        if self.creditCard:
            result["creditCard"] = self.creditCard.toDict()

        return result


class VaultedShopperResource(Resource):
    path = '/services/2/vaulted-shoppers'

    def __init__(self):
        super(VaultedShopperResource, self).__init__()

    def retrieve(self, vaultedShopperId: str) -> dict:
        """
        The Retrieve Vaulted Shopper request retrieves all the saved details for the shopper associated with the
        vaultedShopperId you send in the request.

        https://developers.bluesnap.com/v8976-JSON/docs/retrieve-vaulted-shopper

        :param vaultedShopperId:
        :return:
        """

        response, body = self.request('GET', '%s/%s' % (self.path, vaultedShopperId))

        return dict(body['vaulted-shopper'])

    def retrieveByMerchantShopperId(self, merchantShopperId: str) -> dict:
        """
        The Retrieve Vaulted Shopper request retrieves all the saved details for the shopper associated with the
        merchantShopperId you send in the request.

        https://developers.bluesnap.com/v8976-JSON/docs/retrieve-vaulted-shopper

        :param merchantShopperId:
        :return:
        """

        response, body = self.request('GET', '%s/merchant/%s' % (self.path, merchantShopperId))

        return dict(body['vaulted-shopper'])

    def create(
            self,
            vaultedShopperInfo: VaultedShopperInfo,
            paymentSource: List[CreditCardInfo],
            # TODO: ecpInfo
            # TODO: sepaDirectDebitInfo
    ) -> dict:
        """
        The Create Vaulted Shopper request enables you to store a shopper's details (including payment info) securely
        in BlueSnap. BlueSnap will provide a token (vaultedShopperId) for that saved shopper.

        This method creates it based on a Hosted Payment Fields token.

        You can then use the vaultedShopperId in order to complete payment transactions, improve the checkout
        experience for a returning shopper, and update the shopper's payment details.

        https://developers.bluesnap.com/v8976-JSON/docs/create-vaulted-shopper

        :param vaultedShopperInfo: This is used for invoices, and to show information about the user in BlueSnap itself
        :param paymentSource: Contains payment source information for vaulted shoppers. More info:
            https://developers.bluesnap.com/v8976-JSON/docs/payment-sources
        :return:
        """

        data = {
            "paymentSources": {
                "creditCardInfo": [
                    creditCardInfo.toDict() for creditCardInfo in paymentSource
                ]
            }
        }

        data.update(vaultedShopperInfo.toDict())

        response, body = self.request('POST', self.path, data=data)

        return body

    def update(
            self,
            vaultedShopperId: str,
            vaultedShopperInfo: VaultedShopperInfo,
            paymentSource: List[CreditCardInfo],
            # TODO: ecpInfo
            # TODO: sepaDirectDebitInfo
    ) -> dict:
        """
        The Update Vaulted Shopper request enables you to update an existing vaulted shopper by changing their
        contact info, adding credit card details, or adding wallet details.

        Note: It is suggested that you first retrieve the vaulted shopper and then modify the desired property.

        More info: https://developers.bluesnap.com/v8976-JSON/docs/update-vaulted-shopper

        :param vaultedShopperId:
        :param vaultedShopperInfo: Contains information about the vaulted shopper,
            More info here: https://developers.bluesnap.com/v8976-JSON/docs/vaulted-shopper
        :param paymentSource: TODO
        :return: The vaultedShopper object, which contains all details that are saved for that shopper.

        """

        data = {
            "paymentSources": {
                "creditCardInfo": [
                    creditCardInfo.toDict() for creditCardInfo in paymentSource
                ]
            }
        }
        data.update(vaultedShopperInfo.toDict())

        response, body = self.request('PUT', '%s/%s' % (self.path, vaultedShopperId), data=data)

        return body


class TransactionMetadata:
    """
    The Payment API enables you to associate any data you wish to any type of transaction by using the flexible
    metadata property in your requests. This elegant approach to handling key business data allows you to create
    fields that append key information to a payment, such as product info, customer info, key dates, shipping and tax,
    or more. By using metadata, you can store the info that is most useful for your business and build the reporting
    needed.

    https://developers.bluesnap.com/v8976-JSON/docs/metadata

    Examples:
    [
        {
            "metaValue": 20,
            "metaKey": "stateTaxAmount",
            "metaDescription": "State Tax Amount"
        },
        {
            "metaValue": 20,
            "metaKey": "cityTaxAmount",
            "metaDescription": "City Tax Amount"
        },
        {
            "metaValue": 10,
            "metaKey": "shippingAmount",
            "metaDescription": "Shipping Amount"
        }
    ]
    """

    def __init__(self, value: str, key: str, description: str):

        if value is None or value == "" or key is None or key == "" or description is None or description == "":
            raise ValueError(
                'Missing value %s, key %s or description %s.' % (value, key, description)
            )

        self.value = str(value)
        self.key = str(key)
        self.description = str(description)

        if len(self.value) > 500 or len(self.key) > 40 or len(self.description) > 40:
            raise ValueError('Maximum length in chars - value: 500, key: 40, description: 40')

    def toDict(self) -> dict:

        return {
            "metaValue":       self.value,
            "metaKey":         self.key,
            "metaDescription": self.description
        }


class TransactionResource(Resource):
    path = '/services/2/transactions'

    def __init__(self):
        super(TransactionResource, self).__init__()

    def authCapture(
            self,
            amount: str,
            currency: str,
            transactionInitiator: str = "SHOPPER",
            vaultedShopperId: str = None,
            creditCard: CreditCard = None,
            pfToken: str = None,
            cardHolderInfo: CardHolderInfo = None,
            merchantTransactionId: str = None,
            softDescriptor: str = None,
            descriptorPhoneNumber: str = None,
            level3Data: Level3Data = None,
            networkTransactionInfo: NetworkTransactionInfo = None,
            threeDSecure: ThreeDSecure = None,
            transactionOrderSource: str = None,
            transactionMetadataObjectList: list = ()
    ) -> dict:
        """
        Auth Capture performs two actions via a single request:

            authorize: checks whether a credit card is valid and has the funds to complete a specific
                transaction (i.e. purchase)
            capture: submits the authorized transaction for settlement (i.e. payment by the shopper)

        https://developers.bluesnap.com/v8976-JSON/docs/auth-capture

        :param amount:
        :param currency:
        :param transactionInitiator:
        :param vaultedShopperId:
        :param creditCard: Use this to select the credit card of the vaulted shopper.
        :param pfToken: Hosted Payment Fields token.
        :param cardHolderInfo: Required if supplying a pfToken.
        :param merchantTransactionId: Merchant's unique ID for a new transaction. Between 1-50 characters.
        :param softDescriptor: Description of the transaction, which appears on the shopper's credit card statement.
            Maximum 20 characters. Overrides merchant default value.
        :param descriptorPhoneNumber: Merchant's support phone number that will appear on the shopper's credit card
            statement. Maximum 20 characters. Overrides merchant default value.
        :param level3Data: Contains Level 2/3 data properties for the transaction
        :param networkTransactionInfo: Contains the network transaction information for this transaction
        :param threeDSecure: Contains 3D Secure details for this transaction
        :param transactionOrderSource: Identifies the order type. The only option is MOTO (Mail Order Telephone Order).
        :param transactionMetadataObjectList:
        :return:
        """

        return self._executeTransaction(
            cardTransactionType="AUTH_CAPTURE",
            amount=amount,
            currency=currency,
            transactionInitiator=transactionInitiator,
            vaultedShopperId=vaultedShopperId,
            creditCard=creditCard,
            pfToken=pfToken,
            cardHolderInfo=cardHolderInfo,
            merchantTransactionId=merchantTransactionId,
            softDescriptor=softDescriptor,
            descriptorPhoneNumber=descriptorPhoneNumber,
            level3Data=level3Data,
            networkTransactionInfo=networkTransactionInfo,
            threeDSecure=threeDSecure,
            transactionOrderSource=transactionOrderSource,
            transactionMetadataObjectList=transactionMetadataObjectList
        )

    def retrieve(self, transactionId: str) -> dict:

        """
        Retrieve is a request that gets details about a past transaction, such as the transaction type, amount,
        cardholder or vaulted shopper, credit card, processing info, and so on.

        https://developers.bluesnap.com/v8976-JSON/docs/retrieve

        :param transactionId: transaction ID received in the response from BlueSnap
        :return:
        """

        response, body = self.request('GET', '%s/%s' % (self.path, transactionId))

        return dict(body['card-transaction'])

    def auth(
            self,
            amount: str,
            currency: str,
            transactionInitiator: str = "SHOPPER",
            vaultedShopperId: str = None,
            creditCard: CreditCard = None,
            pfToken: str = None,
            cardHolderInfo: CardHolderInfo = None,
            transactionFraudInfo: TransactionFraudInfo = None,
            threeDSecure: ThreeDSecure = None,
            merchantTransactionId: str = None,
            softDescriptor: str = None,
            descriptorPhoneNumber: str = None,
            level3Data: Level3Data = None,
            transactionMetadataObjectList: list = ()

    ) -> dict:
        """
        Auth Only is a request to check whether a credit card is valid and has the funds to complete a specific
        transaction (i.e. purchase). It does not actually run the charge on the card, but does temporarily hold
        the funds aside. Note that each credit card company will only hold the authorization for a limited period
        (for example, 3-10 days, depending on the credit card scheme).

        Zero value auth for card validity checks:

        If you wish to check the validity of a card without authorizing any charge amount, simply enter 0 as the
        value for the amount property in this request.

        https://developers.bluesnap.com/v8976-JSON/docs/auth-only

        :param amount:
        :param currency:
        :param transactionInitiator:
        :param vaultedShopperId:
        :param creditCard: Use this to select the credit card of the vaulted shopper.
        :param pfToken: Hosted Payment Fields token.
        :param cardHolderInfo: Required if supplying a pfToken.
        :param transactionFraudInfo:
        :param threeDSecure: Contains 3D Secure details for this transaction
        :param merchantTransactionId: Merchant's unique ID for a new transaction. Between 1-50 characters.
        :param softDescriptor: Description of the transaction, which appears on the shopper's credit card statement.
            Maximum 20 characters. Overrides merchant default value.
        :param descriptorPhoneNumber: Merchant's support phone number that will appear on the shopper's credit card
            statement. Maximum 20 characters. Overrides merchant default value.
        :param level3Data: Contains Level 2/3 data properties for the transaction
        :param transactionMetadataObjectList:

        :return:
        """

        return self._executeTransaction(
            cardTransactionType="AUTH_ONLY",
            amount=amount,
            currency=currency,
            transactionInitiator=transactionInitiator,
            vaultedShopperId=vaultedShopperId,
            creditCard=creditCard,
            pfToken=pfToken,
            cardHolderInfo=cardHolderInfo,
            transactionFraudInfo=transactionFraudInfo,
            threeDSecure=threeDSecure,
            merchantTransactionId=merchantTransactionId,
            softDescriptor=softDescriptor,
            descriptorPhoneNumber=descriptorPhoneNumber,
            level3Data=level3Data,
            transactionMetadataObjectList=transactionMetadataObjectList,
        )

    def capture(
            self,
            transactionId: str,
            amount: str,
            softDescriptor: str = None,
            level3Data: Level3Data = None,
            transactionMetadataObjectList: list = ()
    ) -> dict:
        """
        Capture is a request that submits a previously authorized transaction for settlement (i.e. payment by the
        shopper). Note that each credit card company will only hold the authorization for a limited period (for
        example, 3-10 days, depending on the credit card scheme).

        Before you can send a transaction for capture, you must send it for authorization using the Auth Only request.

        The capture will be performed based on the details that were in the Auth Only request (currency, credit card,
        etc.).

        https://developers.bluesnap.com/v8976-JSON/docs/capture

        :param transactionId: transaction ID received in the response from BlueSnap
        :param amount:  default value is the full authorization amount
        :param softDescriptor: Description of the transaction, which appears on the shopper's credit card statement.
            Maximum 20 characters. Overrides merchant default value.
        :param level3Data: Contains Level 2/3 data properties for the transaction
        :param transactionMetadataObjectList:
        :return:
        """

        return self._executeTransaction(
            cardTransactionType="CAPTURE",
            transactionId=transactionId,
            amount=amount,
            softDescriptor=softDescriptor,
            level3Data=level3Data,
            transactionMetadataObjectList=transactionMetadataObjectList
        )

    def reverse(self, transactionId: str) -> dict:

        """
        Auth Reversal is a request that reverses, or voids, a previously approved authorization that has not yet
        been captured.
        Note: The reversal must be performed within 8 days of the initial Auth Only request, or else an error will
        occur.

        An Auth Reversal will void the entire transaction amount, so the amount property is not relevant.

        https://developers.bluesnap.com/v8976-JSON/docs/auth-reversal

        :param transactionId: transaction ID received in the response from BlueSnap
        :return:
        """

        return self._executeTransaction(
            cardTransactionType="AUTH_REVERSAL",
            transactionId=transactionId,
            mode="PUT",
        )

    def _executeTransaction(
            self,
            cardTransactionType: str,
            transactionId: Optional[str] = None,
            transactionInitiator: Optional[str] = None,
            amount: Optional[str] = None,
            currency: Optional[str] = None,
            vaultedShopperId: Optional[str] = None,
            creditCard: Optional[CreditCard] = None,
            pfToken: Optional[str] = None,
            cardHolderInfo: Optional[CardHolderInfo] = None,
            transactionFraudInfo: Optional[TransactionFraudInfo] = None,
            merchantTransactionId: Optional[str] = None,
            softDescriptor: Optional[str] = None,
            descriptorPhoneNumber: Optional[str] = None,
            level3Data: Optional[Level3Data] = None,
            networkTransactionInfo: Optional[NetworkTransactionInfo] = None,
            threeDSecure: Optional[ThreeDSecure] = None,
            transactionOrderSource: Optional[str] = None,
            transactionMetadataObjectList: list = (),
            mode: str = "POST",
    ) -> dict:
        """
        Internal, perform an auth/capture operation.

        :param cardTransactionType:
        :param transactionId:
        :param transactionInitiator: Identifies who initiated the order. Options are:
            MERCHANT (for MIT)
            SHOPPER (for CIT)
        :param amount:
        :param currency:
        :param vaultedShopperId:
        :param creditCard: Use this to select the credit card of the vaulted shopper.
        :param pfToken: Hosted Payment Fields token.
        :param cardHolderInfo: Required if supplying a pfToken.
        :param transactionFraudInfo:
        :param merchantTransactionId:
        :param softDescriptor:
        :param descriptorPhoneNumber:
        :param level3Data:
        :param networkTransactionInfo: Contains the network transaction information for this transaction
        :param threeDSecure: Contains 3D Secure details for this transaction
        :param transactionOrderSource: Identifies the order type. The only option is MOTO (Mail Order Telephone Order).
        :param transactionMetadataObjectList:

        :return:
        """

        data = {
            "cardTransactionType":  cardTransactionType,
        }

        if transactionId:
            data["transactionId"] = transactionId

        if transactionInitiator:
            if not transactionInitiator in {"SHOPPER", "MERCHANT"}:
                raise RuntimeError("transactionInitiator must be SHOPPER or MERCHANT.")
            data["transactionInitiator"] = transactionInitiator

        if amount:
            data["amount"] = amount

        if currency:
            data["currency"] = currency

        if transactionOrderSource:
            if not transactionOrderSource == "MOTO":
                raise RuntimeError("transactionOrderSource must be of the value MOTO or null.")
            data["transactionOrderSource"] = transactionOrderSource

        if vaultedShopperId:
            pfToken = None

        if vaultedShopperId:
            data["vaultedShopperId"] = vaultedShopperId

            if creditCard:
                data["creditCard"] = creditCard.toDict()

        if pfToken:
            data["pfToken"] = pfToken

            if cardHolderInfo:
                data['cardHolderInfo'] = cardHolderInfo.toDict()

        if transactionFraudInfo:
            data["transactionFraudInfo"] = transactionFraudInfo.toDict()

        if merchantTransactionId:
            data['merchantTransactionId'] = merchantTransactionId

        if softDescriptor:
            data['softDescriptor'] = softDescriptor

        if descriptorPhoneNumber:
            data['descriptorPhoneNumber'] = softDescriptor

        if level3Data:
            data['level3Data'] = level3Data.toDict()

        if networkTransactionInfo:
            data['networkTransactionInfo'] = networkTransactionInfo.toDict()

        if threeDSecure:
            data['threeDSecure'] = threeDSecure.toDict()

        transactionMetaData = []
        for currentMetadataObject in transactionMetadataObjectList:
            transactionMetaData.append(currentMetadataObject.toDict())
        if transactionMetaData:
            data['transactionMetaData'] = {
                'metaData': transactionMetaData
            }

        response, body = self.request(mode, self.path, data=data)

        return body
