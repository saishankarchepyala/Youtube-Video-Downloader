async function downloadVideo() {
  const url = document.getElementById('videoUrl').value.trim();
  const quality = document.getElementById('quality').value;
  const type = document.getElementById('downloadType').value;
  const status = document.getElementById('status');

  if (!url) {
    alert('Please enter a YouTube video URL.');
    return;
  }

  status.style.color = 'black';
  status.textContent = 'Download started. Please wait...';

  try {
    const response = await fetch('http://localhost:8000/download', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({url, quality, type})
    });
    const data = await response.json();

    if (data.status === 'success') {
      status.style.color = 'green';
      status.textContent = `Download completed! Saved as: "${data.title}" in your Downloads folder.`;
    } else {
      status.style.color = 'red';
      status.textContent = `Error: ${data.message}`;
    }
  } catch (error) {
    status.style.color = 'red';
    status.textContent = 'Network error: ' + error.message;
  }
}
