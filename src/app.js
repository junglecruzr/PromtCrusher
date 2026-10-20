document.addEventListener('DOMContentLoaded', async () => {
  const generateBtn = document.getElementById('generate-btn');
  const frameworkSelect = document.getElementById('framework');
  const subjectInput = document.getElementById('subject');
  const outputContainer = document.getElementById('output-container');
  const outputDisplay = document.getElementById('output-display');
  const copyBtn = document.getElementById('copy-btn');
  const enhanceBtn = document.getElementById('enhance-btn');
  const enhancementInput = document.getElementById('enhancement-input');
  const apiKeyInput = document.getElementById('api-key-input');
  const saveKeyBtn = document.getElementById('save-key-btn');
  const keyStatusMsg = document.getElementById('key-status-msg');

  const BASE_URL = 'http://127.0.0.1:8124';
  let maxCharLimit = 200;
  let loadingText = 'Crushing Prompt Matrix... Please Wait...';

  try {
    const configRes = await fetch(`${BASE_URL}/ui-config.json`);
    if (configRes.ok) {
      const config = await configRes.json();
      maxCharLimit = config.security_limits?.subject_max_length || 200;
      loadingText = config.ui_strings?.btn_text_loading || loadingText;
      subjectInput.maxLength = maxCharLimit;
    }

    const keyCheckRes = await fetch(`${BASE_URL}/check-key`);
    if (keyCheckRes.ok) {
      const keyData = await keyCheckRes.json();
      keyStatusMsg.textContent = keyData.message || '⚡ No API key loaded.';
      keyStatusMsg.style.display = 'block';

      if (keyData.custom_active) {
        keyStatusMsg.style.color = '#22c55e';
        apiKeyInput.placeholder = '••••••••••••••••••••••••••••••••';
      } else if (keyData.mode === 'evaluation') {
        keyStatusMsg.style.color = '#f59e0b';
      } else {
        keyStatusMsg.style.color = '#ef4444';
      }
    }
  } catch (err) {
    console.warn(err);
  }

  saveKeyBtn.addEventListener('click', async () => {
    const customKey = apiKeyInput.value.trim();
    if (!customKey) {
       return alert('⚠️ Input Error: Please paste a Gemini API key from Google AI Studio.');
    }

    try {
      const response = await fetch(`${BASE_URL}/save-key`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: customKey })
      });

      if (response.ok) {
        alert('✨ Success: Custom Gemini API key configuration saved locally.');
        window.location.reload();
      } else {
        const data = await response.json().catch(() => ({}));
        alert(data.message || '❌ The Gemini API key was rejected.');
      }
    } catch (err) {
      alert('❌ Profile Generation Failure.');
    }
  });

  generateBtn.addEventListener('click', async () => {
    const subject = subjectInput.value.trim();
    const framework = frameworkSelect.value;

    if (!subject) {
      return alert('⚠️ Input Required.');
    }

    if (subject.length > maxCharLimit) {
      return alert('⚠️ Input Too Long.');
    }

    generateBtn.disabled = true;
    const originalBtnText = generateBtn.textContent;
    generateBtn.textContent = loadingText;

    try {
      const response = await fetch(`${BASE_URL}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject, framework })
      });

      if (!response.ok) {
        return alert(`❌ Error Code: ${response.status}`);
      }

      const data = await response.json();
      if (data.status === 'success') {
        outputDisplay.textContent = data.prompt;
        outputContainer.style.display = 'block';
        outputContainer.scrollIntoView({ behavior: 'smooth' });
      } else {
        alert(data.message);
      }
    } catch (error) {
      alert('❌ Server Connection Error.');
    } finally {
      generateBtn.disabled = false;
      generateBtn.textContent = originalBtnText;
    }
  });

  enhanceBtn.addEventListener('click', async () => {
    const existingPrompt = outputDisplay.textContent.trim();
    if (!existingPrompt) {
      return alert('⚠️ Generate a Super Prompt before enhancing it.');
    }

    enhanceBtn.disabled = true;
    const originalBtnText = enhanceBtn.textContent;
    enhanceBtn.textContent = 'Enhancing Super Prompt...';

    try {
      const response = await fetch(`${BASE_URL}/enhance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: existingPrompt,
          framework: frameworkSelect.value,
          instructions: enhancementInput.value.trim()
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        outputDisplay.textContent = data.prompt;
        outputContainer.scrollIntoView({ behavior: 'smooth' });
      } else {
        alert(data.message || '❌ Enhancement failed.');
      }
    } catch (error) {
      alert('❌ Server Connection Error.');
    } finally {
      enhanceBtn.disabled = false;
      enhanceBtn.textContent = originalBtnText;
    }
  });

  copyBtn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(outputDisplay.textContent);
      const originalCopyText = copyBtn.textContent;
      copyBtn.textContent = 'Copied!';
      copyBtn.style.background = '#22c55e';
      setTimeout(() => {
        copyBtn.textContent = originalCopyText;
        copyBtn.style.background = '';
      }, 2000);
    } catch (err) {
      alert('Failed to copy prompt.');
    }
  });

  window.addEventListener('beforeunload', () => {
    if (navigator.sendBeacon) {
      navigator.sendBeacon(`${BASE_URL}/shutdown`);
    } else {
      fetch(`${BASE_URL}/shutdown`, { method: 'GET', keepalive: true });
    }
  });
});
