function previewImage(event) {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      const previewDiv = document.getElementById('upload-preview');
      previewDiv.innerHTML = `<img src="${e.target.result}" style="max-width: 100%; max-height: 100%; border-radius: 10px;">`;
    };
    reader.readAsDataURL(file);
  }
}

function handleEventFormatChange(){
    const selectedFormat = document.querySelector('input[name = "event_format"]:checked').nextSibling.textContent.trim();
    const offForm = document.querySelector(".form-info-event-offline")
    const onForm = document.querySelector(".form-info-event-online")

    if (selectedFormat.includes("Online")){
        offForm.style.display = "none";
        onForm.style.display = "block";
    }
    else{
        onForm.style.display = "none";
        offForm.style.display = "block";
    }
}
document.addEventListener("DOMContentLoaded", handleEventFormatChange);

function showError(input, message) {
    input.classList.add('error');
    let errorDiv = input.parentElement.querySelector('.form-error');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'form-error';
        input.parentElement.appendChild(errorDiv);
    }
    errorDiv.innerText = message;
}

function clearErrors() {
    document.querySelectorAll('.form-error').forEach(e => e.remove());
    document.querySelectorAll('.error').forEach(e => e.classList.remove('error'));
}

function validateStep1() {
    clearErrors();

    let valid = true;

    const imageInput = document.getElementById("imageUpload");
    const preview = document.getElementById("upload-preview");
    const hasFile = imageInput.files && imageInput.files.length > 0;
    const hasPreviewImage = preview.querySelector("img");

    if (!hasFile && !hasPreviewImage) {
        showError(preview, "Vui lòng chọn ảnh sự kiện.");
        valid = false;
    }

    const nameEvent = document.getElementById("name_event");
    if (!nameEvent.value.trim()) {
        showError(nameEvent, "Tên sự kiện không được để trống.");
        valid = false;
    }

    const eventFormat = document.querySelector('input[name="event_format"]:checked').value;

    if (eventFormat === "offline") {
        const venueName = document.getElementById("venue_name");
        const address = document.getElementById("address");
        if (!venueName.value.trim()) {
            showError(venueName, "Vui lòng nhập tên địa điểm.");
            valid = false;
        }
        if (!address.value.trim()) {
            showError(address, "Vui lòng nhập địa chỉ cụ thể.");
            valid = false;
        }
    } else if (eventFormat === "online") {
        const livestreamUrl = document.getElementById("livestream_url");
        if (!livestreamUrl.value.trim()) {
            showError(livestreamUrl, "Vui lòng nhập link tham gia sự kiện.");
            valid = false;
        }
    }

    const eventType = document.getElementById("event_type");
    if (!eventType.value) {
        showError(eventType, "Vui lòng chọn thể loại sự kiện.");
        valid = false;
    }

    const fields = [
        { id: "description", name: "Thông tin sự kiện" },
        { id: "rules", name: "Luật lệ sự kiện" },
        { id: "performers", name: "Thông tin người biểu diễn" },
        { id: "organizer", name: "Thông tin người tổ chức" }
    ];

    for (let field of fields) {
        const el = document.getElementById(field.id);
        if (!el.value.trim()) {
            showError(el, `${field.name} không được để trống.`);
            valid = false;
        }
    }

    return valid;
}

function validateStep2() {
    clearErrors();
    let valid = true;

    const startTime = document.getElementById("start_time");
    const endTime = document.getElementById("end_time");

    if (!startTime.value) {
        showError(startTime, "Vui lòng chọn ngày và thời gian bắt đầu.");
        valid = false;
    }

    if (!endTime.value) {
        showError(endTime, "Vui lòng chọn ngày và thời gian kết thúc.");
        valid = false;
    }

    if (startTime.value >= endTime.value) {
        showError(endTime, "Vui lòng thời gian bắt đầu trước thời gian kết thúc.");
        valid = false;
    }

    const ticketRows = document.querySelectorAll("#ticket-types .ticket-type");

    if (ticketRows.length === 0) {
        showToast("Vui lòng thêm ít nhất 1 loại vé.");
        valid = false;
    }

    ticketRows.forEach((row, index) => {
        const name = row.querySelector(".ticket_name");
        const price = row.querySelector(".ticket_price");
        const quantity = row.querySelector(".ticket_quantity");

        if (!name || !name.value.trim()) {
            showError(name, `Tên vé #${index + 1} không được để trống.`);
            valid = false;
        }

        if (!price || price.value === '' || parseInt(price.value) < 0) {
            showError(price, `Giá vé #${index + 1} không hợp lệ.`);
            valid = false;
        }

        if (!quantity || quantity.value === '' || parseInt(quantity.value) < 1) {
            showError(quantity, `Số lượng vé #${index + 1} phải từ 1 trở lên.`);
            valid = false;
        }
    });

    return valid;
}

function goToNextStep() {
    const allSections = document.querySelectorAll('.step-section');
    const stepsProgress = document.querySelectorAll('.step-progress .step');
    const btnNext = document.querySelector('.btn-next');

    const currentIndex = Array.from(allSections).findIndex(el => el.classList.contains('active'));

    if (currentIndex === 0 && !validateStep1()) return;
    if (currentIndex === 1 && !validateStep2()) return;

    // Nếu chuyển từ bước 2 sang bước 3 => load vé
    if (currentIndex === 1) {
        loadTicketTypesToStep3();
    }

    if (currentIndex < allSections.length - 1) {
        allSections[currentIndex].classList.remove('active');
        allSections[currentIndex + 1].classList.add('active');

        stepsProgress.forEach((step, i) => {
            if (i <= currentIndex + 1) step.classList.add('active');
            else step.classList.remove('active');
        });

        if (currentIndex + 1 === allSections.length - 1) {
            btnNext.innerText = 'Lưu';
            btnNext.onclick = submitEventForm;
        } else {
            btnNext.innerText = 'Tiếp tục';
            btnNext.onclick = goToNextStep;
        }
    }
}

function goToPrevStep() {
    const allSteps = document.querySelectorAll('.step-section');
    const stepsProgress = document.querySelectorAll('.step-progress .step');
    const btnNext = document.querySelector('.btn-next');

    const currentIndex = Array.from(allSteps).findIndex(el => el.classList.contains('active'));

    if (currentIndex > 0) {
        allSteps[currentIndex].classList.remove('active');
        allSteps[currentIndex - 1].classList.add('active');

        stepsProgress.forEach((step, i) => {
            if (i <= currentIndex - 1) step.classList.add('active');
            else step.classList.remove('active');
        });

        // Reset nút Next
        if (currentIndex - 1 === allSteps.length - 1) {
            btnNext.innerText = 'Lưu';
            btnNext.onclick = submitEventForm;
        } else {
            btnNext.innerText = 'Tiếp tục';
            btnNext.onclick = goToNextStep;
        }
    }
}

function addTicketType() {
    const container = document.getElementById("ticket-types");

    const newTicket = document.createElement("div");
    newTicket.classList.add("ticket-type", "form-group", "form-row");

    newTicket.innerHTML = `
        <div>
            <label class="required-label-ticket"><span class="text-danger">*</span> Tên vé</label>
            <input type="text" class="ticket_name" placeholder="Ví dụ: Vé thường">
        </div>
        <div>
            <label class="required-label-ticket"><span class="text-danger">*</span> Giá vé(VNĐ)</label>
            <input type="number" class="ticket_price" min="0" placeholder="100000">
        </div>
        <div>
           <label class="required-label-ticket"><span class="text-danger">*</span> Số lượng</label>
            <input type="number" class="ticket_quantity" min="1" placeholder="50">
        </div>
        <div class="requires-seat-container" style="display:none; align-self:center; padding-left:10px;">
            <label  style="color: #000000 !important;">
                <input type="checkbox" class="requires_seat" required>
                Yêu cầu chọn ghế
            </label>
        </div>

        <div>
            <label class="required-label-ticket">
                <span class="text-danger">*</span> Lợi ích
            </label>
            <input type="text" class="ticket_benefits" placeholder="Hãy nhập với cấu trúc lợi ích 1 | lợi ích 2">
        </div>

        <div>
            <button type="button" class="btn btn-danger remove-ticket" onclick="this.parentElement.parentElement.remove()">X</button>
        </div>
    `;

    container.appendChild(newTicket);

    // Cập nhật lại trạng thái checkbox "Yêu cầu chọn ghế" theo has_seat
    toggleRequiresSeatCheckbox();
}

function showToast(message, duration = 3000) {
    const container = document.getElementById("toast-container");

    const toast = document.createElement("div");
    toast.innerText = message;
    toast.style.background = "#333";
    toast.style.color = "#fff";
    toast.style.padding = "12px 20px";
    toast.style.marginTop = "10px";
    toast.style.borderRadius = "8px";
    toast.style.boxShadow = "0 4px 8px rgba(0,0,0,0.2)";
    toast.style.fontSize = "14px";
    toast.style.animation = "fadeInOut 0.5s ease";

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 500);
    }, duration);
}

function submitEventForm() {
    const formData = new FormData();

    // === Ảnh sự kiện ===
    const imageInput = document.getElementById("imageUpload");
    const previewImage = document.getElementById("preview-img");

    if (imageInput.files.length > 0) {
        formData.append("image", imageInput.files[0]); // ảnh mới
    } else if (previewImage && previewImage.src) {
        formData.append("existing_image_url", previewImage.src); // giữ ảnh cũ
    }

    // === Thông tin cơ bản ===
    formData.append("name_event", document.getElementById("name_event").value);
    formData.append("event_format", document.querySelector('input[name="event_format"]:checked')?.value);
    formData.append("event_type", document.getElementById("event_type").value);
    formData.append("description", document.getElementById("description").value);
    formData.append("rules", document.getElementById("rules").value);
    formData.append("performers", document.getElementById("performers").value);
    formData.append("organizer", document.getElementById("organizer").value);
    formData.append("start_time", document.getElementById("start_time").value);
    formData.append("end_time", document.getElementById("end_time").value);

    const format = document.querySelector('input[name="event_format"]:checked')?.value;
    if (format === "offline") {
        formData.append("venue_name", document.getElementById("venue_name").value);
        formData.append("address", document.getElementById("address").value);
    } else {
        formData.append("livestream_url", document.getElementById("livestream_url").value);
    }

    // === Ghế ngồi ===
    const hasSeatCheckbox = document.getElementById("has_seat");
    formData.append("has_seat", hasSeatCheckbox && hasSeatCheckbox.checked ? "true" : "false");

    if (hasSeatCheckbox && hasSeatCheckbox.checked) {
        const numRows = document.getElementById("num_rows")?.value || "";
        const seatsPerRow = document.getElementById("seats_per_row")?.value || "";
        formData.append("num_rows", numRows);
        formData.append("seats_per_row", seatsPerRow);
    }

    // === Vé ===
    const ticketRows = document.querySelectorAll("#ticket-types .ticket-type");
    const tickets = [];
    ticketRows.forEach(row => {
        tickets.push({
            name: row.querySelector(".ticket_name")?.value || "",
            price: row.querySelector(".ticket_price")?.value || "",
            quantity: row.querySelector(".ticket_quantity")?.value || "",
            requires_seat: row.querySelector(".requires_seat") ? row.querySelector(".requires_seat").checked : false,
            benefits: row.querySelector(".ticket_benefits")?.value || "",
        });
    });
    formData.append("tickets", JSON.stringify(tickets));

    // === Khuyến mãi ===
    const promoRows = document.querySelectorAll("#promo-list .promo-item");
    const promos = [];

    promoRows.forEach(row => {
        const select = row.querySelector(".select-ticket-types"); // class thay vì id
        let selectedTickets = Array.from(select?.selectedOptions || []).map(opt => opt.value);

        // Nếu chọn "all", map ra tất cả vé hiện có
        if (selectedTickets.includes("all")) {
            selectedTickets = Array.from(document.querySelectorAll('#ticket-types .ticket_name'))
                                   .map(input => input.value.trim())
                                   .filter(name => name);
        }

        promos.push({
            code: row.querySelector(".promo_code")?.value || "",
            value: row.querySelector(".promo_value")?.value || "",
            quantity: row.querySelector(".promo_quantity")?.value || "",
            start_time: row.querySelector(".promo_start_time")?.value || "",
            end_time: row.querySelector(".promo_end_time")?.value || "",
            ticket_types: selectedTickets
        });
    });

    formData.append("promotions", JSON.stringify(promos));

    // === Debug ===
    for (let pair of formData.entries()) {
        console.log(pair[0], pair[1]);
    }

    // === Gửi dữ liệu ===
    fetch("/organizer/api/create-event", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert("Tạo sự kiện thành công!");
        } else {
            alert(data.message || "Đã có lỗi.");
        }
    })
    .catch(() => alert("Lỗi kết nối máy chủ"));
}

function toggleDropdown() {
        const dropdown = document.getElementById("accountDropdown");
        dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
    }

// Ẩn dropdown nếu bấm ra ngoài
window.onclick = function(event) {
    if (!event.target.closest('.account-wrapper')) {
        const dropdown = document.getElementById("accountDropdown");
        if (dropdown) dropdown.style.display = "none";
    }
}

document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // Bỏ active tất cả
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        // Ẩn tất cả nội dung
        document.querySelectorAll('.tab-content').forEach(content => content.style.display = 'none');

        // Active tab hiện tại
        btn.classList.add('active');
        const tabId = btn.getAttribute('data-tab');
        document.getElementById(tabId).style.display = 'block';
    });
});

let selectedEventId = null;

function showConfirmForm(eventId) {
    selectedEventId = eventId;
    document.getElementById("confirmForm").style.display = "flex";
}

function hideConfirmForm(id) {
    selectedEventId = null;
    document.getElementById(id).style.display = "none";
}

function confirmHide() {
    if (!selectedEventId) return;

    fetch(`/organizer/api/${selectedEventId}/hide`, {
        method: "POST"
    })
    .then(res => {
        if (res.ok) {
            alert("Ẩn sự kiện thành công.");
            location.reload();
        } else {
            alert("Ẩn sự kiện thất bại.");
        }
    })
    .catch(err => {
        console.error(err);
        alert("Có lỗi xảy ra khi gửi yêu cầu.");
    });

    hideConfirmForm();
}

function showEvent(eventId) {
    if (!eventId) return;

    fetch(`/organizer/api/${eventId}/show`, {
        method: "POST"
    })
    .then(res => {
        if (res.ok) {
            alert("Công khai sự kiện thành công.");
            location.reload();
        } else {
            alert("Công khai sự kiện thất bại.");
        }
    })
    .catch(err => {
        console.error(err);
        alert("Có lỗi xảy ra khi gửi yêu cầu.");
    });
}

function viewRejectionReason( eventId){
    selectedEventId = eventId;
    document.getElementById("rejectModal").style.display = "flex";

    if (!eventId) return;

    fetch(`/organizer/api/${eventId}/rejected_reason`)
        .then(response => response.json())
        .then(data => {
            console.log("Response từ server:", data);
            if (data.reason) {
                document.getElementById("rejectedReasonText").innerText = data.reason;
            } else {
                document.getElementById("rejectedReasonText").innerText = "Không tìm thấy lý do.";
            }
            document.getElementById("rejectModal").style.display = "flex";
        })
        .catch(err => {
            document.getElementById("rejectedReasonText").innerText = "Không thể tải lý do.";
            document.getElementById("rejectModal").style.display = "flex";
        });
}

function hideRejectModal() {
    selectedEventId = null;
    document.getElementById("rejectModal").style.display = "none";
}

function goToNextStepUpdate() {
    const allSections = document.querySelectorAll('.step-section');       // nội dung các bước
    const stepsProgress = document.querySelectorAll('.step-progress .step'); // thanh tiến trình
    const btnNext = document.querySelector('.btn-next');

    const currentIndex = Array.from(allSections).findIndex(el => el.classList.contains('active'));

     if (currentIndex === 0 && !validateStep1()) {
        return;
    }

    if (currentIndex ===1 && ! validateStep2()){
        return;
    }

    if (currentIndex < allSections.length - 1) {
        // Ẩn bước hiện tại
        allSections[currentIndex].classList.remove('active');

        // Hiện bước tiếp theo
        allSections[currentIndex + 1].classList.add('active');

        // Cập nhật thanh tiến trình
        stepsProgress.forEach((step, i) => {
            if (i <= currentIndex + 1) step.classList.add('active');
            else step.classList.remove('active');
        });

        // Nếu bước tiếp theo là bước cuối (bước 3) thì đổi nút thành "Lưu"
        if (currentIndex + 1 === allSections.length - 1) {
            btnNext.innerText = 'Cập nhật';
            btnNext.onclick = submitEventFormUpdate;
        } else {
            btnNext.innerText = 'Tiếp tục';
            btnNext.onclick = goToNextStepUpdate;
        }
    }
}

function submitEventFormUpdate() {

    const pathParts = window.location.pathname.split('/');
    const eventId = pathParts[pathParts.length - 1];

    const formData = new FormData();
    const imageInput = document.getElementById("imageUpload");
    const previewImage = document.getElementById("preview-img");

    if (imageInput.files.length > 0) {
        formData.append("image", imageInput.files[0]);  // ảnh mới
    } else if (previewImage && previewImage.src) {
        formData.append("existing_image_url", previewImage.src);  // giữ ảnh cũ
    }

    formData.append("name_event", document.getElementById("name_event").value);
    formData.append("event_format", document.querySelector('input[name="event_format"]:checked')?.value);
    formData.append("event_type", document.getElementById("event_type").value);
    formData.append("description", document.getElementById("description").value);
    formData.append("rules", document.getElementById("rules").value);
    formData.append("performers", document.getElementById("performers").value);
    formData.append("organizer", document.getElementById("organizer").value);
    formData.append("start_time", document.getElementById("start_time").value);
    formData.append("end_time", document.getElementById("end_time").value);

    // Format phụ thuộc hình thức
    const format = document.querySelector('input[name="event_format"]:checked')?.value;
    formData.append("event_format", format.toUpperCase());

    if (format === "OFFLINE") {
        formData.append("venue_name", document.getElementById("venue_name").value);
        formData.append("address", document.getElementById("address").value);
    } else {
        formData.append("livestream_url", document.getElementById("livestream_url").value);
    }

    // Loại vé
    const ticketRows = document.querySelectorAll("#ticket-types .ticket-type");
    const tickets = [];
    ticketRows.forEach(row => {
        tickets.push({
            name: row.querySelector(".ticket_name")?.value,
            price: row.querySelector(".ticket_price")?.value,
            quantity: row.querySelector(".ticket_quantity")?.value
        });
    });
    formData.append("tickets", JSON.stringify(tickets));

    // Gửi dữ liệu
    fetch(`/organizer/api/${eventId}/edit`, {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert("Cập nhật sự kiện thành công!");
        } else {
            alert(data.message || "Đã có lỗi.");
        }
    })
    .catch(() => alert("Lỗi kết nối máy chủ"));
}

function showConfirmDeleteForm(eventId) {
    selectedEventId = eventId;
    document.getElementById("confirmDeleteForm").style.display = "flex";
}

function confirmDelete() {
    if (!selectedEventId) return;

    console.log("Deleting event:", selectedEventId);

    fetch(`/organizer/api/${selectedEventId}/delete`, {
        method: "DELETE"
    })
    .then(res => {
        if (res.ok) {
            alert("Xóa sự kiện thành công.");
            location.reload();
        } else {
            alert("Xóa sự kiện thất bại.");
        }
    })
    .catch(err => {
        console.error(err);
        alert("Có lỗi xảy ra khi gửi yêu cầu.");
    });

    hideConfirmForm();
}

function toggleRequiresSeatCheckbox() {
    const hasSeatChecked = document.getElementById('has_seat').checked;
    // Lấy tất cả checkbox yêu cầu ghế trong step 2
    const requireSeatContainers = document.querySelectorAll('.requires-seat-container');

    requireSeatContainers.forEach(container => {
        if (hasSeatChecked) {
            container.style.display = 'flex';  // hoặc 'block' tùy style bạn muốn
            // đồng thời set required cho checkbox
            const checkbox = container.querySelector('input[type="checkbox"]');
            if (checkbox) checkbox.required = true;
        } else {
            container.style.display = 'none';
            const checkbox = container.querySelector('input[type="checkbox"]');
            if (checkbox) {
                checkbox.required = false;
                checkbox.checked = false; // reset checkbox
            }
        }
    });
}

// Lắng nghe sự kiện check/uncheck của has_seat
document.getElementById('has_seat').addEventListener('change', toggleRequiresSeatCheckbox);

document.getElementById('has_seat').addEventListener('change', function() {
    const seatSetup = document.getElementById('seat-setup-section');
    seatSetup.style.display = this.checked ? 'block' : 'none';
});

// Gọi hàm một lần khi load trang để set đúng trạng thái lúc đầu
window.addEventListener('DOMContentLoaded', () => {
    toggleRequiresSeatCheckbox();
});


const ticketSelect = document.getElementById('select-ticket-types');
let ticketChoices;

if (ticketSelect) {
    ticketChoices = new Choices(ticketSelect, {
        removeItemButton: true,
        searchPlaceholderValue: 'Tìm loại vé...',
        placeholder: true,
        placeholderValue: 'Chọn loại vé'
    });
}

function loadTicketTypesToStep3() {
    if (!ticketChoices) return; // đảm bảo instance tồn tại

    ticketChoices.clearChoices();

    let choices = [{ value: 'all', label: '-- Chọn tất cả --', selected: false }];
    const ticketInputs = document.querySelectorAll('.step-2 .ticket_name');

    ticketInputs.forEach((input, idx) => {
        const name = input.value.trim();
        if (name) {
            choices.push({ value: idx + 1, label: name, selected: false });
        }
    });

    ticketChoices.setChoices(choices, 'value', 'label', false);
}

function addPromo() {
    const promoList = document.getElementById('promo-list');
    if (!promoList) return;

    const promoDiv = document.createElement('div');
    promoDiv.classList.add('promo-item', 'form-group', 'form-row');

    promoDiv.innerHTML = `
        <h3>Mã khuyến mãi </h3>
        <div>
            <label class="required-label"><span class="text-danger">*</span> Tên khuyến mãi</label>
            <input type="text" class="promo_name" maxlength="50" placeholder="Ví dụ: Giảm giá khai trương">
        </div>
        <div>
            <label class="required-label"><span class="text-danger">*</span> Mã code</label>
            <input type="text" class="promo_code" maxlength="20" placeholder="VD: KHAITRUONG20">
        </div>
        <div>
            <label class="required-label"><span class="text-danger">*</span> Giá trị giảm (% hoặc VNĐ)</label>
            <input type="text" class="promo_value" placeholder="VD: 20% hoặc 50000">
        </div>
        <div>
            <label class="required-label"><span class="text-danger">*</span> Số lượng áp dụng</label>
            <input type="number" class="promo_quantity" min="1" placeholder="VD: 100">
        </div>
        <div>
            <label class="required-label"><span class="text-danger">*</span> Ngày bắt đầu</label>
            <input type="datetime-local" class="promo_start_time" required>
        </div>
        <div>
            <label class="required-label"><span class="text-danger">*</span> Ngày kết thúc</label>
            <input type="datetime-local" class="promo_end_time" required>
        </div>
        <div>
            <label class="required-label"><span class="text-danger">*</span> Áp dụng cho loại vé</label>
            <select class="select-ticket-types" multiple></select>
        </div>
        <div>
            <button type="button" class="btn btn-danger remove-ticket">X</button>
        </div>
    `;

    promoList.appendChild(promoDiv);

    // Nút xóa promo
    promoDiv.querySelector('.remove-ticket').addEventListener('click', () => {
        promoDiv.remove();
    });

    // Khởi tạo select Choices.js cho select mới
    const select = promoDiv.querySelector('.select-ticket-types');
    if (select) {
        // Thêm option "Chọn tất cả"
        const allOption = document.createElement('option');
        allOption.value = 'all';
        allOption.textContent = '-- Chọn tất cả --';
        select.appendChild(allOption);

        // Nạp danh sách vé từ step 2
        document.querySelectorAll('#ticket-types .ticket-type').forEach(ticketRow => {
            const ticketName = ticketRow.querySelector('.ticket_name').value.trim();
            if (ticketName) {
                const option = document.createElement('option');
                option.value = ticketName;
                option.textContent = ticketName;
                select.appendChild(option);
            }
        });

        // Khởi tạo Choices riêng cho select động
        new Choices(select, {
            removeItemButton: true,
            placeholderValue: 'Chọn loại vé',
            searchPlaceholderValue: 'Tìm vé...'
        });
    }
}





