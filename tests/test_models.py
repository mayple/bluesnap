from unittest import TestCase

from bluesnap import models
from .helper import NAMESPACE_PREFIX, DUMMY_CARD_VISA, configure_client, get_xml_schema


configure_client()


class PlainCreditCardTestCase(TestCase):
    model = models.PlainCreditCard

    def setUp(self):
        self.card = DUMMY_CARD_VISA

        self.instance = self.model(
            card_type=self.card['card_type'],
            expiration_month=self.card['expiration_month'],
            expiration_year=self.card['expiration_year'],
            card_number=self.card['card_number'],
            security_code=self.card['security_code']
        )

        self.xml = self.instance.to_xml()

    def test_to_xml_returns_correct_schema(self):
        # Validate XML schema
        get_xml_schema('credit-card-info.xsd').assertValid(self.xml)

    def test_to_xml_sets_correct_values(self):
        self.assertEqual(self.xml.tag, '{http://ws.plimus.com}credit-card')

        # Validate values being set correctly
        for xml_key, dict_key in [('card-type', 'card_type'),
                                  ('expiration-month', 'expiration_month'),
                                  ('expiration-year', 'expiration_year'),
                                  ('card-number', 'card_number'),
                                  ('security-code', 'security_code')]:
            self.assertEqual(self.xml.find(NAMESPACE_PREFIX + xml_key).text, str(self.card[dict_key]))


class EncryptedCreditCardTestCase(TestCase):
    model = models.EncryptedCreditCard

    def setUp(self):
        self.card = DUMMY_CARD_VISA

        self.instance = self.model(
            card_type=self.card['card_type'],
            expiration_month=self.card['expiration_month'],
            expiration_year=self.card['expiration_year'],
            encrypted_card_number=self.card['encrypted_card_number'],
            encrypted_security_code=self.card['encrypted_security_code']
        )

        self.xml = self.instance.to_xml()

    def test_to_xml_returns_correct_schema(self):
        # Validate XML schema
        get_xml_schema('credit-card-info.xsd').assertValid(self.xml)

    def test_to_xml_sets_correct_values(self):
        self.assertEqual(self.xml.tag, '{http://ws.plimus.com}credit-card')

        # Validate values being set correctly
        for xml_key, dict_key in [('card-type', 'card_type'),
                                  ('expiration-month', 'expiration_month'),
                                  ('expiration-year', 'expiration_year'),
                                  ('encrypted-card-number', 'encrypted_card_number'),
                                  ('encrypted-security-code', 'encrypted_security_code')]:
            element = self.xml.find(NAMESPACE_PREFIX + xml_key)

            self.assertIsNotNone(element, 'Cannot find element <{}/>'.format(NAMESPACE_PREFIX + xml_key))
            self.assertEqual(element.text, str(self.card[dict_key]))


class CreditCardSelectionTestCase(TestCase):
    model = models.CreditCardSelection

    def setUp(self):
        self.card = DUMMY_CARD_VISA

        self.instance = self.model(
            card_type=self.card['card_type'],
            card_last_four_digits=self.card['card_number'][-4:]
        )

        self.xml = self.instance.to_xml()

    def test_to_xml_returns_correct_schema(self):
    # Validate XML schema
        get_xml_schema('credit-card-info.xsd').assertValid(self.xml)

    def test_to_xml_sets_correct_values(self):
        self.assertEqual(self.xml.tag, '{http://ws.plimus.com}credit-card')

        # Validate values being set correctly
        self.assertEqual(self.xml.find(NAMESPACE_PREFIX + 'card-type').text, self.card['card_type'])
        self.assertEqual(self.xml.find(NAMESPACE_PREFIX + 'card-last-four-digits').text, self.card['card_number'][-4:])


class WebInfoTestCase(TestCase):
    model = models.WebInfo

    def setUp(self):
        self.instance = self.model()
        self.xml = self.instance.to_xml()

    def test_to_xml_returns_correct_schema(self):
    # Validate XML schema
        get_xml_schema('web-info.xsd').assertValid(self.xml)

    def test_to_xml_sets_correct_values(self):
        self.assertEqual(self.xml.tag, '{http://ws.plimus.com}web-info')

        # Validate values being set correctly
        for xml_key, dict_key in [('ip', 'ip'),
                                  ('remote-host', 'remote_host'),
                                  ('user-agent', 'user_agent')]:
            element = self.xml.find(NAMESPACE_PREFIX + xml_key)

            self.assertIsNotNone(element, 'Cannot find element <{}/>'.format(NAMESPACE_PREFIX + xml_key))
            self.assertEqual(element.text, getattr(self.instance, dict_key))


class ContactInfoTestCase(TestCase):
    model = models.ContactInfo
    element_name = '{http://ws.plimus.com}contact-info'

    def setUp(self):
        self.contact_info = {
            'email': 'test@justyoyo.com',
            'first_name': 'John',
            'last_name': 'Doe'
        }

        self.instance = self.model(**self.contact_info)
        self.xml = self.instance.to_xml()

    def test_to_xml_sets_correct_element_name(self):
        self.assertEqual(self.instance.to_xml('billing').tag, '{http://ws.plimus.com}billing-contact-info')
        self.assertEqual(self.instance.to_xml('shopper').tag, '{http://ws.plimus.com}shopper-contact-info')

    def test_to_xml_sets_correct_values(self):
        self.assertEqual(self.xml.tag, self.element_name, '{http://ws.plimus.com}contact-info')

        # Validate values being set correctly
        for xml_key, dict_key in [('first-name', 'first_name'),
                                  ('last-name', 'last_name'),
                                  ('email', 'email'),
                                  ('address1', 'address_1'),
                                  ('city', 'city'),
                                  ('zip', 'zip'),
                                  ('country', 'country'),
                                  ('phone', 'phone')]:
            element = self.xml.find(NAMESPACE_PREFIX + xml_key)

            self.assertIsNotNone(element, 'Cannot find element <{}/>'.format(NAMESPACE_PREFIX + xml_key))
            self.assertEqual(element.text, getattr(self.instance, dict_key))
