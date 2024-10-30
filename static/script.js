document.getElementById("download-btn").addEventListener("click", async () => {
    const url = document.getElementById("video-url").value;
    const quality = document.getElementById("quality").value;
    const downloadType = document.getElementById("download-type").value;
    const message = document.getElementById("message");
    const loadingSpinner = document.getElementById("loading-spinner");
    const downloadLink = document.getElementById("download-link");

    // Reset the message and show the loading spinner
    message.textContent = "";
    loadingSpinner.style.display = "block";
    downloadLink.style.display = "none"; // Hide the link initially

    try {
        const response = await fetch("/download", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url, quality, download_type: downloadType })
        });

        const result = await response.json();

        // Hide the loading spinner after the request is complete
        loadingSpinner.style.display = "none";

        // Display the success message
        message.textContent = result.message;

        // Show the link to view/download the file
        if (result.file_path) {
            downloadLink.href = `/downloads/${result.file_path}`; // Set the link URL
            downloadLink.style.display = "inline"; // Show the link
        }
    } catch (error) {
        loadingSpinner.style.display = "none"; // Hide the spinner if there's an error
        message.textContent = "Error downloading video. Please try again.";
    }
});
