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
    // Ghế đã bị chọn cho vé khác
    for (let ticketId in seatSelections) {
        if (ticketId != currentTicketId) {
            if (seatSelections[ticketId].some(s => s.seat_code === seatNumber)) {
                alert(`Ghế ${seatNumber} đã được chọn cho vé khác!`);
                return;
            }
        }
    }

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

    // Cập nhật dữ liệu ghế đã chọn cho vé hiện tại
    document.getElementById("seat-grid").dataset.selectedSeats = JSON.stringify(selectedSeats);
}

function closeSeatSelection() {
    document.getElementById("seat-modal").style.display = "none";
}

function confirmSeatSelection() {
    let selectedSeats = Array.from(document.querySelectorAll(".seat.selected")).map(seatEl => ({
        seat_id: parseInt(seatEl.dataset.id),
        seat_code: seatEl.dataset.code
    }));

    if (selectedSeats.length !== maxSeats) {
        alert(`Bạn phải chọn đủ ${maxSeats} ghế cho vé này!`);
        return; // không cho đóng modal nếu chưa đủ
    }

    // Lưu ghế đã chọn cho vé hiện tại
    seatSelections[currentTicketId] = selectedSeats;

    updateSummary(); // Cập nhật thông tin tóm tắt vé và ghế
    closeSeatSelection();
}

function goToCheckout() {
    let continueBtn = document.getElementById('continue-btn');
    let eventId = continueBtn.getAttribute('data-event-id');

    let tickets = [];
    let hasSeatError = false;

    document.querySelectorAll('.quantity-input').forEach(input => {
        let qty = parseInt(input.value) || 0;
        if (qty > 0) {
            let ticketId = input.getAttribute('data-ticket-id');
            let selectedSeats = seatSelections[ticketId] || [];

            let hasSeatButton = document.querySelector(`.select-seat-btn[onclick*="${ticketId}"]`);
            if (hasSeatButton && selectedSeats.length < qty) {
                hasSeatError = true;
            }

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

    if (hasSeatError) {
        alert('Vui lòng chọn đủ số ghế cho các loại vé cần chọn ghế.');
        return;
    }

    sessionStorage.setItem('checkoutEventId', eventId);
    sessionStorage.setItem('checkoutTickets', JSON.stringify(tickets));

    let subtotal = tickets.reduce((sum, t) => sum + (t.price * t.quantity), 0);

    fetch("/booking/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            tickets: tickets,
            totalPrice: subtotal,
            eventId: eventId,
        }),
    })
    .then(res => res.json())
    .then(bookingData => {
        if (!bookingData.success) {
            alert("Tạo booking thất bại: " + bookingData.message);
            throw new Error("Booking failed");
        }

        // Lưu bookingId để thanh toán sau
        sessionStorage.setItem('bookingId', bookingData.bookingId);

        window.location.href = `/pay-ticket/${eventId}`;
    })
    .catch(err => {
        console.error(err);
        alert("Có lỗi khi tạo booking, vui lòng thử lại.");
    });
}

document.addEventListener('DOMContentLoaded', () => {
    let tickets = JSON.parse(sessionStorage.getItem('checkoutTickets')) || [];
    let appliedVoucher = JSON.parse(sessionStorage.getItem('appliedVoucher')) || null;

    let summaryDiv = document.getElementById('ticket-summary');
    let subtotalEl = document.getElementById('subtotal');
    let totalEl = document.getElementById('total-price');
    let voucherNameEl = document.getElementById('voucher-name'); // element hiển thị voucher

    if (!summaryDiv || !subtotalEl || !totalEl) return;

    if (tickets.length === 0) {
        summaryDiv.innerHTML = '<div class="muted">Chưa có vé nào được chọn</div>';
        subtotalEl.textContent = '0 đ';
        totalEl.textContent = '0 đ';
        if (voucherNameEl) voucherNameEl.textContent = '-';
        return;
    }

    summaryDiv.innerHTML = '';
    let subtotal = 0;

    tickets.forEach(ticket => {
        let itemPrice = parseInt(ticket.price) * ticket.quantity;
        subtotal += itemPrice;

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

    subtotalEl.textContent = subtotal.toLocaleString() + ' đ';

    // Xử lý voucher
    let discount = 0;
    if (appliedVoucher) {
        if (appliedVoucher.discount_type === "PHAN_TRAM") {
            discount = subtotal * (appliedVoucher.discount_value / 100);
        } else {
            discount = appliedVoucher.discount_value;
        }
        discount = Math.min(discount, subtotal);

        if (voucherNameEl) {
            voucherNameEl.textContent = `${appliedVoucher.code} (-${discount.toLocaleString()} đ)`;
        }
    } else {
        if (voucherNameEl) voucherNameEl.textContent = 'Không áp dụng';
    }

    let total = subtotal - discount;
    totalEl.textContent = total.toLocaleString() + ' đ';

    sessionStorage.setItem('checkoutTotal', total);
});

let minutes = 1;
let seconds = 0;

const minEl = document.getElementById("cd-min");
const secEl = document.getElementById("cd-sec");

function updateDisplay() {
  if (minEl && secEl) {
    minEl.textContent = String(minutes).padStart(2, "0");
    secEl.textContent = String(seconds).padStart(2, "0");
  }
}

function deleteBooking() {
  const bookingId = sessionStorage.getItem("bookingId");
  if (!bookingId) return; // nếu không có booking thì thôi

  fetch("/booking/delete", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ bookingId: bookingId })
  })
    .then((res) => res.json())
    .then((data) => {
      console.log("Booking deleted:", data);
      alert("Hết thời gian giữ vé. Booking đã bị hủy.");
      window.location.href = "/";
    })
    .catch((err) => {
      console.error("Error deleting booking:", err);
      alert("Có lỗi xảy ra khi xóa booking!");
      window.location.href = "/";
    });
}

function tick() {
  if (seconds === 0) {
    if (minutes === 0) {
      clearInterval(timer);
      deleteBooking();
      return;
    }
    minutes--;
    seconds = 59;
  } else {
    seconds--;
  }
  updateDisplay();
}

if (minEl && secEl && sessionStorage.getItem("bookingId")) {
  updateDisplay();
  var timer = setInterval(tick, 1000);
}


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
    if (tickets.length === 0) {
        alert("Không có vé để thanh toán");
        payBtn.disabled = false;
        return;
    }

    let totalPrice = Math.round(Number(sessionStorage.getItem('checkoutTotal')) || 0);
    let bookingId = sessionStorage.getItem('bookingId');
    let orderId = `order_${bookingId}_${Date.now()}`;
    let orderInfo = `Thanh toán vé sự kiện ${sessionStorage.getItem('checkoutEventId')}`;

    // Voucher áp dụng
    let appliedVoucher = JSON.parse(sessionStorage.getItem('appliedVoucher')) || null;
    let voucherId = appliedVoucher ? appliedVoucher.id : null;
//
//    console.log("Total price:", totalPrice);
//    console.log("Booking ID:", bookingId);
//    console.log("Order ID:", orderId);
//    console.log("Order info:", orderInfo);
//    console.log("Voucher applied:", appliedVoucher);

    if (voucherId) {
        fetch("/booking/apply-voucher", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ bookingId, voucherId })
        })
        .then(res => res.json())
        .then(dataVoucher => {
            console.log("Voucher save response:", dataVoucher);
            return fetch("/payment/momo", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    amount: totalPrice,
                    bookingId,
                    orderId,
                    orderInfo
                })
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
            alert("Đã xảy ra lỗi, vui lòng thử lại.");
            payBtn.disabled = false;
        });
    } else {
        fetch("/payment/momo", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                amount: totalPrice,
                bookingId,
                orderId,
                orderInfo
            })
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
            alert("Đã xảy ra lỗi, vui lòng thử lại.");
            payBtn.disabled = false;
        });
    }
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

    let totalPrice = Math.round(Number(sessionStorage.getItem('checkoutTotal')) || 0);
    let bookingId = sessionStorage.getItem('bookingId');
    let orderId = `order_${bookingId}_${Date.now()}`;
    let orderInfo = `Thanh toán vé sự kiện ${sessionStorage.getItem('checkoutEventId')}`;

    // Voucher áp dụng
    let appliedVoucher = JSON.parse(sessionStorage.getItem('appliedVoucher')) || null;
    let voucherId = appliedVoucher ? appliedVoucher.id : null;

    if (voucherId) {
        fetch("/booking/apply-voucher", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ bookingId, voucherId })
        })
        .then(res => res.json())
        .then(dataVoucher => {
            console.log("Voucher save response:", dataVoucher);
            return fetch("/payment/vnpay", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    amount: totalPrice,
                    bookingId,
                    orderId,
                    orderInfo
                })
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
            alert("Đã xảy ra lỗi, vui lòng thử lại.");
            payBtn.disabled = false;
        });
    } else {
        fetch("/payment/vnpay", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                amount: totalPrice,
                bookingId,
                orderId,
                orderInfo
            })
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
            alert("Đã xảy ra lỗi, vui lòng thử lại.");
            payBtn.disabled = false;
        });
    }
}

function closeVoucherModal(){
    document.getElementById('voucherModal').style.display = 'none';
}

function showVoucherModal(eventId) {
    // Hiển thị modal
    const modal = document.getElementById("voucherModal");
    modal.style.display = "flex";

    // Xóa danh sách cũ
    const list = document.getElementById("voucherList");
    list.innerHTML = "";

    // Lấy tickets đã chọn trong giỏ hàng
    let tickets = JSON.parse(sessionStorage.getItem('checkoutTickets')) || [];

    // Gọi API lấy voucher, gửi kèm danh sách vé
    fetch(`/api/vouchers/${eventId}`, {
        method: "POST",  // đổi sang POST
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ tickets: tickets })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert("Lỗi load voucher: " + data.error);
            return;
        }

        data.forEach(v => {
            const li = document.createElement("li");
            li.textContent = `${v.code} - ${v.discount_value}${v.discount_type === "PHAN_TRAM" ? "%" : "đ"}`;
            li.onclick = () => applyVoucher(v);
            list.appendChild(li);
        });
    })
    .catch(err => console.error("Lỗi fetch voucher:", err));
}

function applyVoucher(voucher) {
    appliedVoucher = voucher;

    // Lưu voucher vào sessionStorage để các trang / lần reload còn nhớ
    sessionStorage.setItem('appliedVoucher', JSON.stringify(voucher));

    // Hiển thị voucher trên nút
    const voucherBtn = document.querySelector('.voucher .btn');
    if (voucherBtn) {
        voucherBtn.textContent = `Voucher: ${voucher.code} - ${voucher.discount_value}${voucher.discount_type === "PHAN_TRAM" ? "%" : "đ"}`;
    }

    closeVoucherModal();
    window.location.reload();
}

function updateSummary() {
    const summaryList = document.getElementById('summary-list');
    const totalEl = document.getElementById('summary-total');
    const continueBtn = document.getElementById('continue-btn');

    if (summaryList) summaryList.innerHTML = '';

    let totalTickets = 0;
    let totalPrice = 0;

    // Lấy tất cả input số lượng (đảm bảo class .quantity-input có)
    document.querySelectorAll('.quantity-input').forEach(input => {
        let qty = parseInt(input.value) || 0;
        if (qty > 0) {
            let name = input.getAttribute('data-name');
            let price = parseInt(input.getAttribute('data-price')) || 0;
            let ticketId = input.getAttribute('data-ticket-id');
            let seats = seatSelections[ticketId] || [];
            let seatCodes = seats.map(s => s.seat_code).join(', ');
            let seatInfo = seatCodes ? ` [Ghế: ${seatCodes}]` : '';

            if (summaryList) {
                const li = document.createElement('li');
                li.textContent = `${name} x${qty} — ${formatPrice(price * qty)}${seatInfo}`;
                summaryList.appendChild(li);
            }

            totalTickets += qty;
            totalPrice += price * qty;
        }
    });

    if (totalEl) {
        totalEl.innerHTML = `<strong>🎟 x${totalTickets}</strong> — Tổng: ${formatPrice(totalPrice)}`;
    }

    if (continueBtn) {
        continueBtn.textContent = `Tiếp tục - Tổng: ${formatPrice(totalPrice)}`;
    }
}


//document.addEventListener('DOMContentLoaded', updateSummary);
// Format giá
function formatPrice(value) {
    return value.toLocaleString('vi-VN') + ' đ';
}

document.addEventListener("DOMContentLoaded", () => {
    const filterBtn = document.querySelector(".btn-filter");
    const filterPanel = document.querySelector(".filter-panel");

    if (filterBtn && filterPanel) {
        filterBtn.addEventListener("click", () => {
            filterPanel.classList.toggle("active");
        });
    }
});

