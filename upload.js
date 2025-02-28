document.addEventListener("DOMContentLoaded", function () {
    const fileUpload = document.getElementById("fileupload");
    const jobDesc = document.getElementById("job_desc");
    const form = document.getElementById("mainform");
    const submitButton = form.querySelector("button[type='submit']");
    const resultContainer = document.getElementById("mb2");

    // Allowed file types
    const allowedExtensions = ["pdf", "docx", "doc", "png", "jpg", "jpeg"];

    // File validation
    fileUpload.addEventListener("change", function () {
        const file = fileUpload.files[0];
        if (file) {
            const fileName = file.name;
            const fileSize = file.size / 1024 / 1024; // Convert to MB
            const fileExtension = fileName.split(".").pop().toLowerCase();

            if (!allowedExtensions.includes(fileExtension)) {
                alert("Invalid file type! Please upload a PDF, DOCX, DOC, PNG, JPG, or JPEG file.");
                fileUpload.value = ""; // Reset input
                return;
            }

            if (fileSize > 5) {
                alert("File size too large! Please upload a file smaller than 5MB.");
                fileUpload.value = "";
                return;
            }

            console.log("File selected:", fileName);
        }
    });

    // Handle form submission
    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const file = fileUpload.files[0];
        const jobDescValue = jobDesc.value.trim();

        if (!file) {
            alert("Please upload a resume.");
            return;
        }

        if (!jobDescValue) {
            alert("Please enter a job description.");
            return;
        }

        // Prepare FormData
        const formData = new FormData();
        formData.append("file", file);
        formData.append("job_desc", jobDescValue);

        // Disable button while uploading
        submitButton.disabled = true;
        submitButton.textContent = "Uploading...";

        // Send the file via AJAX
        fetch("/selection", {
            method: "POST",
            body: formData
        })
        .then(response => response.text())
        .then(data => {
            resultContainer.innerHTML = data;
            submitButton.disabled = false;
            submitButton.textContent = "Submit";
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Something went wrong! Please try again.");
            submitButton.disabled = false;
            submitButton.textContent = "Submit";
        });
    });
});
