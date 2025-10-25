const params = new URLSearchParams(location.search);
const app = params.get('app') || 'site';
const perm = params.get('perm') || 'permission';
const risk = params.get('risk') || 'unknown';
document.getElementById('msg').innerText = `${app} requests ${perm}. Risk score: ${risk}. Allow?`;

document.getElementById('allow').addEventListener('click', () => {
  chrome.runtime.sendMessage({ type: 'confirm_response', value: true });
});
document.getElementById('block').addEventListener('click', () => {
  chrome.runtime.sendMessage({ type: 'confirm_response', value: false });
});
