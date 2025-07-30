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

function goToNextStep() {
    const allSteps = document.querySelectorAll('.step-section');
    const currentIndex = Array.from(allSteps).findIndex(el => el.classList.contains('active'));

    if (currentIndex < allSteps.length - 1) {
        allSteps[currentIndex].classList.remove('active');
        allSteps[currentIndex + 1].classList.add('active');

        const stepsProgress = document.querySelectorAll('.step-progress .step');
        stepsProgress.forEach((step, i) => {
            if (i <= currentIndex + 1) step.classList.add('active');
            else step.classList.remove('active');
        });
    }
}

function goToPrevStep() {
    const allSteps = document.querySelectorAll('.step-section');
    const currentIndex = Array.from(allSteps).findIndex(el => el.classList.contains('active'));

    if (currentIndex > 0) {
        allSteps[currentIndex].classList.remove('active');
        allSteps[currentIndex - 1].classList.add('active');

        const stepsProgress = document.querySelectorAll('.step-progress .step');
        stepsProgress.forEach((step, i) => {
            if (i <= currentIndex - 1) step.classList.add('active');
            else step.classList.remove('active');
        });
    }
}

function addTicketType() {
    const container = document.getElementById("ticket-types");

    // Tạo một div mới cho loại vé
    const newTicket = document.createElement("div");
    newTicket.classList.add("ticket-type", "form-group", "form-row");

    newTicket.innerHTML = `
        <div>
            <label class="required-label"><span class="text-danger">*</span> Tên vé</label>
            <input type="text" name="ticket_name[]" placeholder="Ví dụ: Vé thường">
        </div>
        <div>
            <label class="required-label"><span class="text-danger">*</span> Giá vé(VNĐ)</label>
            <input type="number" name="ticket_price[]" min="0" placeholder="100000">
        </div>
        <div>
           <label class="required-label"><span class="text-danger">*</span> Số lượng</label>
            <input type="number" name="ticket_quantity[]" min="1" placeholder="50">
        </div>
        <div>
            <button type="button" class="btn btn-danger remove-ticket" onclick="this.parentElement.parentElement.remove()">X</button>
        </div>
    `;

    container.appendChild(newTicket);
}


