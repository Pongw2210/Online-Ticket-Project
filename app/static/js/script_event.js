function increaseTicket(ticketId) {
    let quantityInput = document.getElementById(`quantity-${ticketId}`);
    let stockEl = document.getElementById(`stock-${ticketId}`);

    // Lấy số vé còn lại hiện tại từ text
    let currentStock = parseInt(stockEl.textContent.replace(/\D/g, ''));

    // Lấy số lượng đã chọn hiện tại
    let currentQuantity = parseInt(quantityInput.value);

    if (currentStock > 0) {  // còn vé thì tăng
        quantityInput.value = currentQuantity + 1;
        // Cập nhật số vé còn lại (giảm đi 1)
        updateStock(ticketId, currentStock - 1);
        updateSummary();
    } else {
        alert('Bạn đã chọn tối đa số vé còn lại!');
    }
}

function decreaseTicket(ticketId) {
    let quantityInput = document.getElementById(`quantity-${ticketId}`);
    let stockEl = document.getElementById(`stock-${ticketId}`);

    let currentQuantity = parseInt(quantityInput.value);
    let currentStock = getCurrentStock(stockEl);

    if (currentQuantity > 0) {
        quantityInput.value = currentQuantity - 1;
        updateStock(ticketId, currentStock + 1);
        updateSummary();
    }
}

function manualTicketChange(ticketId) {
    let quantityInput = document.getElementById(`quantity-${ticketId}`);
    let stockEl = document.getElementById(`stock-${ticketId}`);

    // Lấy số vé còn lại thực tế (ví dụ: "Số vé còn lại: 50" -> 50)
    let currentStock = parseInt(stockEl.textContent.replace(/\D/g, ''));

    let enteredQuantity = parseInt(quantityInput.value);

    // Nếu nhập không hợp lệ hoặc âm, set về 0
    if (isNaN(enteredQuantity) || enteredQuantity < 0) {
        enteredQuantity = 0;
    }

    // Nếu nhập vượt quá số vé còn lại hiện tại, giới hạn lại
    if (enteredQuantity > currentStock) {
        alert(`Số vé tối đa bạn có thể chọn là ${currentStock}`);
        enteredQuantity = currentStock;
    }

    // Cập nhật input với giá trị hợp lệ
    quantityInput.value = enteredQuantity;

    // Cập nhật số vé còn lại: giảm số vé còn lại đi bằng số vé đã chọn mới
    updateStock(ticketId, currentStock - enteredQuantity);

    updateSummary();
}

function getCurrentStock(stockEl) {
    return parseInt(stockEl.textContent.replace(/\D/g, ''));
}

function updateStock(ticketId, newStock) {
    let stockEl = document.getElementById(`stock-${ticketId}`);
    stockEl.textContent = `Số vé còn lại: ${newStock}`;
}

let seatSelections = {};
let currentTicketId = null;
let maxSeats = 0;

function openSeatSelection(ticketId, eventId) {
    currentTicketId = ticketId;

    const qtyInput = document.getElementById(`quantity-${ticketId}`);
    maxSeats = parseInt(qtyInput.value) || 0;

    if (maxSeats === 0) {
        alert("Vui lòng chọn số lượng vé trước khi chọn ghế!");
        return;
    }

    fetch(`/api/seats/${eventId}`)
        .then(res => res.json())
        .then(data => {
            console.log(data);
            let preselectedSeats = (seatSelections[ticketId] || []).map(s => s.seat_code);
            renderSeatGrid(data, preselectedSeats);
            document.getElementById("seat-modal").style.display = "block";
        })
        .catch(err => {
            console.error("Lỗi tải ghế:", err);
            alert("Không thể tải danh sách ghế!");
        });
}

function renderSeatGrid(seats, preselectedSeats) {
    const seatGrid = document.getElementById("seat-grid");
    seatGrid.innerHTML = "";
    let selectedSeats = [...preselectedSeats];

    seats.forEach(seat => {
        const seatEl = document.createElement("div");
        seatEl.classList.add("seat");
        seatEl.innerText = seat.name;

        // Set data-id và data-code cho seat để dùng khi confirm
        seatEl.dataset.id = seat.id;       // id ghế trong DB
        seatEl.dataset.code = seat.name;   // mã ghế hiển thị

        if (seat.occupied) {
            seatEl.classList.add("occupied");
        } else {
            if (selectedSeats.includes(seat.name)) {
                seatEl.classList.add("selected");
            }
            seatEl.onclick = () => toggleSeat(seat.name, seatEl, selectedSeats);
        }

        seatGrid.appendChild(seatEl);
    });

    seatGrid.dataset.selectedSeats = JSON.stringify(selectedSeats);
}

function toggleSeat(seatNumber, seatElement, selectedSeats) {
    if (seatElement.classList.contains("occupied")) return;

    if (seatElement.classList.contains("selected")) {
        seatElement.classList.remove("selected");
        let index = selectedSeats.indexOf(seatNumber);
        if (index > -1) selectedSeats.splice(index, 1);
    } else {
        if (selectedSeats.length >= maxSeats) {
            alert(`Bạn chỉ được chọn tối đa ${maxSeats} ghế!`);
            return;
        }
        seatElement.classList.add("selected");
        selectedSeats.push(seatNumber);
    }

    document.getElementById("seat-grid").dataset.selectedSeats = JSON.stringify(selectedSeats);
}

function closeSeatSelection() {
    document.getElementById("seat-modal").style.display = "none";
}

function confirmSeatSelection() {
    let selectedSeats = Array.from(document.querySelectorAll(".seat.selected")).map(seatEl => ({
        seat_id: parseInt(seatEl.dataset.id),   // ID trong DB
        seat_code: seatEl.dataset.code          // Mã hiển thị
    }));

    seatSelections[currentTicketId] = selectedSeats;

    updateSummary();
    closeSeatSelection();
}

function updateSummary() {
    let summaryList = document.getElementById('summary-list');
    let totalEl = document.getElementById('summary-total');
    let continueBtn = document.getElementById('continue-btn');

    summaryList.innerHTML = '';

    let totalTickets = 0;
    let totalPrice = 0;

    document.querySelectorAll('.quantity-input').forEach(input => {
        let qty = parseInt(input.value) || 0;
        if (qty > 0) {
            let name = input.getAttribute('data-name');
            let price = parseInt(input.getAttribute('data-price'));
            let ticketId = input.getAttribute('data-ticket-id');
            let seats = seatSelections[ticketId] || [];
            let seatCodes = seats.map(s => s.seat_code).join(', ');
            let seatInfo = seatCodes ? ` [Ghế: ${seatCodes}]` : '';

            let li = document.createElement('li');
            li.textContent = `${name} x${qty} — ${formatPrice(price * qty)}${seatInfo}`;
            summaryList.appendChild(li);

            totalTickets += qty;
            totalPrice += price * qty;
        }
    });

    totalEl.innerHTML = `<strong>🎟 x${totalTickets}</strong>`;

    if (continueBtn) {
        continueBtn.textContent = `Tiếp tục - Tổng: ${formatPrice(totalPrice)}`;
    }
}

function goToCheckout() {
    let continueBtn = document.getElementById('continue-btn');
    let eventId = continueBtn.getAttribute('data-event-id');

    let tickets = [];
    document.querySelectorAll('.quantity-input').forEach(input => {
        let qty = parseInt(input.value) || 0;
        if (qty > 0) {
            let ticketId = input.getAttribute('data-ticket-id');
            let selectedSeats = seatSelections[ticketId] || [];

            tickets.push({
                id: ticketId,
                name: input.getAttribute('data-name'),
                price: parseInt(input.getAttribute('data-price')),
                quantity: qty,
                seats: selectedSeats
            });
        }
    });

    if (tickets.length === 0) {
        alert('Vui lòng chọn ít nhất một vé để tiếp tục.');
        return;
    }

    sessionStorage.setItem('checkoutEventId', eventId);
    sessionStorage.setItem('checkoutTickets', JSON.stringify(tickets));

    // Có thể thêm điều hướng trang thanh toán ở đây nếu cần
    // window.location.href = '/checkout';
}

document.addEventListener('DOMContentLoaded', () => {
    let tickets = JSON.parse(sessionStorage.getItem('checkoutTickets')) || [];
    let summaryDiv = document.getElementById('ticket-summary');
    let subtotalEl = document.getElementById('subtotal');
    let totalEl = document.getElementById('total-price');

    if (tickets.length === 0) {
        summaryDiv.innerHTML = '<div class="muted">Chưa có vé nào được chọn</div>';
        subtotalEl.textContent = '0 đ';
        totalEl.textContent = '0 đ';
        return;
    }

    summaryDiv.innerHTML = '';
    let totalPrice = 0;

    tickets.forEach(ticket => {
        let itemPrice = parseInt(ticket.price) * ticket.quantity;
        totalPrice += itemPrice;

        let seatCodes = ticket.seats.map(s => s.seat_code).join(', ');

        summaryDiv.innerHTML += `
            <div class="summary-row">
                <div>${ticket.name} ${seatCodes ? '(' + seatCodes + ')' : ''}</div>
                <div>${ticket.quantity}</div>
            </div>
            <div class="summary-row muted">
                <div>Giá vé</div>
                <div>${itemPrice.toLocaleString()} đ</div>
            </div>
        `;
    });

    subtotalEl.textContent = totalPrice.toLocaleString() + ' đ';
    totalEl.textContent = totalPrice.toLocaleString() + ' đ';
});

function formatPrice(value) {
    return value.toLocaleString('vi-VN') + ' đ';
}



let minutes = 14; let seconds = 30;
const minEl = document.getElementById('cd-min');
const secEl = document.getElementById('cd-sec');
function tick(){
  if(seconds===0){
    if(minutes===0){ clearInterval(timer); return; }
    minutes--; seconds=59;
  } else seconds--;
  minEl.textContent = String(minutes).padStart(2,'0');
  secEl.textContent = String(seconds).padStart(2,'0');
}
const timer = setInterval(tick,1000);

function handlePayment() {
    // Lấy phương thức thanh toán đang được chọn
    const selectedPayMethod = document.querySelector('input[name="pay"]:checked').value;

    if (selectedPayMethod === "momo") {
        payment_momo();
    } else if (selectedPayMethod === "vnpay") {
        payment_vnpay();
    } else {
        alert("Vui lòng chọn phương thức thanh toán.");
    }
}

function payment_momo() {
    let payBtn = document.getElementById("payBtn2");
    payBtn.disabled = true;

    let tickets = JSON.parse(sessionStorage.getItem('checkoutTickets')) || [];
    console.log(sessionStorage.getItem('checkoutTickets'));
    if (tickets.length === 0) {
        alert("Không có vé để thanh toán");
        payBtn.disabled = false;
        return;
    }

    let totalPrice = tickets.reduce((sum, ticket) => sum + (parseInt(ticket.price) * ticket.quantity), 0);

    fetch("/booking/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            tickets: tickets,
            totalPrice: totalPrice,
            eventId: sessionStorage.getItem('checkoutEventId'),
        }),
    })
    .then(res => res.json())
    .then(bookingData => {
        if (!bookingData.success) {
            alert("Tạo booking thất bại: " + bookingData.message);
            payBtn.disabled = false;
            throw new Error("Booking failed");
        }
        return fetch("/payment/momo", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                amount: totalPrice,
                orderId: "order_" + bookingData.bookingId,
                orderInfo: `Thanh toán vé sự kiện ${sessionStorage.getItem('checkoutEventId')}`,
            }),
        });
    })
    .then(res => res.json())
    .then(paymentData => {
        if (paymentData.payUrl) {
            window.location.href = paymentData.payUrl;
        } else {
            alert("Không tạo được link thanh toán!");
            payBtn.disabled = false;
        }
    })
    .catch(err => {
        console.error(err);
        if (err.message !== "Booking failed") {
            alert("Đã xảy ra lỗi, vui lòng thử lại.");
            payBtn.disabled = false;
        }
    });
}

function payment_vnpay() {
    let payBtn = document.getElementById("payBtn2");
    payBtn.disabled = true;

    let tickets = JSON.parse(sessionStorage.getItem('checkoutTickets')) || [];
    if (tickets.length === 0) {
        alert("Không có vé để thanh toán");
        payBtn.disabled = false;
        return;
    }

    let totalPrice = tickets.reduce((sum, ticket) => sum + (parseInt(ticket.price) * ticket.quantity), 0);

    // Tạo booking trước
    fetch("/booking/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            tickets: tickets,
            totalPrice: totalPrice,
            eventId: sessionStorage.getItem('checkoutEventId'),
        }),
    })
    .then(res => res.json())
    .then(bookingData => {
        if (!bookingData.success) {
            alert("Tạo booking thất bại: " + bookingData.message);
            payBtn.disabled = false;
            throw new Error("Booking failed");
        }

        // Tạo yêu cầu thanh toán VNPAY với orderId theo bookingId
        return fetch("/payment/vnpay", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                amount: totalPrice,
                orderId: "order_" + bookingData.bookingId,
                orderInfo: `Thanh toán vé sự kiện ${sessionStorage.getItem('checkoutEventId')}`,
            }),
        });
    })
    .then(res => res.json())
    .then(paymentData => {
        if (paymentData.payUrl) {
            window.location.href = paymentData.payUrl;
        } else {
            alert("Không tạo được link thanh toán!");
            payBtn.disabled = false;
        }
    })
    .catch(err => {
        console.error(err);
        if (err.message !== "Booking failed") {
            alert("Đã xảy ra lỗi, vui lòng thử lại.");
            payBtn.disabled = false;
        }
    });
}




