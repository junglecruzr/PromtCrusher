document.addEventListener('DOMContentLoaded', async () => {
  const baseUrl = 'http://127.0.0.1:8124';
  const mode = document.getElementById('prompt-mode');
  const blueprintPanel = document.getElementById('iterative-panel');
  const taskPanel = document.getElementById('iterative-task-panel');
  const framework = document.getElementById('framework');
  const subject = document.getElementById('subject');
  const generate = document.getElementById('generate-btn');
  const output = document.getElementById('output-display');
  const outputBox = document.getElementById('output-container');

  const list = id => document.getElementById(id).value.split('\n').map(value => value.trim()).filter(Boolean);
  const setList = (id, values) => { document.getElementById(id).value = (values || []).join('\n'); };
  const updateMode = () => {
    const iterative = mode.value === 'iterative';
    blueprintPanel.hidden = !iterative;
    taskPanel.hidden = !iterative;
    framework.disabled = iterative;
    subject.disabled = iterative;
  };
  mode.addEventListener('change', updateMode);
  updateMode();

  try {
    const response = await fetch(`${baseUrl}/blueprint`);
    if (response.ok) {
      const blueprint = await response.json();
      document.getElementById('project-name').value = blueprint.name || '';
      document.getElementById('project-summary').value = blueprint.summary || '';
      setList('project-stack', blueprint.stack);
      setList('project-modules', blueprint.modules);
      setList('project-phases', blueprint.phases);
      setList('project-constraints', blueprint.constraints);
    }
  } catch (error) {
    console.warn('Blueprint load failed', error);
  }

  document.getElementById('save-blueprint-btn').addEventListener('click', async () => {
    const blueprint = {
      name: document.getElementById('project-name').value.trim(),
      summary: document.getElementById('project-summary').value.trim(),
      stack: list('project-stack'), modules: list('project-modules'),
      phases: list('project-phases'), constraints: list('project-constraints')
    };
    const response = await fetch(`${baseUrl}/blueprint`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(blueprint)
    });
    const data = await response.json();
    alert(data.status === 'success' ? '✨ Blueprint saved locally.' : (data.message || '❌ Blueprint save failed.'));
  });

  generate.addEventListener('click', async event => {
    if (mode.value !== 'iterative') return;
    event.preventDefault();
    event.stopImmediatePropagation();
    const task = {
      phase: document.getElementById('task-phase').value.trim(),
      title: document.getElementById('task-title').value.trim(),
      description: document.getElementById('task-description').value.trim(),
      target_files: list('task-files'), acceptance_criteria: list('task-criteria')
    };
    if (!task.title || !task.description) return alert('⚠️ Enter a task title and description.');
    generate.disabled = true;
    try {
      const response = await fetch(`${baseUrl}/iterative`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(task)
      });
      const data = await response.json();
      if (data.status === 'success') {
        output.textContent = data.prompt; outputBox.style.display = 'block';
        outputBox.scrollIntoView({ behavior: 'smooth' });
      } else alert(data.message || '❌ Iterative prompt generation failed.');
    } catch (error) {
      alert('❌ Server Connection Error.');
    } finally {
      generate.disabled = false;
    }
  }, true);
});
