# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import frappe
import requests
from frappe.utils import fmt_money

eu = ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "EL", "ES", "FR", "HR",
	"IT", "CY", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT",
	"RO", "SI", "SK", "FI", "SE"]

def get_context(context):
	context.no_cache = True
	country_code = get_country().get("countryCode")

	if country_code == 'IN':
		context.currency = 'INR'
		context.symbol = '₹'

	else:
		context.currency = 'USD'
		context.symbol = '$'

	context.base_features = {
		'all_modules': {
			'title': 'All Modules',
			'content': 'Accounting, Inventory, HR and more'
		},
		'email_support': {
			'title': 'Email Support',
			'content': 'Email Support during bussiness hours'
		},
		'backup': {
			'title': 'Backup + Redundancy',
			'content': 'Daily offsite backups on AWS'
		},
		'priority_support': {
			'title': 'Priority Support',
			'content': '24 hours priority support'
		},
		'account_manager': {
			'title': 'Account Manager',
			'content': 'Dedicated account manager to fulfill your requirements.'
		}
	}

	context.plan_features = ['Server and Emails', 'Customization', 'Integrations + API']

	def get_plan_and_pricing(plan_name):
		plan = frappe.get_doc('Base Plan', plan_name)
		pricing = [d.as_dict() for d in plan.amounts if d.currency == context.currency][0]
		pricing['symbol'] = context.symbol

		return plan, pricing

	business_plan, business_plan_pricing = get_plan_and_pricing('P-Standard')
	enterprise_plan, enterprise_plan_pricing = get_plan_and_pricing('P-Pro')

	context.plans = [
		{
			'name': business_plan.name,
			'title': business_plan.name.replace('P-', ''),
			'pricing': business_plan_pricing,
			'storage': business_plan.space,
			'emails': business_plan.emails,
			'base_features': ['all_modules', 'email_support', 'backup'],
			'features': [
				{
					'title': 'Organisations',
					'content': [
						'3 Companies',
					]
				},
				{
					'title': 'Server and Emails ',
					'content': [
						'5 GB cloud storage',
						'5000 emails / month',
						'Extensible via add-ons'
					]
				},
				{
					'title': 'Customization',
					'content': [
						'Customized Print Formats and Email Alerts',
						'30 Custom Fields',
						'10 Custom Forms, 10 Custom Scripts'
					]
				},
				{
					'title': 'Integrations + API',
					'content': [
						'Email Integration and REST API',
						'Payment Gateways',
						'Dropbox, Shopify and AWS'
					]
				}
			],

		},
		{
			'name': enterprise_plan.name,
			'title': enterprise_plan.name.replace('P-', ''),
			'pricing': enterprise_plan_pricing,
			'storage': enterprise_plan.space,
			'emails': enterprise_plan.emails,
			'base_features': ['all_modules', 'priority_support', 'backup'],
			'features': [
				{
					'title': 'Organisations',
					'content': [
						'Unlimited Companies',
					]
				},
				{
					'title': 'Server and Emails',
					'content': [
						'15 GB cloud storage',
						'15000 emails / month',
						'Extensible via add-ons'
					]
				},
				{
					'title': 'Customization',
					'content': [
						'Customized Print Formats and Email Alerts',
						'Unlimited Custom Fields',
						'Unlimited Custom Forms and Scripts'
					]
				},
				{
					'title': 'Integrations + API',
					'content': [
						'Email Integration and REST API',
						'Payment Gateways',
						'Dropbox, Shopify and AWS'
					]
				}
			],
		},
		{
			'name': '$$$$$',
			'title': 'Enterprise',
			'no_pricing': True,
			'description': 'Enterprise Implementation and Customizations',
			'base_features': ['all_modules', 'account_manager', 'priority_support', 'backup'],
			'features': [
				{
					'title': 'Organisations',
					'content': [
						'Unlimited Companies',
					]
				},
				{
					'title': 'Server and Emails',
					'content': [
						'Private Server',
						'Unlimited storage',
						'Unlimited emails'
					]
				},
				{
					'title': 'Customization',
					'content': [
						'Customized Print Formats and Email Alerts',
						'Unlimited Custom Fields',
						'Unlimited Custom Forms and Scripts'
					]
				},
				{
					'title': 'Integrations + API',
					'content': [
						'Email Integration and REST API',
						'Payment Gateways',
						'Dropbox, Shopify and AWS'
					]
				}
			],
		}
	]


@frappe.whitelist(allow_guest=True)
def get_plan_details(plan_name):
	currency = 'USD'
	symbol = '$'

	if get_country().get('countryCode') == 'IN':
		currency = 'INR'
		symbol = '₹'

	plan = frappe.get_doc('Base Plan', plan_name)
	pricing = [d for d in plan.amounts if d.currency == currency][0].as_dict()

	pricing['symbol'] = symbol

	plan = plan.as_dict()
	plan['pricing'] = pricing

	return plan

country_info = {}

@frappe.whitelist(allow_guest=True)
def get_country(fields=None):
	global country_info
	ip = frappe.local.request_ip

	if not ip in country_info:
		fields = ['countryCode', 'country', 'regionName', 'city']
		res = requests.get('https://pro.ip-api.com/json/{ip}?key={key}&fields={fields}'.format(
			ip=ip, key=frappe.conf.get('ip-api-key'), fields=','.join(fields)))

		try:
			country_info[ip] = res.json()

		except Exception:
			country_info[ip] = {}

	return country_info[ip]