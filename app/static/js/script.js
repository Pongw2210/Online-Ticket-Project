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
    const currentStep = document.querySelector('.step-section.active');
    const nextStep = currentStep.nextElementSibling;

    if (nextStep && nextStep.classList.contains('step-section')) {
        // Ẩn bước hiện tại
        currentStep.classList.remove('active');

        // Hiện bước tiếp theo
        nextStep.classList.add('active');

        // Cập nhật thanh tiến trình
        const steps = document.querySelectorAll('.step-progress .step');
        const allSections = document.querySelectorAll('.step-section');
        const stepIndex = Array.from(allSections).indexOf(nextStep);

        steps.forEach((step, i) => {
            if (i <= stepIndex) step.classList.add('active');
            else step.classList.remove('active');
        });
    }
}

function goToPrevStep() {
    const currentStep = document.querySelector('.step-section.active');
    const prevStep = currentStep.previousElementSibling;
    if (prevStep && prevStep.classList.contains('step-section')) {
        currentStep.classList.remove('active');
        prevStep.classList.add('active');

        const steps = document.querySelectorAll('.step-progress .step');
        const stepIndex = Array.from(document.querySelectorAll('.step-section')).indexOf(prevStep);
        steps.forEach((step, i) => {
            if (i <= stepIndex) step.classList.add('active');
            else step.classList.remove('active');
        });
    }
}


