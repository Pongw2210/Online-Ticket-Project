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
        return;
    }

    // Lưu dữ liệu vào sessionStorage (hoặc localStorage) để trang thanh toán dùng
    sessionStorage.setItem('checkoutEventId', eventId);
    sessionStorage.setItem('checkoutTickets', JSON.stringify(tickets));

}
