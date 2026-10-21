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
  const apiProviderSelect = document.getElementById('api-provider-select');
  const apiKeyHelp = document.getElementById('api-key-help');
  const openaiSettings = document.getElementById('openai-settings');
  const apiBaseUrlInput = document.getElementById('api-base-url');
  const apiModelInput = document.getElementById('api-model');
  const saveKeyBtn = document.getElementById('save-key-btn');
  const keyStatusMsg = document.getElementById('key-status-msg');

  const BASE_URL = 'http://127.0.0.1:8124';
  let maxCharLimit = 200;
  let loadingText = 'Framing Prompt... Please Wait...';

  const providerPresets = {
    gemini: { baseUrl: '', model: 'gemini-3.8-flash', help: 'Paste a Gemini API key from Google AI Studio. OAuth access tokens are not supported.' },
    openai: { baseUrl: 'https://api.openai.com/v1', model: 'gpt-4o-mini', help: 'Paste an OpenAI API key.' },
    anthropic: { baseUrl: 'https://api.anthropic.com/v1', model: 'claude-sonnet-4-20250514', help: 'Paste an Anthropic API key.' },
    openrouter: { baseUrl: 'https://openrouter.ai/api/v1', model: 'openai/gpt-4o-mini', help: 'Paste an OpenRouter API key.' },
    groq: { baseUrl: 'https://api.groq.com/openai/v1', model: 'llama-3.3-70b-versatile', help: 'Paste a Groq API key.' },
    mistral: { baseUrl: 'https://api.mistral.ai/v1', model: 'mistral-small-latest', help: 'Paste a Mistral API key.' },
    deepseek: { baseUrl: 'https://api.deepseek.com/v1', model: 'deepseek-chat', help: 'Paste a DeepSeek API key.' },
    xai: { baseUrl: 'https://api.x.ai/v1', model: 'grok-3-mini', help: 'Paste an xAI API key.' },
    ollama: { baseUrl: 'http://localhost:11434/v1', model: 'llama3.2', help: 'Ollama runs locally and usually does not require a real API key.' },
    lmstudio: { baseUrl: 'http://localhost:1234/v1', model: 'local-model', help: 'LM Studio runs locally. Use any key value accepted by your local server.' },
    'openai-compatible': { baseUrl: 'https://api.openai.com/v1', model: 'gpt-4o-mini', help: 'Paste an API key for an OpenAI-compatible service.' }
  };

  const updateProviderFields = () => {
    const provider = apiProviderSelect.value;
    const preset = providerPresets[provider] || providerPresets.gemini;
    const requiresSettings = provider !== 'gemini';
    openaiSettings.hidden = !requiresSettings;
    apiKeyHelp.textContent = preset.help;
    apiKeyInput.placeholder = provider === 'gemini' ? 'Paste your Google AI Studio API key' : 'Paste your provider API key';
    if (requiresSettings && !apiBaseUrlInput.value) apiBaseUrlInput.value = preset.baseUrl;
    if (requiresSettings && !apiModelInput.value) apiModelInput.value = preset.model;
  };

  apiProviderSelect.addEventListener('change', () => {
    const preset = providerPresets[apiProviderSelect.value] || providerPresets.gemini;
    apiBaseUrlInput.value = preset.baseUrl;
    apiModelInput.value = preset.model;
    updateProviderFields();
  });
  updateProviderFields();

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

      if (keyData.provider) {
        apiProviderSelect.value = keyData.provider;
        const preset = providerPresets[keyData.provider] || providerPresets.gemini;
        apiBaseUrlInput.value = keyData.base_url || preset.baseUrl;
        apiModelInput.value = keyData.model || preset.model;
        updateProviderFields();
      }

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
    const provider = apiProviderSelect.value;
    const isLocalProvider = provider === 'ollama' || provider === 'lmstudio';
    if (!customKey && !isLocalProvider) {
       return alert('⚠️ Input Error: Please paste an API key first.');
    }

    const baseUrl = apiBaseUrlInput.value.trim();
    const model = apiModelInput.value.trim();
    if (provider !== 'gemini' && (!baseUrl || !model)) {
      return alert('⚠️ Input Error: Enter an API base URL and model name.');
    }

    try {
      const response = await fetch(`${BASE_URL}/save-key`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: customKey, provider, base_url: baseUrl, model })
      });

      if (response.ok) {
         alert('✨ Success: API provider configuration saved locally.');
        window.location.reload();
      } else {
        const data = await response.json().catch(() => ({}));
         alert(data.message || '❌ The API key was rejected.');
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
