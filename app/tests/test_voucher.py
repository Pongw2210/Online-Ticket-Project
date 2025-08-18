from app import create_app, db
from app.data.models import Voucher, TicketVoucher

app = create_app()

def test_voucher(event_id, ticket_type_ids):
    with app.app_context():
        vouchers = (
            db.session.query(Voucher)
            .filter(Voucher.event_id == event_id)
            .all()
        )

        result = []
        for v in vouchers:
            if v.apply_all:
                result.append(v.code)
            else:
                ticket_ids = [tv.ticket_type_id for tv in v.tickets]

                if any(t in ticket_ids for t in ticket_type_ids):
                    result.append(v.code)

        print(f"Voucher áp dụng cho event {event_id}, tickets {ticket_type_ids}:")
        print(result)
        return result

# ví dụ test
if __name__ == "__main__":
    test_voucher(3, [2, 5])
