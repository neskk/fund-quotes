from flask import Flask, Response, request, abort, render_template, jsonify, send_file
from flask_admin import Admin
from flask_admin.menu import MenuLink

from datetime import datetime, timedelta
import logging
import sys

from config import Config
from db import Database
from models import Fund, Quote, FundAdmin
from utils import configure_logging

log = logging.getLogger(__name__)

# https://flask.palletsprojects.com/en/2.0.x/api/
app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')

app.config['JSON_SORT_KEYS'] = False
# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

args = None
db = None


@app.before_request
def before_request():
    db.connect()


@app.after_request
def after_request(response):
    db.close()
    return response


# Flask webserver routes
@app.route('/')
def index():
    stats = {
        'Fund count': Fund.select().count(),
        'Quote count': Quote.select().count(),
    }
    data = Fund.get_all()
    return render_template('page.html', data=data, stats=stats)


@app.route('/chart-example')
def chart_example():
    return render_template('chart-example.html', data=None)


@app.route('/chart/<int:fund_id>')
def chart(fund_id):
    fund = Fund.get(fund_id)

    return render_template('chart.html', fund=fund)


@app.route('/quotes/<int:fund_id>')
def quotes(fund_id):
    # if not fund_id:
    #     abort(400)

    limit = int(request.args.get('limit', 100))

    # default_from = str(datetime.utcnow() - timedelta(days=30))
    # date_from = request.args.get('from', default_from)
    # date_from = datetime.strptime(date_from, '%d-%m-%Y').date()

    # default_to = str(datetime.utcnow())
    # date_to = request.args.get('to', default_to)
    # date_to = datetime.strptime(date_to, '%d-%m-%Y').date()

    if limit > 1000:
        limit = 1000

    data = []
    query = Quote.get_by_fund(fund_id).dicts()
    for quote in query:
        data.append(
            {
                'date': quote['date'].strftime('%Y-%m-%d'),
                'value': quote['value']
            }
        )

    return jsonify(data)


@app.route('/get_image')
def get_image():
    filepath = db.query('')

    return send_file(filepath, mimetype='image/jpeg')


def cleanup():
    """ Handle shutdown tasks """
    log.info('Shutting down...')


if __name__ == '__main__':
    try:
        args = Config.get_args()
        configure_logging(log, args.verbose, args.log_path, "-webserver")
        db = Database.get_db()

        admin = Admin(app, name='fund-quotes', template_mode='bootstrap3')
        # admin.add_link(MenuLink(name='Home Page', url='/'))
        admin.add_view(FundAdmin(Fund))

        log.info('Starting webserver...')
        # Note: Flask reloader runs two processes
        # https://stackoverflow.com/questions/25504149/why-does-running-the-flask-dev-server-run-itself-twice
        app.run(
            debug=True if args.verbose else False,
            host='0.0.0.0',
            port=5000,
            use_reloader=False)
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        log.exception(e)
    finally:
        cleanup()
        sys.exit()
