document.addEventListener('DOMContentLoaded', function () {
    const increaseButtons = document.querySelectorAll('.increase');
    const decreaseButtons = document.querySelectorAll('.decrease');
    const summaryList = document.getElementById('summary-list');
    const summaryTotal = document.getElementById('summary-total');
    const continueBtn = document.getElementById('continue-btn');

    function updateSummary() {
        const quantities = document.querySelectorAll('.quantity-input');
        let total = 0;
        let summaryHTML = '';

        quantities.forEach(input => {
            const quantity = parseInt(input.value);
            const name = input.dataset.name;
            const price = parseFloat(input.dataset.price);

            if (quantity > 0) {
                total += quantity;
                summaryHTML += `<li>${name}: ${price.toLocaleString()}đ x${quantity}</li>`;
            }
        });

        summaryList.innerHTML = summaryHTML || '<li>Chưa chọn vé nào</li>';
        summaryTotal.innerHTML = `<strong>🎟 x${total}</strong>`;
    }

    increaseButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const ticketId = btn.dataset.ticketId;
            const input = document.querySelector(`.quantity-input[data-ticket-id="${ticketId}"]`);
            input.value = parseInt(input.value) + 1;
            updateSummary();
        });
    });

    decreaseButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const ticketId = btn.dataset.ticketId;
            const input = document.querySelector(`.quantity-input[data-ticket-id="${ticketId}"]`);
            input.value = Math.max(0, parseInt(input.value) - 1);
            updateSummary();
        });
    });

    if (continueBtn) {
        continueBtn.addEventListener('click', function (e) {
            e.preventDefault();

            const quantities = document.querySelectorAll('.quantity-input');
            let tickets = [];
            let ticketMap = {};  // Để lưu vào localStorage

            quantities.forEach(input => {
                const quantity = parseInt(input.value);
                const ticketName = input.dataset.name;  // Sử dụng tên vé trực tiếp từ database

                if (quantity > 0) {
                    tickets.push({
                        id: parseInt(input.dataset.ticketId),
                        quantity: quantity
                    });

                    ticketMap[ticketName] = quantity;
                }
            });

            if (tickets.length === 0) {
                alert("Vui lòng chọn ít nhất 1 vé.");
                return;
            }

            // Lưu vào localStorage để sử dụng ở trang chọn ghế
            localStorage.setItem("selectedTickets", JSON.stringify(ticketMap));
            console.log("Saved to localStorage:", ticketMap); // Debug log

            const eventId = parseInt(continueBtn.dataset.eventId);

            // Gửi vé lên server
            fetch('/process-order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ tickets: tickets })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = `/select-seats/${eventId}`;
                } else {
                    if (data.message && data.message.includes('đăng nhập')) {
                        // Nếu lỗi đăng nhập, chuyển hướng đến trang đăng nhập
                        alert("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.");
                        window.location.href = '/login';
                    } else {
                        alert(data.message || "Đặt vé thất bại.");
                    }
                }
            })
            .catch(err => {
                alert("Lỗi kết nối đến server.");
                console.error(err);
            });
        });
    }

    updateSummary(); // Cập nhật ban đầu
});
