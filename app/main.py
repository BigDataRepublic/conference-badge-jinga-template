"""
Conference Badge Generator

This script serves as the main entry point for the Flask application that generates conference badges for attendees.
It uses a 4-fold model and Jinja templating to create unique badges for each visitor based on the provided data in
visitors.py and quotes.py. The final badge is rendered using the badge.html template.
"""

from flask import Flask, render_template, send_from_directory
from werkzeug.utils import safe_join

from quotes import data_quotes
from visitors import visitors, breakout, attach_breakout_sessions_to_visitors, find_fuzzy_email_matches, assign_breakout_sessions, morning_breakouts, afternoon_breakouts, linked_breakout_emails, generate_all_qr_codes

import os

app = Flask("Template", static_folder='./static')

visitors = attach_breakout_sessions_to_visitors(visitors, breakout)
visitors = find_fuzzy_email_matches(visitors, breakout)
generate_all_qr_codes(visitors)

"""
    For all visitors that didnt signup for a breakout, assign a
    'random' (based on email hash) one, to make sure everyone has a seat.
"""
assign_breakout_sessions(visitors, morning_breakouts, afternoon_breakouts)

@app.route("/")
def overview():

    breakout_signups = sum([v.get('exact_match', False) for v in visitors] )


    conference_stats = { 
        'visitors_count' : len(visitors),
        'visitors_breakout_count' : breakout_signups,
        'morning_breakouts' : morning_breakouts,
        'afternoon_breakouts' : afternoon_breakouts,
     }

    return render_template("overview.html", conference_stats=conference_stats)

@app.route("/all_badges")
def all_badges():
    """
    Render the badge.html template with all visitors and their assigned breakout sessions.
    """
    return render_template("badge.html", data_quotes=data_quotes, visitors=visitors, breakout=breakout)

@app.route("/visitors_list")
def visitors_list():
    """
    Render the visitors_table.html template with all visitors.
    """
    return render_template("visitors_table.html", visitors=visitors, breakout=breakout)


@app.route("/badge/<int:page_num>")
def badge(page_num):
    """
    Render the badge.html template with a subset of visitors based on the specified page number.
    """
    items_per_page = 25
    start = (page_num - 1) * items_per_page
    end = start + items_per_page
    paged_visitors = visitors[start:end]
    return render_template("badge.html", data_quotes=data_quotes, visitors=paged_visitors, breakout=breakout)

@app.route("/empty_badge")
def empty_badge():
    """
    Render the empty_badge.html template with a subset of visitors based on the specified page number.
    """
    return render_template("empty_badge.html",)


@app.route("/visitor/<int:visitor_num>")
def visitor(visitor_num):
    """
    Render the badge.html template for a specific visitor
    """
    visitor = visitors[visitor_num-1:visitor_num]
    return render_template("badge.html", data_quotes=data_quotes, visitors=visitor, breakout=breakout)

@app.route("/fuzzy_email")
def fuzzy_mail():
    """
    Render the fuzzy_email.html template with a sorted list of visitors that have fuzzy email matches.
    """
    # Create a copy of the visitors list and add fuzzy email matches
    fuzzy_visitors = find_fuzzy_email_matches(visitors.copy(), breakout)
    # Sort the visitors list based on the fuzzy_email_score in descending order
    sorted_visitors = sorted(fuzzy_visitors, key=lambda v: v['fuzzy_email_score'], reverse=True)
    # Render the fuzzy_email.html template with the sorted visitors list
    return render_template("fuzzy_email.html", visitors=sorted_visitors, breakout=breakout)


@app.route("/unlinked_breakouts")
def unlinked_breakouts():
    """
    Render the unlinked_breakouts.html template with a list of breakout sessions that are not linked to any visitor.
    """

    unlinked_breakouts = {k:v for k,v in breakout.items() if k not in linked_breakout_emails}
    return render_template("unlinked_breakouts.html", linked_breakout_emails=linked_breakout_emails, unlinked_breakouts=unlinked_breakouts)



