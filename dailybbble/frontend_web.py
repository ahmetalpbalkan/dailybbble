# coding=utf-8

import datetime
from . import service
from . import email
from os import environ
from dateutil.relativedelta import relativedelta
import calendar
from flask import render_template, redirect, url_for, request
from dailybbble import app


ARCHIVE_LISTING_SHOTS = 3 * 2 + 6 * 4
HOME_TODAY_SHOTS = 6
CALENDAR_START = datetime.date(2013, 0o5, 30)
DISABLE_EMAIL='DISABLE_EMAIL'

def is_email_disabled():
    return DISABLE_EMAIL in environ and environ[DISABLE_EMAIL] == '1'

@app.route('/')
def home(subscribe=False, subscribe_success=True):
    today_utc = datetime.datetime.utcnow().date() - datetime.timedelta(days=1)
    today_popular = service.popular_shots_of_day(today_utc, HOME_TODAY_SHOTS)
    return render_template('pages/home.html', today_popular=today_popular,
                           today=today_utc, subscribe=subscribe,
                           subscribe_success=subscribe_success,
                           disable_email=is_email_disabled())


@app.route('/subscribe', methods=['GET'])
def subscribe():
    return redirect(url_for('home'))


@app.route('/subscribe', methods=['POST'])
def subscribe_form():
    if is_email_disabled():
        return 'Email subscription is disabled', 400

    addr = request.form.get('email', None)
    mode = request.form.get('mode', email.DAILY_OPTION)

    lists = email.get_email_list_names()
    if mode == email.DAILY_OPTION:
        list_name = lists[0]
    elif mode == email.WEEKLY_OPTION:
        list_name = lists[1]
    else:
        return 'Invalid subscription type.', 400
    subscribed = email.add_subscriber(addr, list_name) if addr else False
    return home(subscribe=True, subscribe_success=subscribed)


@app.route('/archive/<int:year>/<int:month>/<int:day>/')
def archive_day(year, month, day):
    date = datetime.date(year, month, day)

    if date < CALENDAR_START:
        return redirect(url_for('archive_day', year=CALENDAR_START.year,
                                month=CALENDAR_START.month,
                                day=CALENDAR_START.day))

    shots = service.popular_shots_of_day(date, ARCHIVE_LISTING_SHOTS)
    return render_template('pages/archive_day.html', shots=shots,
                           day=date)


@app.route('/archive/<int:year>/<int:month>/')
def archive_month(year, month):
    calendar_start_month = datetime.date(CALENDAR_START.year,
                                         CALENDAR_START.month, 1)
    first_month_redir = redirect(url_for('archive_month',
                                         year=CALENDAR_START.year,
                                         month=CALENDAR_START.month))
    if year == 0 or month == 0:
        return first_month_redir

    date = datetime.date(year, month, 1)
    if date < calendar_start_month:
        return first_month_redir

    today = datetime.datetime.utcnow().date()
    if date > today:
        return redirect(url_for('archive_month',
                                year=today.year,
                                month=today.month))

    cal = calendar.Calendar()
    days = list(cal.itermonthdays2(date.year, date.month))

    prev = date - relativedelta(months=1)
    next = date + relativedelta(months=1)
    prev_disabled = prev < calendar_start_month
    next_disabled = next > today

    return render_template('pages/archive_month.html', date=date, days=days,
                           prev=prev, prev_disabled=prev_disabled,
                           next=next, next_disabled=next_disabled,
                           today=today)


@app.route('/api/documentation')
def api_docs():
    return render_template('pages/api_docs.html')
