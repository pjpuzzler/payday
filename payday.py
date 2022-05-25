import curses
from datetime import datetime, time, timedelta
from time import sleep

from humanize.time import naturaldelta, precisedelta

START_DATE = datetime(2022, 5, 23, 9)  # May 23, 2022 9:00 AM
HOURLY_WAGE = 16.00
START_TIME = time(9)  # 9:00 AM
END_TIME = time(17)  # 5:00 PM
DAILY_HOURS_WORKED = 7
BREAK_TIME = time(13)  # 1:00 PM
BREAK_DURATION = timedelta(hours=1)
TAX_PERCENTAGE = 0.2233
TIME_OFF = timedelta()
PAY_INTERVAL = timedelta(weeks=2)  # Biweekly
PAY_INTERVAL_DAYS = 10
FIRST_PAYDAY = datetime(2022, 6, 3, 17)  # June 3, 2022 5:00 PM

TOTAL_DAILY_EARNINGS = DAILY_HOURS_WORKED * HOURLY_WAGE * (1 - TAX_PERCENTAGE)
TOTAL_PAYDAY_EARNINGS = PAY_INTERVAL_DAYS * TOTAL_DAILY_EARNINGS

stdscr = curses.initscr()

while True:
    curses.resize_term(*stdscr.getmaxyx())
    stdscr.clear()

    now = datetime.now()
    day_start = datetime.combine(now.date(), START_TIME)
    break_start = datetime.combine(now.date(), BREAK_TIME)
    day_end = datetime.combine(now.date(), END_TIME)

    time_worked_prev = timedelta(
        hours=(now - START_DATE).days * DAILY_HOURS_WORKED) - TIME_OFF

    # completed a full day today
    if now >= day_end:
        time_worked_today = timedelta(hours=DAILY_HOURS_WORKED)
    # have worked a partial day so far
    elif now > day_start:
        time_worked_today = now - day_start
        # have started a break so far today
        if now > break_start:
            time_worked_today -= min(now - break_start, BREAK_DURATION)
    else:
        time_worked_today = timedelta()

    time_worked = time_worked_prev + time_worked_today

    next_payday = FIRST_PAYDAY
    while next_payday < now:
        next_payday += PAY_INTERVAL

    time_until_payday = next_payday - now

    money_earned = time_worked.total_seconds() * HOURLY_WAGE / 3600
    taxes_paid = money_earned * TAX_PERCENTAGE
    money_earned_today = time_worked_today.total_seconds() * HOURLY_WAGE / 3600 * \
        (1 - TAX_PERCENTAGE)

    prev_payday = next_payday - PAY_INTERVAL
    time_worked_before_payday = (timedelta(hours=(prev_payday - START_DATE).days *
                                 DAILY_HOURS_WORKED) - TIME_OFF) if prev_payday > START_DATE else timedelta()
    time_worked_payday = time_worked - time_worked_before_payday
    money_earned_payday = time_worked_payday.total_seconds() * HOURLY_WAGE / \
        3600 * (1 - TAX_PERCENTAGE)

    stdscr.addstr(
        0, 0, f'Gross Earnings: ${money_earned:,.2f} (${HOURLY_WAGE / 3600:,.4f}/s)')
    stdscr.addstr(1, 0, f'Taxes Paid:    -${taxes_paid:,.2f}')
    stdscr.addstr(
        1, 40, f'Time Worked: {precisedelta(time_worked, format="%.0f")}')
    stdscr.addstr(
        2, 0, f'Net Earnings:   ${(money_earned - taxes_paid):,.2f} (${HOURLY_WAGE / 3600 * (1 - TAX_PERCENTAGE):,.4f}/s)')

    stdscr.addstr(
        4, 0, f'Payday Earnings: ${money_earned_payday:,.2f}/${TOTAL_PAYDAY_EARNINGS:,.2f}')
    stdscr.addstr(
        4, 40, f'Time Until Payday: {naturaldelta(time_until_payday)}')

    stdscr.addstr(
        6, 0, f'Earnings Today: ${money_earned_today:,.2f}/${TOTAL_DAILY_EARNINGS:,.2f}')
    stdscr.addstr(
        6, 40, f'Time Worked Today: {precisedelta(time_worked_today, format="%.0f")}')

    stdscr.refresh()
    sleep(0.25)