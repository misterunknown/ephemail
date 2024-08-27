const email_address = document.getElementById("email_address")
const copyButton = document.getElementById("copy_button")
const copyButtonFeedback = document.getElementById("copy_button_feedback")

const escapeHtml = (unsafe) => {
	return unsafe
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;")
		.replace(/'/g, "&#039;");
}

const messageController = (e) => {
	var data = JSON.parse(e.data);
	console.log(data);
	if (data.email_address)
		document.getElementById("email_address").innerText = data.email_address;
	else if (data.email) {
		newmail = document.createElement("template");
		newmail.innerHTML = '<pre><code>'+escapeHtml(data.email)+'</code></pre>';
		document.getElementById("emails").prepend(newmail.content.firstChild);
	}
}

const websocket = new WebSocket(`ws://${window.location.host}`);
websocket.onmessage = messageController;

copyButton.addEventListener('click', (e) => {
	copyTextToClipboard(email_address.innerText)
	copyButtonFeedback.textContent = '\u2714\uFE0F'
	setTimeout(() => { copyButtonFeedback.textContent = '' }, 1000)
})


//// fucking copy&paste

function fallbackCopyTextToClipboard(text) {
  var textArea = document.createElement("textarea");
  textArea.value = text;
  
  // Avoid scrolling to bottom
  textArea.style.top = "0";
  textArea.style.left = "0";
  textArea.style.position = "fixed";

  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();

  try {
    var successful = document.execCommand('copy');
    var msg = successful ? 'successful' : 'unsuccessful';
    console.log('Fallback: Copying text command was ' + msg);
  } catch (err) {
    console.error('Fallback: Oops, unable to copy', err);
  }

  document.body.removeChild(textArea);
}
function copyTextToClipboard(text) {
  if (!navigator.clipboard) {
    fallbackCopyTextToClipboard(text);
    return;
  }
  navigator.clipboard.writeText(text).then(function() {
    console.log('Async: Copying to clipboard was successful!');
  }, function(err) {
    console.error('Async: Could not copy text: ', err);
  });
}
