async function processVideo() {
  let url = document.getElementById("url").value;

  let res = await fetch("http://127.0.0.1:5000/process", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({url})
  });

  let data = await res.json();

  let div = document.getElementById("formats");
  div.innerHTML = "";

  data.formats.forEach(f => {
    div.innerHTML += `
      <p>${f.format} 
      <button onclick="download('${f.id}','${url}')">Download</button></p>
    `;
  });
}

function download(id, url) {
  window.open(`http://127.0.0.1:5000/download?url=${url}&format=${id}`);
}