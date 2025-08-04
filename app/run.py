from app import create_app
from app.data.models import EventRejectionLog

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        rejection_log = EventRejectionLog.query.filter_by(event_id=3).first()
        print(rejection_log.reason)
    app.run(debug=True)

