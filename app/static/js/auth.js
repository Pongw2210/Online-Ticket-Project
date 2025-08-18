document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("avatar");
    const saveBtn = document.getElementById("saveAvatarBtn");
    const preview = document.getElementById("avatarPreview");

    let selectedFile = null;

    // Xem trước ảnh
    fileInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file) {
            selectedFile = file;
            const reader = new FileReader();
            reader.onload = (ev) => {
                preview.src = ev.target.result;
            };
            reader.readAsDataURL(file);
            saveBtn.disabled = false; // bật lại nút lưu
        }
    });

    // Upload avatar
    saveBtn.addEventListener("click", function () {
        if (!selectedFile) {
            alert("Vui lòng chọn ảnh trước!");
            return;
        }

        saveBtn.disabled = true; // tạm khóa nút khi upload

        const formData = new FormData();
        formData.append("avatar", selectedFile);

        fetch("/upload_avatar", {
            method: "POST",
            body: formData,
        })
            .then(res => {
                const contentType = res.headers.get("content-type") || "";
                if (contentType.includes("application/json")) {
                    return res.json();
                }
                return res.text().then(txt => {
                    console.error("Non-JSON response:", txt);
                    return { status: "error", message: "Server trả về dữ liệu không hợp lệ" };
                });
            })
            .then(data => {
                if (data.status === "success") {
                    preview.src = data.avatar_url;
                    alert("Cập nhật avatar thành công!");
                    fileInput.value = "";   // reset input
                    selectedFile = null;
                } else {
                    alert(data.message || "Có lỗi xảy ra!");
                }
            })
            .catch(err => {
                console.error("Lỗi upload:", err);
                alert("Lỗi kết nối server!");
            })
            .finally(() => {
                saveBtn.disabled = false; // bật lại nút cho lần sau
            });
    });
});
