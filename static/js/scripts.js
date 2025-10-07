const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const fileButton = document.getElementById("fileButton");
const videoPreview = document.getElementById("videoPreview");
const summarizeButton = document.getElementById("summarizeButton");

let audio_path, transcription, summary = null;

// Open file dialog
fileButton.addEventListener("click", () => fileInput.click());

// File input change
fileInput.addEventListener("change", (e) => handleFile(e.target.files[0]));

// Drag & drop
let dragEnabled = true;

dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    if (!dragEnabled) return;

    dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));

dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    if (!dragEnabled) return;

    dropZone.classList.remove("dragover");
    if (e.dataTransfer.files.length) {
        handleFile(e.dataTransfer.files[0]);
    }
});

// Handles video attachment
function handleFile(file) {
    if (file && file.type.startsWith("video/")) {
        const url = URL.createObjectURL(file);

        videoPreview.src = url;
        videoPreview.style.display = "block";

        showState("loadingState");

        const fileName = trimFileName(file.name)
        document.getElementById("uploadFileName").textContent = fileName;

        dragEnabled = false;

        uploadVideo(file);
    } else {
        alert("Please upload a valid video file.");
    }
}

// Uploads video
function uploadVideo(file) {
    const formData = new FormData();
    formData.append("video", file);

    showState("loadingState")

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log(".mp3 saved at: ", data.mp3_path);
        audio_path = data.mp3_path;
        showState("resultsState")
        console.log("Upload result:", data);
    })
    .catch(err => console.error("Upload failed: ", err));
}

// Trims file name if too long
function trimFileName(fileName, maxLength = 60) {
  const dotIndex = fileName.lastIndexOf('.');
  const name = dotIndex !== -1 ? fileName.slice(0, dotIndex) : fileName;
  const extension = dotIndex !== -1 ? fileName.slice(dotIndex) : '';

  if (fileName.length <= maxLength) {
    return fileName;
  }

  const allowedNameLength = maxLength - (extension.length + 3);

  const trimmedName = name.slice(0, allowedNameLength);

  return `${trimmedName}...${extension}`;
}

// Hides and shows content
function showState(stateId) {
    document.querySelectorAll(".dashed-container > div").forEach(div => {
        div.style.display = "none";
    });

    if (stateId == "resultsState") {
        style = "block";
    } else {
        style = "contents";
    }

    document.getElementById(stateId).style.display = style;
}

// Change text for loading spinner
function changeLoadingText(text) {
    document.getElementById("loadingText").innerText = text;
}

// Markdown to HTML
function displaySummary(markdownText) {
    const markdown = document.getElementById("markdownText");
    const html = marked.parse(markdownText);

    markdown.innerHTML = html;
}

// Handles transcription & summarization
summarizeButton.addEventListener("click", () => handleSummarization());

function handleSummarization() {
    showState("loadingState")
    changeLoadingText("Transcribing audio")

    fetch("/transcribe", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ audio_path: audio_path })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Transcription result:", data);
        changeLoadingText("Summarizing into notes")
        transcription = data.transcript;
        document.getElementById("transcriptionText").innerText = transcription;

        return fetch("/summarize", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ text: data.transcript })
        });
    })
    .then(response => response.json())
    .then(summaryData => {
        console.log("Summary result:", summaryData);
        showState("downloadState");
        summary = summaryData.summary;
        document.getElementById("summaryText").innerText = summary;
        displaySummary(summaryData.summary);
    })
    .catch(err => {
        console.error("Transcription or summarization failed: ", err);
    });
}

// Copies text to clipboard
const copyTranscriptionButton = document.getElementById("copyTranscription");
const copySummaryButton = document.getElementById("copySummary");

copyTranscriptionButton.addEventListener("click", (e) => copyText("transcriptionText"));
copySummaryButton.addEventListener("click", (e) => copyText("summaryText"));

function copyText(id) {
    const text = document.getElementById(id).innerText;
    navigator.clipboard.writeText(text).then(() => {
        alert("Copied to clipboard!");
    }).catch(err => {
        console.error("Failed to copy: ", err);
    });
}

// Downloads PDF
const downloadPDFButton = document.getElementById("downloadButton");
downloadPDFButton.addEventListener("click", (e) => downloadPDF());

function downloadPDF() {
const { jsPDF } = window.jspdf;
    const pdf = new jsPDF();

    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(16);
    pdf.text("Transcription", 10, 20);

    pdf.setFont("helvetica", "normal");
    pdf.setFontSize(12);
    pdf.text(transcription, 10, 30, { maxWidth: 180 });

    pdf.addPage();
    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(16);
    pdf.text("Summary", 10, 20);

    pdf.setFont("helvetica", "normal");
    pdf.setFontSize(12);
    pdf.text(summary, 10, 30, { maxWidth: 180 });

    pdf.save("export.pdf");
}

// Update year
const currentYear = new Date().getFullYear();
document.getElementById("year").innerText = currentYear;