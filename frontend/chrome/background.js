// Send a toggle message to the active tab when the extension icon is clicked
chrome.action.onClicked.addListener((tab) => {
	try {
		chrome.tabs.sendMessage(tab.id, { type: 'toggle-closetx' });
	} catch (e) {
		// Tab may not have the content script yet; ignore
		console.warn('Could not send toggle message to tab', e);
	}
});