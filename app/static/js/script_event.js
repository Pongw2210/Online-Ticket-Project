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

function formatPrice(price) {
    return new Intl.NumberFormat('vi-VN').format(price) + 'đ';
}

function updateSummary() {
    let summaryList = document.getElementById('summary-list');
    let totalEl = document.getElementById('summary-total');
    let continueBtn = document.getElementById('continue-btn');

    summaryList.innerHTML = '';

    let totalTickets = 0;
    let totalPrice = 0;
    let ticketInputs = document.querySelectorAll('.quantity-input');

    ticketInputs.forEach(input => {
        let qty = parseInt(input.value);
        if (qty > 0) {
            let name = input.getAttribute('data-name');
            let price = parseInt(input.getAttribute('data-price'));
            let li = document.createElement('li');
            li.textContent = `${name} x${qty} — ${formatPrice(price * qty)}`;
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

    // Thu thập các vé đã chọn
    let tickets = [];
    document.querySelectorAll('.quantity-input').forEach(input => {
        let qty = parseInt(input.value);
        if (qty > 0) {
            tickets.push({
                id: input.getAttribute('data-ticket-id'),
                name: input.getAttribute('data-name'),
                price: input.getAttribute('data-price'),
                quantity: qty
            });
        }
    });

    if (tickets.length === 0) {
        alert('Vui lòng chọn ít nhất một vé để tiếp tục.');
        event.preventDefault();
        return;
    }

    // Lưu dữ liệu vào sessionStorage (hoặc localStorage) để trang thanh toán dùng
    sessionStorage.setItem('checkoutEventId', eventId);
    sessionStorage.setItem('checkoutTickets', JSON.stringify(tickets));
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

        summaryDiv.innerHTML += `
            <div class="summary-row">
                <div>${ticket.name}</div>
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

function payment_vnpay(){

}

