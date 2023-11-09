import datetime
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from .models import Site, PhoneNumber, Email, Link
from django.core.exceptions import ObjectDoesNotExist

def get_emails_and_phone_numbers_and_links(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    page_source = driver.page_source

    emails = re.findall(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_source)
    emails = set(emails)

    phone_numbers = re.findall(
        r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', page_source)
    phone_numbers = set(phone_numbers)

    link_pattern = re.compile(r'https?://')

    link_elements = driver.find_elements(By.TAG_NAME, 'a')
    links = [str(element.get_attribute('href')) for element in link_elements]
    links = set(links)

    links = {link for link in links if link_pattern.match(link)}

    driver.quit()

    return emails, phone_numbers, links

def insert_emails_and_phone_numbers_and_links(emails, phone_numbers, links, site_obj):
    for email in emails:
        try:
            email_obj = Email.objects.get(email=email)
        except ObjectDoesNotExist:
            email_obj = Email.objects.create(email=email)
            email_obj.save()
        site_obj.emails.add(email_obj)

    for phone_number in phone_numbers:
        try: 
            phone_number_obj = PhoneNumber.objects.get(num=phone_number)
        except ObjectDoesNotExist:
            phone_number_obj = PhoneNumber.objects.create(num=phone_number)
            phone_number_obj.save()
        site_obj.phone_numbers.add(phone_number_obj)

    for link in links:
        try:
            link_obj = Link.objects.get(url=link)
        except ObjectDoesNotExist:
            link_obj = Link.objects.create(url=link)
            link_obj.save()
        site_obj.links.add(link_obj)


def home_view(req):
    return render(req, "index.html", {})

@login_required(login_url = 'login')
def result_view(req):
    if req.method == 'POST':
        url = req.POST.get('url')

        cache_days = 1

        try:
            site_obj = Site.objects.get(url=url)
        except ObjectDoesNotExist:
            site_obj = None
        
        if site_obj == None:
            emails, phone_numbers, links = get_emails_and_phone_numbers_and_links(url)

            site_obj = Site.objects.create(url=url)
            site_obj.save()

            insert_emails_and_phone_numbers_and_links(emails, phone_numbers, links, site_obj)

        elif site_obj.last_edited < timezone.now() - timezone.timedelta(days=cache_days):
            emails, phone_numbers, links = get_emails_and_phone_numbers_and_links(url) 
            insert_emails_and_phone_numbers_and_links(emails, phone_numbers, links, site_obj)
            site_obj.last_edited = timezone.now()
            site_obj.save()

        else:
            emails = [email.email for email in site_obj.emails.all()]
            phone_numbers = [phone_number.num for phone_number in site_obj.phone_numbers.all()]
            links = [link.url for link in site_obj.links.all()]

        return render(req, "result.html", {
            "status": "true",
            "emails": emails,
            "links": links,
            "phone_numbers": phone_numbers,
        })

    return render(req, "result.html", {
        "status": "false",
    })
